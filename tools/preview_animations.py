"""Preview every role and transition; optionally export contact sheets and GIFs."""
from pathlib import Path
import argparse
import os
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import pygame
from pvz_game.presentation.skin_catalog import Catalog, REQUIRED
from pvz_game.presentation.animation import DOG_SCALE, blit_frame, frame_at, display_scale_for_role
from pvz_game.resources import resource


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--export',type=Path)
    parser.add_argument('--frames',type=int,default=0)
    args=parser.parse_args()
    if args.export:os.environ.setdefault('SDL_VIDEODRIVER','dummy')
    pygame.display.init();pygame.font.init()
    window=pygame.display.set_mode((1000,660))
    pygame.display.set_caption('动画预览 · 空格切换外观，Esc退出')
    font=pygame.font.Font(str(resource('fonts/NotoSansSC.ttf')),16)
    catalog=Catalog();skin_id='default';tick=0;frames=0
    if args.export:args.export.mkdir(parents=True,exist_ok=True)
    clock=pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type==pygame.QUIT or event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE:
                pygame.quit();return
            if event.type==pygame.KEYDOWN and event.key==pygame.K_SPACE:
                skin_id='dogs' if skin_id=='default' else 'default'
        window.fill((219,227,198));skin=catalog.load(skin_id)
        dog=skin_id=='dogs'
        for row,(role,states) in enumerate(REQUIRED.items()):
            for col,state in enumerate(states):
                x=130+col*240;y=190+row*205
                pygame.draw.line(window,(123,141,106),(x-85,y),(x+85,y),1)
                blit_frame(window,skin,frame_at(skin.clip(role,state),tick),(x,y),
                           display_scale_for_role(skin,role,DOG_SCALE if dog else 1))
                window.blit(font.render(skin.data['roles'][role]['name']+' / '+state,True,(40,60,35)),(x-90,y+12))
        window.blit(font.render(skin.data['display_name']+' · 全部动作（脚底基线可见）',True,(40,60,35)),(30,16))
        pygame.display.flip()
        if args.export:
            pygame.image.save(window,str(args.export/(skin_id+'-actions.png')))
            # Export all actual poses in order for independent loop inspection.
            for role,states in REQUIRED.items():
                for state in states:
                    clip=skin.clip(role,state);count=len(clip['frames'])
                    strip=pygame.Surface((128*count,160),pygame.SRCALPHA)
                    for index,f in enumerate(clip['frames']):
                        blit_frame(strip,skin,f,(index*128+64,112),
                                   display_scale_for_role(skin,role,DOG_SCALE if dog else 1))
                    pygame.image.save(strip,str(args.export/(skin_id+'-'+role+'-'+state+'.png')))
            if skin_id=='dogs':break
            skin_id='dogs';continue
        tick+=1;frames+=1
        if args.frames and frames>=args.frames:break
        clock.tick(60)
    pygame.quit()


if __name__=='__main__':main()
