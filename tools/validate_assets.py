from pathlib import Path
import hashlib
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from pvz_game.presentation.skin_catalog import Catalog, AssetError
from pvz_game.presentation.backgrounds import BackgroundCatalog
from pvz_game.presentation.dog_validation import validate_dog_non_overlap, validate_dog_canvas_bounds
import pygame
from pvz_game.presentation.skin_catalog import REQUIRED, REQUIRED_BY_SKIN
from pvz_game.presentation.animation import (pose_rate_hz, POSE_RATE_MIN_HZ,
    POSE_RATE_MAX_HZ, JALAPENO_IGNITE_DURATION_TICKS)
from pvz_game.config import load, load_campaign


def main():
    music_dir=Path(__file__).resolve().parents[1]/'assets'/'music'
    music_manifest=json.loads((music_dir/'provenance.json').read_text(encoding='utf-8'))
    if not isinstance(music_manifest.get('tracks'),list) or len(music_manifest['tracks'])!=3:
        raise SystemExit('music provenance must list exactly three tracks')
    for track in music_manifest['tracks']:
        path=music_dir/track['file']
        if not path.is_file() or path.suffix.lower()!='.mp3':
            raise SystemExit('missing or unsupported music file: '+track['file'])
        if track.get('license')!='CC0 1.0' or not track.get('source'):
            raise SystemExit('music source/license missing: '+track['file'])
        if hashlib.sha256(path.read_bytes()).hexdigest()!=track.get('sha256'):
            raise SystemExit('music hash mismatch: '+track['file'])
    print('music: valid, 3 offline tracks with CC0 provenance and matching hashes')
    config, campaign, levels = load_campaign()
    print('campaign: valid, '+str(len(levels))+' stages; endless unlock after '+campaign['endless']['unlock_after'])
    backgrounds = BackgroundCatalog()
    if backgrounds.error:
        raise SystemExit('backgrounds invalid: ' + backgrounds.error)
    print('backgrounds: valid, '+str(len(backgrounds.order))+' options, default '+backgrounds.default_id)
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
            diagnostics.extend(validate_dog_canvas_bounds(skin))
            if diagnostics:
                raise AssetError('狗狗主体尺寸或相邻遮挡验证失败：\n'+'\n'.join(diagnostics))
        count=0
        required_roles=dict(REQUIRED)
        required_roles.update(REQUIRED_BY_SKIN.get(name,{}))
        for role,states in required_roles.items():
            for state in states:
                clip=skin.clip(role,state);frames=clip['frames']
                count+=len(frames)
                duration=sum(frame['duration_ticks'] for frame in frames)
                unique=len({pygame.image.tobytes(skin.surface(frame),'RGBA') for frame in frames})
                rate=pose_rate_hz(unique,duration,config['tick_hz'])
                if name in ('dogs','dogs_photo') and role=='jalapeno' and state=='ignite':
                    refs=[frame.get('source_frames') for frame in frames]
                    if not refs or any(not set(ref)<=set(range(12)) for ref in refs):
                        raise AssetError('dogs/jalapeno/ignite has invalid source pose references')
                    if duration!=JALAPENO_IGNITE_DURATION_TICKS:
                        raise AssetError(f'dogs/jalapeno/ignite must last 120 ticks; got {duration}')
                plant_cycle=role in ('sunflower','peashooter','wallnut','jalapeno','pangbaobao','huanghuang') and clip['loop']
                expected_low,expected_high=(11,13) if plant_cycle else (POSE_RATE_MIN_HZ,POSE_RATE_MAX_HZ)
                if not expected_low<=rate<=expected_high:
                    raise AssetError(f'{name}/{role}/{state}: {unique} distinct poses in {duration} ticks ({rate:.1f}/s), expected {expected_low}-{expected_high}/s')
                if clip['loop'] and duration<60:
                    raise AssetError(f'{name}/{role}/{state}: loop lasts {duration} ticks, below 60')
        print(name+': valid, '+str(count)+' referenced frames; plant loops meet 11-13 poses/s, other clips meet 12-18 poses/s')


if __name__=='__main__':
    try:main()
    except AssetError as exc:
        print(str(exc));raise SystemExit(1)
