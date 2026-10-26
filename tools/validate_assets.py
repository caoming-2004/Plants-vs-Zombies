from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from pvz_game.presentation.skin_catalog import Catalog, AssetError
from pvz_game.presentation.dog_validation import validate_dog_non_overlap
import pygame
from pvz_game.presentation.skin_catalog import REQUIRED
from pvz_game.presentation.animation import (pose_rate_hz, POSE_RATE_MIN_HZ,
    POSE_RATE_MAX_HZ, JALAPENO_IGNITE_DURATION_TICKS)
from pvz_game.config import load


def main():
    catalog=Catalog()
    default_skin=catalog.load('default')
    config,_=load()
    for name in ('default','dogs','dogs_photo'):
        skin=catalog.load(name,refresh=True)
        if name=='default':
            for key in ('background','menu','seedbank','mower','shovel','shovelbank','sun','projectile','card_sunflower','card_peashooter'):
                if key not in skin.ui:raise AssetError('默认界面资源缺失：'+key)
        else:
            diagnostics=validate_dog_non_overlap(skin,default_skin)
            if diagnostics:
                raise AssetError('狗狗主体尺寸或相邻遮挡验证失败：\n'+'\n'.join(diagnostics))
        count=0
        for role,states in REQUIRED.items():
            for state in states:
                clip=skin.clip(role,state);frames=clip['frames']
                count+=len(frames)
                duration=sum(frame['duration_ticks'] for frame in frames)
                unique=len({pygame.image.tobytes(skin.surface(frame),'RGBA') for frame in frames})
                rate=pose_rate_hz(unique,duration,config['tick_hz'])
                if name in ('dogs','dogs_photo') and role=='jalapeno' and state=='ignite':
                    refs=[frame.get('source_frames') for frame in frames]
                    if len(frames)!=35 or refs!=[[i] for i in range(10,45)]:
                        raise AssetError('dogs/jalapeno/ignite must contain the 35 ordered authored source poses')
                    if duration!=JALAPENO_IGNITE_DURATION_TICKS or rate!=17.5:
                        raise AssetError(f'dogs/jalapeno/ignite must last 120 ticks at 17.5 poses/s; got {duration} ticks at {rate:.1f}/s')
                if not POSE_RATE_MIN_HZ<=rate<=POSE_RATE_MAX_HZ:
                    raise AssetError(f'{name}/{role}/{state}: {unique} distinct poses in {duration} ticks ({rate:.1f}/s), expected {POSE_RATE_MIN_HZ}-{POSE_RATE_MAX_HZ}/s')
                if clip['loop'] and duration<60:
                    raise AssetError(f'{name}/{role}/{state}: loop lasts {duration} ticks, below 60')
        print(name+': valid, '+str(count)+' referenced frames; all action clips meet the 12-18 distinct-pose/s cadence')


if __name__=='__main__':
    try:main()
    except AssetError as exc:
        print(str(exc));raise SystemExit(1)
