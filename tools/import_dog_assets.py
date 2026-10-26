"""Compile approved high-density dog pose sheets into deterministic anchored clips."""
from pathlib import Path
import json
import hashlib
import sys
import pygame

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from pvz_game.presentation.animation import (assign_clip_durations,
    JALAPENO_IGNITE_DURATION_TICKS)
OUT=ROOT/'assets/skins/dogs'
CELL=256
COLS=8


def load_grid(filename,rows=(0,1,2,3),actor_scale=1.0):
    sheet=pygame.image.load(str(OUT/'source'/filename))
    if sheet.get_size()!=(1536,1024):
        raise ValueError(f'{filename} must be an exact 6x4 grid of 256-pixel cells')
    result=[]
    for row in rows:
        for col in range(6):
            cell=sheet.subsurface((col*256,row*256,256,256)).copy()
            components=pygame.mask.from_surface(cell,32).connected_components(200)
            largest=max((component.count() for component in components),default=0)
            keep=pygame.Surface(cell.get_size(),pygame.SRCALPHA)
            for component in components:
                if component.count()==largest:
                    silhouette=component.to_surface(setcolor=(255,255,255,255),unsetcolor=(0,0,0,0))
                    keep.blit(silhouette,(0,0))
            cell.blit(keep,(0,0),special_flags=pygame.BLEND_RGBA_MULT)
            bounds=cell.get_bounding_rect(min_alpha=32)
            canvas=pygame.Surface((CELL,CELL),pygame.SRCALPHA)
            if bounds.w and bounds.h:
                crop=cell.subsurface(bounds).copy()
                # Target a stable 2x sprite footprint. Wide poses are gently
                # compressed horizontally so actors stay within neighboring cells.
                size=(min(145,max(1,round(bounds.w*220/bounds.h))),220)
                crop=pygame.transform.smoothscale(crop,size)
                canvas.blit(crop,((CELL-size[0])//2,CELL-24-size[1]))
            result.append(canvas)
    return result


def variants(images,loop=True,steps=4):
    """Keep key poses and build distinct intermediate image samples."""
    result=[]
    pairs=len(images) if loop else len(images)-1
    for i,image in enumerate(images):
        result.append(image)
        if i<pairs:
            nxt=images[(i+1)%len(images)]
            for part in range(1,steps):
                blended=image.copy()
                overlay=nxt.copy()
                overlay.set_alpha(round(255*part/steps))
                blended.blit(overlay,(0,0))
                result.append(blended)
    return result


def user_sheet(filename):
    """Read the user's transparent 10x6 sheet without discarding source poses."""
    path=OUT/'source'/filename
    sheet=pygame.image.load(str(path))
    width,height=sheet.get_size()
    if width<1000 or height<600 or abs(width/10-height/6)>1:
        raise ValueError(f'{filename} must be a 10x6 sheet of 60 frames')
    frames=[]
    for row in range(6):
        for col in range(10):
            step_x=width/10;step_y=height/6
            # These sheets have no gutters and some poses cross their nominal
            # tile edge. Overlap the crop slightly, then isolate the actor.
            x0=max(0,round((col-.22)*step_x));x1=min(width,round((col+1+.22)*step_x))
            y0=max(0,round((row-.08)*step_y));y1=min(height,round((row+1+.08)*step_y))
            cell=sheet.subsurface((x0,y0,x1-x0,y1-y0)).copy()
            # Alpha-threshold connected components remove isolated export specks,
            # while keeping detached flame shapes when they form a real cluster.
            mask=pygame.mask.from_surface(cell,96)
            components=mask.connected_components(80)
            largest_component=max(components,key=lambda item:item.count(),default=None)
            keep=pygame.Surface(cell.get_size(),pygame.SRCALPHA)
            if largest_component is not None:
                keep.blit(largest_component.to_surface(setcolor=(255,255,255,255),unsetcolor=(0,0,0,0)),(0,0))
            cell.blit(keep,(0,0),special_flags=pygame.BLEND_RGBA_MULT)
            bounds=cell.get_bounding_rect(min_alpha=24)
            if bounds.w==0 or bounds.h==0:
                raise ValueError(f'{filename} contains an empty source frame {row*10+col}')
            canvas=pygame.Surface((CELL,CELL),pygame.SRCALPHA)
            if bounds.w and bounds.h:
                crop=cell.subsurface(bounds).copy()
                scale=min(214/bounds.h,145/bounds.w)
                size=(max(1,round(bounds.w*scale)),max(1,round(bounds.h*scale)))
                crop=pygame.transform.smoothscale(crop,size)
                canvas.blit(crop,((CELL-size[0])//2,232-size[1]))
            frames.append(canvas)
    if len(frames)!=60 or len({pygame.image.tobytes(f,'RGBA') for f in frames})!=60:
        raise ValueError(f'{filename} must contain 60 distinct source poses')
    return frames,path


def interpolate_source_frames(images,source_indices,steps,loop=False):
    """Add in-between samples while retaining references to every authored pose."""
    result=[]
    # Do not cross-fade the cycle boundary: blending a resting pose with a
    # dissimilar first pose creates a visible double-image at the loop seam.
    pairs=len(source_indices)-1
    for position,index in enumerate(source_indices):
        result.append((images[index],[index]))
        if position>=pairs:continue
        next_index=source_indices[(position+1)%len(source_indices)]
        first,second=images[index],images[next_index]
        for part in range(1,steps):
            blend=first.copy()
            overlay=second.copy();overlay.set_alpha(round(255*part/steps))
            blend.blit(overlay,(0,0))
            result.append((blend,[index,next_index]))
    return result


def main():
    choices=[
      ('sunflower','beiwo-sheet-hd.png','被窝 · 金围巾','idle','produce',1.30),
      ('peashooter','huanghuang-sheet.png','黄黄 · 豌豆射手','idle','attack',1.05),
      ('zombie_basic','aoao-red-sheet-hd.png','嗷嗷嗷 · 红背心','walk','bite',1.60),
    ]
    cells=[];roles={};records=[]
    def pack(image,duration=2,anchors=(128,232),muzzle=(185,122),contact=(70,150),source_frames=None):
        idx=len(cells);cells.append(image)
        frame=dict(rect=[idx%COLS*CELL,idx//COLS*CELL,CELL,CELL],source_size=[CELL,CELL],
                   trim_offset=[0,0],anchor=list(anchors),muzzle=list(muzzle),contact=list(contact),duration_ticks=duration)
        if source_frames is not None:frame['source_frames']=source_frames
        return frame
    for role,filename,name,base_state,action_state,scale in choices:
        path=OUT/'source'/filename
        rows=load_grid(filename,actor_scale=scale)
        keyposes=rows[:12]
        cycle=variants(keyposes,True)
        cycle_frames=[pack(frame,1 if index<36 else 2) for index,frame in enumerate(cycle)]
        clips={base_state:dict(loop=True,frames=cycle_frames)}
        if action_state:
            active=variants(rows[12:18],True)
            clips[action_state]=dict(loop=(role=='zombie_basic'),frames=[pack(frame,2 if index<12 else 3) if role=='zombie_basic' else pack(frame,2) for index,frame in enumerate(active)])
        hitposes=variants(rows[12:18],True)[:4]
        clips['hit']=dict(loop=False,frames=[pack(frame,2) for frame in hitposes])
        death=variants(rows[18:24],True)
        clips['die']=dict(loop=False,frames=[pack(frame,2) for frame in death])
        if role=='jalapeno':
            clips['plant']=dict(loop=False,frames=[pack(frame,2) for frame in variants(keyposes[:4],False)])
        preview=clips[base_state]['frames'][0]
        roles[role]=dict(name=name,card=preview,preview=preview,clips=clips)
        records.append(dict(role=role,source=filename,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                            generation='Built-in imagegen, 2026-10-26',pixel_scale=2,actor_scale=scale,
                            authored_key_poses=24,inbetween_method='pixel-space linear interpolation'))
    user_inputs=[
        ('wallnut','xiaobao-user-60.png','小宝 · 坚果墙','idle',
         {'idle':(list(range(20)),3,True,2),'hit':(list(range(20,30)),3,False,1),
          'die':(list(range(30,60)),2,False,1)}),
        ('jalapeno','xiaodu-user-60.png','小杜 · 火爆辣椒','plant',
         {'plant':(list(range(0,10)),4,True,2),'ignite':(list(range(10,45)),1,False,1),
          'hit':(list(range(45,52)),4,False,1),'die':(list(range(52,60)),4,False,1)}),
    ]
    for role,filename,name,base_state,clip_specs in user_inputs:
        source_images,path=user_sheet(filename)
        clips={}
        for state,(indices,steps,loop,duration) in clip_specs.items():
            sampled=([(source_images[index],[index]) for index in indices]
                     if role=='jalapeno' and state=='ignite'
                     else interpolate_source_frames(source_images,indices,steps,loop))
            clip_frames=[pack(image,duration,source_frames=refs) for image,refs in sampled]
            if role=='jalapeno' and state=='ignite':
                if len(clip_frames)!=35 or [f['source_frames'] for f in clip_frames]!=[[i] for i in range(10,45)]:
                    raise ValueError('Xiaodu ignite must contain the 35 ordered source poses 10-44')
                each,remainder=divmod(JALAPENO_IGNITE_DURATION_TICKS,len(clip_frames))
                for index,frame in enumerate(clip_frames):
                    frame['duration_ticks']=each+(index<remainder)
            clips[state]=dict(loop=loop,frames=clip_frames)
        preview=clips[base_state]['frames'][0]
        role_data=dict(name=name,card=preview,preview=preview,clips=clips)
        if role in ('wallnut','jalapeno'):role_data['display_scale_multiplier']=1.2
        roles[role]=role_data
        records.append(dict(role=role,source=filename,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                            source_frame_count=60,source_layout='10 columns x 6 rows',
                            clip_source_frames={state:indices for state,(indices,_,_,_) in clip_specs.items()},
                            inbetween_method='alpha blend between adjacent authored poses; each output frame lists source_frames',
                            pixel_scale=2,anchor=[128,232],origin='user-uploaded'))
    tick_hz=json.loads((ROOT/'assets/config/balance.json').read_text(encoding='utf-8-sig'))['tick_hz']
    for role_info in roles.values():
        for clip in role_info['clips'].values():
            frames=clip['frames']
            signatures=[]
            for frame in frames:
                x,y,_,_=frame['rect']
                cell_index=(y//CELL)*COLS+x//CELL
                packed=pygame.Surface((CELL,CELL),pygame.SRCALPHA)
                packed.blit(cells[cell_index],(0,0))
                signatures.append(pygame.image.tobytes(packed,'RGBA'))
            assign_clip_durations(frames,signatures,tick_hz,clip['loop'])
    # Keep the authored fire burst exact: 35 poses span precisely two seconds.
    ignite=roles['jalapeno']['clips']['ignite']['frames']
    each,remainder=divmod(JALAPENO_IGNITE_DURATION_TICKS,len(ignite))
    for index,frame in enumerate(ignite):frame['duration_ticks']=each+(index<remainder)
    atlas=pygame.Surface((COLS*CELL,((len(cells)+COLS-1)//COLS)*CELL),pygame.SRCALPHA)
    for i,image in enumerate(cells):atlas.blit(image,(i%COLS*CELL,i//COLS*CELL))
    atlas_name='atlas-004.png'
    pygame.image.save(atlas,str(OUT/atlas_name))
    manifest=dict(schema_version=1,skin_id='dogs',display_name='门头沟小狗',atlas=atlas_name,pixel_scale=2,
                  source_refs=['generated-dog-skins','user-dog-animation-sheets'],roles=roles,mapping_status='approved',mapping_date='2026-10-26')
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
    (OUT/'provenance.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
    sources_path=ROOT/'assets/sources.json';sources=json.loads(sources_path.read_text(encoding='utf-8-sig'))
    sources['generated-dog-skins']=dict(source='Built-in imagegen, 2026-10-26',roles=[row[0] for row in choices],
        actions=['idle','produce','attack','walk','bite','hit','die','plant','ignite'],version='user-approved dog mapping 2026-10-25',
        reference_time_range='cartoon interpretations from user-approved mappings; no footage frame extraction',
        notes='Generated cartoon artwork; Huanghuang, Xiaobao and Xiaodu are mapped by user instruction. Aoaoao uses red vest for zombie-side clarity. These assets do not claim photographic likeness.',
        reference_urls=['https://www.douyin.com/video/7602901155340913962','https://www.douyin.com/shipin/7642911662139476004'],
        derivation='Six-column, four-row 256px source sheets; fixed foot baseline and 2x pixel scale. The frames retain transparent source artwork in assets/skins/dogs/source.')
    user_records={row['role']:row for row in records if row.get('origin')=='user-uploaded'}
    sources['user-dog-animation-sheets']=dict(source='User-uploaded PNG sprite sheets',roles=['wallnut','jalapeno'],
        actions=['idle','hit','die','plant','ignite'],version='2026-10-26',
        files={record['role']:dict(path='skins/dogs/source/'+record['source'],sha256=record['sha256'],
                                   frames=record['source_frame_count'],layout=record['source_layout'])
               for record in user_records.values()},
        notes='Xiaobao is mapped to wallnut and Xiaodu to jalapeno. Source sheets are preserved unchanged; generated in-betweens identify their adjacent source frame indices.')
    sources_path.write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf8')
    print('Compiled',len(cells),'2x dog frames across',len(roles),'roles')


if __name__=='__main__':main()
