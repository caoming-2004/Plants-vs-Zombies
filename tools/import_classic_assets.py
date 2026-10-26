"""Repack provenance-pinned reference frames into the runtime atlas contract."""
from pathlib import Path
import json
import shutil
import hashlib
import sys
import pygame

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from pvz_game.presentation.animation import assign_clip_durations
SOURCE=ROOT/'.tools/references/pvz/resources/graphics'
OUT=ROOT/'assets/skins/default'
CELL=256
ATLAS_COLUMNS=8


def blend_pose(left,right,weight):
    """A deterministic in-between for adjacent hand-authored key poses."""
    frame=left.copy()
    overlay=right.copy()
    overlay.set_alpha(round(weight*255))
    frame.blit(overlay,(0,0))
    return frame


def expand_sequence(images,source_duration,subdivisions,loop):
    frames=[]
    for index,image in enumerate(images):
        next_image=images[(index+1)%len(images)] if loop else (images[index+1] if index+1<len(images) else None)
        count=subdivisions if next_image is not None else 1
        durations=[source_duration//count+(part<source_duration%count) for part in range(count)]
        frames.append((image,durations[0]))
        if next_image is not None:
            for part in range(1,count):
                frames.append((blend_pose(image,next_image,part/count),durations[part]))
    return frames


def generated_frames(relative,role,first_row,last_row,source_frames):
    sheet=pygame.image.load(str(OUT/'source'/relative))
    width,height=sheet.get_size()
    if width%6 or height%4:raise ValueError('Generated character sheets must use an exact 6x4 grid')
    cell_w,cell_h=width//6,height//4
    frames=[]
    for row in range(first_row,last_row+1):
        for col in range(6):
            cell=sheet.subsurface((col*cell_w,row*cell_h,cell_w,cell_h)).copy()
            bounds=cell.get_bounding_rect(min_alpha=32)
            if bounds.w==0 or bounds.h==0:
                image=pygame.Surface((CELL,CELL),pygame.SRCALPHA)
            else:
                crop=cell.subsurface(bounds).copy()
                scale=min(150/bounds.w,150/bounds.h)
                scaled=pygame.transform.smoothscale(crop,(max(1,round(bounds.w*scale)),max(1,round(bounds.h*scale))))
                image=pygame.Surface((CELL,CELL),pygame.SRCALPHA)
                image.blit(scaled,(round((CELL-scaled.get_width())/2),224-scaled.get_height()))
            frames.append(image)
    if len(frames)!=source_frames:raise ValueError(f'{relative} has {len(frames)} poses, expected {source_frames}')
    return frames


def load_series(relative):
    directory=SOURCE/relative
    paths=sorted(directory.glob('*.png'),key=lambda p:int(p.stem.rsplit('_',1)[-1]))
    return [(pygame.image.load(str(path)),path) for path in paths]


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    cells=[]
    roles={}
    provenance=[]
    def pack(image,anchor=(128,224),muzzle=(188,118),contact=(76,116),duration=6):
        if image.get_size()!=(CELL,CELL):
            image=pygame.transform.smoothscale(image,(CELL,CELL))
        index=len(cells);cells.append(image)
        return dict(rect=[(index%ATLAS_COLUMNS)*CELL,(index//ATLAS_COLUMNS)*CELL,CELL,CELL],source_size=[CELL,CELL],
                    trim_offset=[0,0],anchor=list(anchor),muzzle=list(muzzle),contact=list(contact),duration_ticks=duration)
    def series(relative,role):
        result=[]
        for original,path in load_series(relative):
            image=pygame.Surface((128,128),pygame.SRCALPHA)
            if role=='zombie_basic':
                scaled=pygame.transform.smoothscale(original,(round(original.get_width()*.7),round(original.get_height()*.7)))
                image.blit(scaled,(-13,13))
            else:
                image.blit(original,(64-35,112-73 if role=='sunflower' else 112-70))
            result.append(image)
            provenance.append(dict(path=path.relative_to(SOURCE).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
        if not result:raise RuntimeError('Missing source frames: '+relative)
        return result
    def packed_sequence(images,source_duration,subdivisions,loop=True):
        return [pack(image,duration=ticks) for image,ticks in expand_sequence(images,source_duration,subdivisions,loop)]
    for role,path in [('sunflower','Plants/SunFlower'),('peashooter','Plants/Peashooter'),('zombie_basic','Zombies/NormalZombie/Zombie')]:
        idle_images=series(path,role)
        if role=='zombie_basic':
            action_images=series('Zombies/NormalZombie/ZombieAttack',role)
            death_images=series('Zombies/NormalZombie/ZombieDie',role)
            idle=packed_sequence(idle_images,9,4,True)
            action=packed_sequence(action_images,9,4,True)
            death=packed_sequence(death_images,9,4,False)
            clips=dict(walk=dict(loop=True,frames=idle),bite=dict(loop=True,frames=action))
        else:
            idle=packed_sequence(idle_images,6,3,True)
            action=[dict(f) for f in idle]
            # Original references have no separate plant death sequence. A short
            # renderer-only disappearance is explicitly recorded as derived.
            first_cell=cells[idle[0]['rect'][1]//CELL*ATLAS_COLUMNS+idle[0]['rect'][0]//CELL]
            death=[]
            for alpha in (255,210,155,90):
                img=first_cell.copy();img.set_alpha(alpha)
                death.append(pack(img,duration=2))
            clips=dict(idle=dict(loop=True,frames=idle))
            clips['produce' if role=='sunflower' else 'attack']=dict(loop=True,frames=action)
        hit_source=action_images[:4] if role=='zombie_basic' else idle_images[:4]
        clips['hit']=dict(loop=False,frames=[pack(img,duration=2) for img in hit_source])
        clips['die']=dict(loop=False,frames=death)
        roles[role]=dict(name={'sunflower':'向日葵','peashooter':'豌豆射手','zombie_basic':'普通僵尸'}[role],
                         card=idle[0],preview=idle[0],clips=clips)
    # Generated high-density sheets add the two missing classic plant roles.
    for role,filename,name in [('wallnut','wallnut-sheet.png','坚果墙'),
                               ('jalapeno','jalapeno-sheet.png','火爆辣椒')]:
        idle_images=generated_frames(filename,role,0,1,12)
        active_images=generated_frames(filename,role,2,2,6)
        end_images=generated_frames(filename,role,3,3,6)
        idle=packed_sequence(idle_images,5,2,True)
        if role=='wallnut':
            clips={'idle':dict(loop=True,frames=idle),
                   'hit':dict(loop=False,frames=packed_sequence(active_images[:4],4,2,False)),
                   'die':dict(loop=False,frames=packed_sequence(end_images,10,4,True))}
        else:
            clips={'idle':dict(loop=True,frames=idle),
                   'plant':dict(loop=False,frames=packed_sequence(idle_images[:4],4,4,False)),
                   'ignite':dict(loop=False,frames=packed_sequence(active_images,10,4,True)),
                   'hit':dict(loop=False,frames=packed_sequence(active_images[:4],4,2,False)),
                   'die':dict(loop=False,frames=packed_sequence(end_images,10,4,True))}
        preview=clips['idle']['frames'][0]
        roles[role]=dict(name=name,card=preview,preview=preview,clips=clips)
        provenance.append(dict(path='generated/'+filename,sha256=hashlib.sha256((OUT/'source'/filename).read_bytes()).hexdigest()))
    tick_hz=json.loads((ROOT/'assets/config/balance.json').read_text(encoding='utf-8-sig'))['tick_hz']
    for role_info in roles.values():
        for clip in role_info['clips'].values():
            frames=clip['frames']
            signatures=[]
            for frame in frames:
                x,y,_,_=frame['rect']
                cell_index=(y//CELL)*ATLAS_COLUMNS+x//CELL
                packed=pygame.Surface((CELL,CELL),pygame.SRCALPHA)
                packed.blit(cells[cell_index],(0,0))
                signatures.append(pygame.image.tobytes(packed,'RGBA'))
            assign_clip_durations(frames,signatures,tick_hz,clip['loop'])
    atlas=pygame.Surface((ATLAS_COLUMNS*CELL,((len(cells)+ATLAS_COLUMNS-1)//ATLAS_COLUMNS)*CELL),pygame.SRCALPHA)
    for i,image in enumerate(cells):atlas.blit(image,((i%ATLAS_COLUMNS)*CELL,(i//ATLAS_COLUMNS)*CELL))
    atlas_tmp=OUT/'atlas.generated.png'
    pygame.image.save(atlas,str(atlas_tmp))
    atlas_tmp.replace(OUT/'atlas.png')
    ui={}
    originals={
        'background':'Items/Background/Background_0.jpg','menu':'Screen/MainMenu.png',
        'seedbank':'Screen/ChooserBackground.png','mower':'Screen/car.png',
        'card_sunflower':'Cards/card_sunflower.png','card_peashooter':'Cards/card_peashooter.png',
        'projectile':'Bullets/PeaNormal/PeaNormal_0.png','sun':'Plants/Sun/Sun_0.png',
        'victory':'Screen/GameVictory.png','defeat':'Screen/GameLoose.png'}
    for name,relative in originals.items():
        path=SOURCE/relative
        dest=OUT/('ui-'+name+path.suffix)
        shutil.copyfile(path,dest)
        ui[name]=dest.name
        provenance.append(dict(path=relative,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    extra=ROOT/'.tools/references/original-ui'
    for name,filename in [('shovel','Shovel.png'),('shovelbank','ShovelBank.png')]:
        path=extra/filename
        if path.exists():
            dest=OUT/('ui-'+name+'.png');shutil.copyfile(path,dest);ui[name]=dest.name
            provenance.append(dict(path='original-ui/'+filename,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    # Shelf-pack UI to a dedicated atlas, keeping full source rectangles.
    ui_images={name:pygame.image.load(str(OUT/relative)) for name,relative in ui.items()}
    layout={};x=y=row_height=0
    for name,img in ui_images.items():
        iw,ih=img.get_size()
        if x+iw>2048:x=0;y+=row_height;row_height=0
        layout[name]=dict(rect=[x,y,iw,ih]);x+=iw;row_height=max(row_height,ih)
    ui_atlas=pygame.Surface((2048,y+row_height),pygame.SRCALPHA)
    for name,img in ui_images.items():
        if name=='mower':img.set_colorkey((0,0,0))
        ui_atlas.blit(img,layout[name]['rect'][:2])
    pygame.image.save(ui_atlas,str(OUT/'ui-atlas.png'))
    manifest=dict(schema_version=1,skin_id='default',display_name='经典外观',atlas='atlas.png',pixel_scale=2,
                  source_refs=['classic-reference-frames','classic-ui-extracted','generated-classic-plants'],roles=roles,ui=layout,ui_atlas='ui-atlas.png',
                  derivations=['Plant idle/attack/produce share source cyclic frames; hit is overlay; plant death is derived fade.'])
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
    (OUT/'provenance.json').write_text(json.dumps(dict(commit=(ROOT/'.tools/references/pvz-commit.txt').read_text().strip(),files=provenance),indent=2),encoding='utf8')
    sources_path=ROOT/'assets/sources.json'
    sources=json.loads(sources_path.read_text())
    sources['classic-reference-frames']=dict(source='https://github.com/marblexu/PythonPlantsVsZombies',
        commit=(ROOT/'.tools/references/pvz-commit.txt').read_text().strip(),version='PC classic reference, community-exported frames',
        roles=['sunflower','peashooter','zombie_basic','ui','mower','sun','projectile'],
        actions=['idle','produce','attack','walk','bite','hit','die'],
        notes='Source project marks personal learning and noncommercial use; character/media rights are not implied to be an open-source license.',
        derivation='See skins/default/provenance.json and manifest derivations; plant death uses derived fade, original frame timing not independently verified.')
    sources['classic-ui-extracted']=dict(source='https://github.com/FregD156/PvZ_Assets',
        commit=(extra/'commit.txt').read_text(encoding='utf-8-sig').strip(),
        roles=['shovel','shovelbank'],actions=['idle','selected'],version='original-game extracted UI reference',
        notes='Source describes main.pak extraction; asset ownership remains with original creators.')
    sources['generated-classic-plants']=dict(source='Built-in imagegen',version='2026-10-26',
        roles=['wallnut','jalapeno'],actions=['idle','hit','die','plant','ignite'],
        notes='Original generated cartoon game character sheets; not photographs or extracted original-game art. High-density source frames are included in assets/skins/default/source.')
    sources_path.write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf8')
    print('Packed',len(cells),'frames',len(provenance),'source checksums')


if __name__=='__main__':main()
