"""Compile approved high-density dog pose sheets into deterministic anchored clips."""
from pathlib import Path
import copy
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


def beiwo_sheet(filename='beiwo-sheet.png'):
    """Import the preserved 4x3 source separately from the 6x4 art sheets."""
    path=OUT/'source'/filename
    sheet=pygame.image.load(str(path))
    if sheet.get_size()!=(1448,1086):
        raise ValueError(f'{filename} must remain the original 1448x1086 4x3 sheet')
    frames=[]
    cell_width,cell_height=sheet.get_width()/4,sheet.get_height()/3
    for index in range(12):
        row,col=divmod(index,4)
        rect=pygame.Rect(round(col*cell_width),round(row*cell_height),
                         round((col+1)*cell_width)-round(col*cell_width),
                         round((row+1)*cell_height)-round(row*cell_height))
        cell=sheet.subsurface(rect).copy()
        mask=pygame.mask.from_surface(cell,96)
        components=mask.connected_components(80)
        body=max(components,key=lambda component:component.count(),default=None)
        if body is None:
            raise ValueError(f'{filename} contains an empty source frame {index}')
        silhouette=body.to_surface(setcolor=(255,255,255,255),unsetcolor=(0,0,0,0))
        cell.blit(silhouette,(0,0),special_flags=pygame.BLEND_RGBA_MULT)
        bounds=cell.get_bounding_rect(min_alpha=96)
        canvas=pygame.Surface((CELL,CELL),pygame.SRCALPHA)
        crop=cell.subsurface(bounds).copy()
        scale=min(220/bounds.w,214/bounds.h)
        size=(max(1,round(bounds.w*scale)),max(1,round(bounds.h*scale)))
        crop=pygame.transform.smoothscale(crop,size)
        canvas.blit(crop,((CELL-size[0])//2,232-size[1]))
        frames.append(canvas)
    if len({pygame.image.tobytes(frame,'RGBA') for frame in frames})!=12:
        raise ValueError(f'{filename} must contain 12 distinct source poses')
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


def cartoonize_frame(image):
    """Reduce photographic detail to a clean, repeatable illustrated sprite."""
    small=pygame.transform.smoothscale(image,(64,64))
    pixels=pygame.PixelArray(small)
    for x in range(small.get_width()):
        for y in range(small.get_height()):
            color=small.unmap_rgb(pixels[x,y])
            if color.a<96:
                pixels[x,y]=small.map_rgb((0,0,0,0))
            else:
                channels=tuple(min(255,round(value/32)*32) for value in color[:3])
                pixels[x,y]=small.map_rgb((*channels,255))
    del pixels
    return pygame.transform.scale(small,image.get_size())


def main():
    choices=[
      ('sunflower','beiwo-sheet-hd.png','被窝 · 金围巾','idle','produce',1.30),
      ('zombie_basic','aoao-red-sheet-hd.png','嗷嗷嗷 · 红背心','walk','bite',1.60),
    ]
    cells=[];roles={};records=[];cell_cache={}
    def pack(image,duration=2,anchors=(128,232),muzzle=(185,122),contact=(70,150),source_frames=None):
        signature=hashlib.sha256(pygame.image.tobytes(image,'RGBA')).digest()
        idx=cell_cache.get(signature)
        if idx is None:
            idx=len(cells);cells.append(image);cell_cache[signature]=idx
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
        ('wallnut','xiaobao-user-20261026.png','小宝 · 坚果墙','idle',
         {'idle':(list(range(20)),3,True,2),'hit':(list(range(20,30)),3,False,1),
          'die':(list(range(30,60)),2,False,1)},1.15),
        ('jalapeno','xiaodu-user-20261026.png','小杜 · 火爆辣椒','plant',
         {'plant':(list(range(0,10)),4,True,2),'ignite':(list(range(10,45)),1,False,1),
          'hit':(list(range(45,52)),4,False,1),'die':(list(range(52,60)),4,False,1)},0.92),
        ('peashooter','haohazi-user-20261026.png','好孩子 · 豌豆射手','idle',
         {'idle':(list(range(20)),2,True,1),'attack':(list(range(20,40)),2,False,1),
          'hit':(list(range(40,50)),2,False,1),'die':(list(range(50,60)),2,False,1)},1.10),
    ]
    photo_cells=[];photo_roles={};photo_records=[];photo_cell_cache={}
    def pack_photo(image,duration=2,anchors=(128,232),muzzle=(185,122),contact=(70,150),source_frames=None):
        signature=hashlib.sha256(pygame.image.tobytes(image,'RGBA')).digest()
        idx=photo_cell_cache.get(signature)
        if idx is None:
            idx=len(photo_cells);photo_cells.append(image);photo_cell_cache[signature]=idx
        frame=dict(rect=[idx%COLS*CELL,idx//COLS*CELL,CELL,CELL],source_size=[CELL,CELL],
                   trim_offset=[0,0],anchor=list(anchors),muzzle=list(muzzle),contact=list(contact),duration_ticks=duration)
        if source_frames is not None:frame['source_frames']=source_frames
        return frame
    cloned={}
    def clone_frame(frame):
        key=tuple(frame['rect'])
        if key not in cloned:
            x,y,_,_=frame['rect']
            source_index=(y//CELL)*COLS+x//CELL
            image=cells[source_index].copy()
            cloned[key]=pack_photo(image,frame['duration_ticks'],frame['anchor'],
                                   frame['muzzle'],frame['contact'],frame.get('source_frames'))
        clone=copy.deepcopy(cloned[key])
        clone['duration_ticks']=frame['duration_ticks']
        if 'source_frames' in frame:clone['source_frames']=list(frame['source_frames'])
        return clone
    def clone_role(role):
        source=roles[role]
        result=dict(source)
        result['card']=clone_frame(source['card'])
        result['preview']=clone_frame(source['preview'])
        result['clips']={
            state:dict(clip,frames=[clone_frame(frame) for frame in clip['frames']])
            for state,clip in source['clips'].items()
        }
        return result
    for role in ('zombie_basic',):
        photo_roles[role]=clone_role(role)
    beiwo_images,beiwo_path=beiwo_sheet()
    beiwo_specs={
        'idle':(list(range(0,4)),4,True,1),
        'produce':(list(range(4,8)),4,False,1),
        'hit':(list(range(4,8)),4,False,1),
        'die':(list(range(8,12)),4,False,1),
    }
    beiwo_clips={}
    for state,(indices,steps,loop,duration) in beiwo_specs.items():
        sampled=interpolate_source_frames(beiwo_images,indices,steps,loop)
        beiwo_clips[state]=dict(
            loop=loop,
            frames=[pack_photo(image,duration,source_frames=refs)
                    for image,refs in sampled],
        )
    beiwo_preview=beiwo_clips['idle']['frames'][0]
    photo_roles['sunflower']=dict(name='被窝 · 金围巾',card=beiwo_preview,
                                  preview=beiwo_preview,clips=beiwo_clips)
    photo_records.append(dict(
        role='sunflower',source=beiwo_path.name,
        sha256=hashlib.sha256(beiwo_path.read_bytes()).hexdigest(),
        source_frame_count=12,source_layout='4 columns x 3 rows',
        clip_source_frames={state:indices for state,(indices,_,_,_) in beiwo_specs.items()},
        inbetween_method='original source poses with anchored alpha-blended transitions',
        pixel_scale=2,anchor=[128,232],origin='preserved-cartoon-source'))
    roles['sunflower']['display_scale_multiplier']=1.02
    roles['zombie_basic']['display_scale_multiplier']=1.0
    photo_roles['sunflower']['display_scale_multiplier']=1.02
    photo_roles['zombie_basic']['display_scale_multiplier']=1.0
    for role,filename,name,base_state,clip_specs,scale in user_inputs:
        source_images,path=user_sheet(filename)
        if pygame.image.load(str(path)).get_size()!=(1619,971):
            raise ValueError(f'{filename} must be the preserved 1619x971 user source sheet')
        for state,(indices,_,_,_) in clip_specs.items():
            if min(indices)<0 or max(indices)>=len(source_images):
                raise ValueError(f'{filename} has an invalid {state} source-frame range')
        def build_user_role(target_pack,stylized):
            images=[cartoonize_frame(image) for image in source_images] if stylized else source_images
            derived_source=None
            derived_digest=None
            if stylized:
                source_atlas=pygame.Surface((10*CELL,6*CELL),pygame.SRCALPHA)
                for source_index,image in enumerate(images):
                    source_atlas.blit(image,((source_index%10)*CELL,(source_index//10)*CELL))
                derived_source=path.stem.replace('-user-20261026','')+'-cartoon-20261026.png'
                derived_path=OUT/'source'/derived_source
                pygame.image.save(source_atlas,str(derived_path))
                derived_digest=hashlib.sha256(derived_path.read_bytes()).hexdigest()
            clips={}
            for state,(indices,steps,loop,duration) in clip_specs.items():
                sampled=([(images[index],[index]) for index in indices]
                         if role=='jalapeno' and state=='ignite'
                         else interpolate_source_frames(images,indices,steps,loop))
                clip_frames=[target_pack(image,duration,source_frames=refs) for image,refs in sampled]
                if role=='jalapeno' and state=='ignite':
                    if len(clip_frames)!=35 or [f['source_frames'] for f in clip_frames]!=[[i] for i in range(10,45)]:
                        raise ValueError('Xiaodu ignite must contain the 35 ordered source poses 10-44')
                    each,remainder=divmod(JALAPENO_IGNITE_DURATION_TICKS,len(clip_frames))
                    for index,frame in enumerate(clip_frames):
                        frame['duration_ticks']=each+(index<remainder)
                clips[state]=dict(loop=loop,frames=clip_frames)
            preview=clips[base_state]['frames'][0]
            role_data=dict(name=name,card=preview,preview=preview,clips=clips,
                           display_scale_multiplier=scale)
            return role_data,derived_source,derived_digest
        roles[role],derived_source,derived_digest=build_user_role(pack,True)
        photo_roles[role],_,_=build_user_role(pack_photo,False)
        records.append(dict(role=role,source=filename,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                            source_frame_count=60,source_layout='10 columns x 6 rows',
                            clip_source_frames={state:indices for state,(indices,_,_,_) in clip_specs.items()},
                            inbetween_method='pixelated color-quantized cartoon adaptation; every output frame lists original source_frames',
                            pixel_scale=2,anchor=[128,232],origin='stylized-user-upload',
                            derived_source=derived_source,derived_sha256=derived_digest))
        photo_records.append(dict(role=role,source=filename,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                            source_frame_count=60,source_layout='10 columns x 6 rows',
                            clip_source_frames={state:indices for state,(indices,_,_,_) in clip_specs.items()},
                            inbetween_method='authored photo poses; output frames retain original source_frames',
                            pixel_scale=2,anchor=[128,232],origin='user-uploaded'))
    tick_hz=json.loads((ROOT/'assets/config/balance.json').read_text(encoding='utf-8-sig'))['tick_hz']
    for skin_roles,skin_cells in ((roles,cells),(photo_roles,photo_cells)):
        for role_info in skin_roles.values():
            for clip in role_info['clips'].values():
                frames=clip['frames']
                signatures=[]
                for frame in frames:
                    x,y,_,_=frame['rect']
                    cell_index=(y//CELL)*COLS+x//CELL
                    packed=pygame.Surface((CELL,CELL),pygame.SRCALPHA)
                    packed.blit(skin_cells[cell_index],(0,0))
                    signatures.append(pygame.image.tobytes(packed,'RGBA'))
                assign_clip_durations(frames,signatures,tick_hz,clip['loop'])
    for skin_roles in (roles,photo_roles):
        ignite=skin_roles['jalapeno']['clips']['ignite']['frames']
        each,remainder=divmod(JALAPENO_IGNITE_DURATION_TICKS,len(ignite))
        for index,frame in enumerate(ignite):frame['duration_ticks']=each+(index<remainder)
    atlas=pygame.Surface((COLS*CELL,((len(cells)+COLS-1)//COLS)*CELL),pygame.SRCALPHA)
    for i,image in enumerate(cells):atlas.blit(image,(i%COLS*CELL,i//COLS*CELL))
    atlas_name='atlas-004.png'
    pygame.image.save(atlas,str(OUT/atlas_name))
    photo_directory=ROOT/'assets/skins/dogs_photo'
    photo_directory.mkdir(parents=True,exist_ok=True)
    photo_atlas=pygame.Surface((COLS*CELL,((len(photo_cells)+COLS-1)//COLS)*CELL),pygame.SRCALPHA)
    for i,image in enumerate(photo_cells):photo_atlas.blit(image,(i%COLS*CELL,i//COLS*CELL))
    photo_atlas_name='atlas-001.png'
    pygame.image.save(photo_atlas,str(photo_directory/photo_atlas_name))
    manifest=dict(schema_version=1,skin_id='dogs',display_name='门头沟小狗',atlas=atlas_name,pixel_scale=2,
                  source_refs=['generated-dog-skins','generated-dog-cartoon-005','user-dog-animation-sheets-005'],
                  roles=roles,mapping_status='approved',mapping_date='2026-10-26')
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
    (OUT/'provenance.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
    photo_manifest=dict(schema_version=1,skin_id='dogs_photo',display_name='门头沟小狗 · 照片版',
                        atlas=photo_atlas_name,pixel_scale=2,
                        source_refs=['generated-dog-skins','user-dog-animation-sheets-005',
                                     'beiwo-photo-cartoon-source'],
                        roles=photo_roles,mapping_status='approved',mapping_date='2026-10-26')
    (photo_directory/'manifest.json').write_text(
        json.dumps(photo_manifest,ensure_ascii=False,indent=2),encoding='utf8')
    (photo_directory/'provenance.json').write_text(
        json.dumps(photo_records,ensure_ascii=False,indent=2),encoding='utf8')
    sources_path=ROOT/'assets/sources.json';sources=json.loads(sources_path.read_text(encoding='utf-8-sig'))
    sources['generated-dog-skins']=dict(source='Built-in imagegen, 2026-10-26',roles=list(roles),
        actions=['idle','produce','attack','walk','bite','hit','die','plant','ignite'],version='user-approved dog mapping 2026-10-25',
        reference_time_range='cartoon interpretations from user-approved mappings; no footage frame extraction',
        notes='Generated cartoon artwork; Haohazi replaces Huanghuang as peashooter, Xiaobao maps to wallnut, and Xiaodu maps to jalapeno. Aoaoao remains the red-vest zombie. These assets do not claim photographic likeness.',
        reference_urls=['https://www.douyin.com/video/7602901155340913962','https://www.douyin.com/shipin/7642911662139476004'],
        derivation='Six-column, four-row 256px source sheets plus user-approved identity-based cartoon adaptations; fixed foot baseline and 2x pixel scale.')
    sources['generated-dog-cartoon-005']=dict(
        source='Deterministic local adaptation of user-uploaded animation sheets',
        version='2026-10-26',
        roles=['peashooter','wallnut','jalapeno'],
        derivation='Frames are reduced to 64x64, color-quantized and enlarged with nearest-neighbor sampling; original source-frame indexes remain in dogs/provenance.json.',
        files={
            row['role']:{
                'path':'skins/dogs/source/'+row['derived_source'],
                'sha256':row['derived_sha256'],
                'layout':'10 columns x 6 rows; 256px cells',
                'derived_from':row['source'],
            }
            for row in records if row.get('origin')=='stylized-user-upload'
        },
        notes='The original uploaded sheets are preserved unchanged; this is a stylized cartoon treatment, not a claim of hand-drawn or photographic artwork.')
    user_records={row['role']:row for row in photo_records}
    sources['user-dog-animation-sheets']=dict(source='User-uploaded PNG sprite sheets',
        roles=['peashooter','wallnut','jalapeno'],
        actions=['idle','attack','hit','die','plant','ignite'],version='2026-10-26',
        files={record['role']:dict(path='skins/dogs/source/'+record['source'],sha256=record['sha256'],
                                   frames=record['source_frame_count'],layout=record['source_layout'])
               for record in user_records.values()},
        notes='The updated 005 photo skin adds Haohazi as peashooter. Original source sheets are preserved unchanged; derived frames identify their source indexes.')
    sources['user-dog-animation-sheets-005']={
        'source':'User-uploaded transparent PNG pose sheets',
        'version':'2026-10-26',
        'layout':'10 columns x 6 rows; 1619 x 971 pixels',
        'files':{
            row['role']:{
                'dog':{'sunflower':'被窝','peashooter':'好孩子','wallnut':'小宝','jalapeno':'小杜'}[row['role']],
                'path':'skins/dogs/source/'+row['source'],
                'sha256':row['sha256'],
                'frames':60,
                'layout':'10 columns x 6 rows',
            }
            for row in photo_records
        },
        'derivation':'dogs_photo uses cleaned photo poses; dogs uses a deterministic cartoon adaptation. Original PNG files remain unchanged.',
    }
    sources['beiwo-photo-cartoon-source']={
        'source':'Preserved local user-provided cartoon sprite sheet',
        'file':'skins/dogs/source/beiwo-sheet.png',
        'sha256':hashlib.sha256(beiwo_path.read_bytes()).hexdigest(),
        'dimensions':[1448,1086],
        'layout':'4 columns x 3 rows',
        'role':'dogs_photo sunflower',
        'derivation':'Imported with a dedicated 4x3 path; original gold scarf and source PNG remain unchanged.',
    }
    sources_path.write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf8')
    print('Compiled',len(cells),'cartoon frames and',len(photo_cells),'photo frames across',len(roles),'roles')


if __name__=='__main__':main()
