import argparse
import json
import math
import os
import platform
import time
from pathlib import Path


def clamp_window_size(size):
    from .config import LOGICAL_WIDTH, LOGICAL_HEIGHT
    return max(LOGICAL_WIDTH,size[0]),max(LOGICAL_HEIGHT,size[1])


def benchmark_window(scene, seconds, output=None):
    """Measure the real display path used by the packaged game."""
    import pygame
    from .config import load, LOGICAL_WIDTH, LOGICAL_HEIGHT
    from .presentation.renderer import Renderer
    from .presentation.skin_catalog import Catalog, AppearanceController
    from .presentation.performance import make_scene, summarize_frame_intervals, SCENES

    if seconds <= 0:
        raise ValueError("Benchmark duration must be positive")
    config, level = load()
    pygame.display.init()
    pygame.font.init()
    window = pygame.display.set_mode((1260, 720), pygame.RESIZABLE)
    pygame.display.set_caption("草坪保卫战 · 实机性能测量")
    appearance = AppearanceController(Catalog())
    appearance.select("plant", "dogs", "menu")
    appearance.select("zombie", "dogs", "menu")
    renderer = Renderer(config, appearance)
    snapshot = make_scene(config, level, scene)
    clock = pygame.time.Clock()
    started = previous = time.perf_counter()
    intervals = []
    try:
        while time.perf_counter() - started < seconds:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise RuntimeError("Benchmark interrupted before 60 seconds")
            snapshot["tick"] = int((time.perf_counter() - started) * config["tick_hz"])
            canvas = renderer.draw(snapshot)
            w, h = window.get_size()
            scale = min(w / LOGICAL_WIDTH, h / LOGICAL_HEIGHT)
            size = (int(LOGICAL_WIDTH * scale), int(LOGICAL_HEIGHT * scale))
            window.fill((24, 40, 28))
            image = pygame.transform.smoothscale(canvas, size)
            window.blit(image, ((w - size[0]) // 2, (h - size[1]) // 2))
            pygame.display.flip()
            clock.tick(60)
            now = time.perf_counter()
            intervals.append((now - previous) * 1000)
            previous = now
        report = summarize_frame_intervals(intervals)
        report.update(scene=scene, load=SCENES[scene], machine=platform.platform(),
                      window_size=list(window.get_size()),
                      driver=pygame.display.get_driver(),
                      measured_at=time.strftime("%Y-%m-%d %H:%M:%S"))
        if output:
            output = Path(output)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print("PERFORMANCE_JSON=" + json.dumps({k: v for k, v in report.items()
                                                if k != "frame_intervals_ms"}, ensure_ascii=False), flush=True)
        return report
    finally:
        pygame.quit()


def run(smoke_frames=0, screenshot=None, smoke_play=False, plant_skin='default', zombie_skin='default', smoke_skins=False,
        input_latency=False, latency_seconds=60, window_size=(1260,720)):
    import pygame
    from .config import load
    from .config import LOGICAL_WIDTH, LOGICAL_HEIGHT
    from .domain.simulation import Simulation
    from .domain.commands import Command
    from .presentation.renderer import Renderer
    from .presentation.input import (click, logical_position, card_at, begin_drag,
                                     update_drag, finish_drag, inside)
    from .presentation.scenes import MESSAGES, BUTTONS
    from .presentation.skin_catalog import Catalog, AppearanceController

    config,level=load()
    pygame.display.init()
    pygame.font.init()
    window=pygame.display.set_mode(clamp_window_size(window_size),pygame.RESIZABLE)
    pygame.display.set_caption("植物大战僵尸小游戏 · 经典与小狗换肤")
    appearance=AppearanceController(Catalog())
    appearance.select('plant',plant_skin,'menu')
    appearance.select('zombie',zombie_skin,'menu')
    renderer=Renderer(config,appearance)
    plant_types={item['id']:item for item in config['plant_types']}
    icon=pygame.Surface((48,48))
    icon.fill((98,150,76))
    pygame.draw.circle(icon,(252,199,62),(24,24),18)
    pygame.draw.circle(icon,(145,88,38),(24,24),11)
    pygame.display.set_icon(icon)
    game=Simulation(config,level)
    if smoke_play:
        game.step([Command("Start")])
        game.sun=1000
        for row in range(5):
            for kind,col in (("sunflower",0),("peashooter",2)):
                game.ready_tick[kind]=0
                game.step([Command("SelectPlant",(kind,)),Command("PlantAt",(row,col),sequence=1)])
        for row in range(5):game.add_zombie(row,x=650+row*10)
    clock=pygame.time.Clock()
    last=time.perf_counter()
    accumulated=0.0
    help_open=False
    skins_open=smoke_skins
    message=""
    message_until=0
    frames=0
    pending_events=[]
    pending_commands=[]
    drag_state=None
    latency_samples=[]
    pending_motion_time=None
    latency_deadline=time.perf_counter()+latency_seconds if input_latency else None
    while game.phase!="quit":
        now=time.perf_counter()
        elapsed=min(now-last,.25)
        last=now
        commands=[]
        snapshot=game.snapshot()
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                commands.append(Command("Quit"))
            elif event.type in (pygame.WINDOWRESIZED,pygame.VIDEORESIZE):
                requested_size=(event.x,event.y) if event.type==pygame.WINDOWRESIZED else (event.w,event.h)
                width,height=clamp_window_size(requested_size)
                if (width,height)!=requested_size:
                    window=pygame.display.set_mode((width,height),pygame.RESIZABLE)
            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_SPACE and game.phase in ("playing","paused"):
                    drag_state=None
                    commands.append(Command("Resume" if game.phase=="paused" else "Pause"))
                elif event.key==pygame.K_ESCAPE:
                    drag_state=None
                    if help_open: help_open=False
                    elif skins_open: skins_open=False
                    elif game.phase=="playing": commands.append(Command("CancelSelection"))
                elif event.key in (pygame.K_1,pygame.K_2) and game.phase=="playing":
                    commands.append(Command("SelectPlant",("sunflower" if event.key==pygame.K_1 else "peashooter",)))
            elif event.type==pygame.WINDOWFOCUSLOST and game.phase=="playing":
                drag_state=None
                commands.append(Command("Pause"))
            elif event.type==pygame.MOUSEBUTTONDOWN:
                point=logical_position(event.pos,window.get_size())
                if event.button==3:
                    drag_state=None
                if event.button==1 and game.phase=="playing":
                    card=card_at(point)
                    if card is not None or point is not None and inside(point,BUTTONS["shovel"]):
                        drag_state=begin_drag(card if card is not None else "shovel",point)
                        continue
                result=click(point,snapshot,config,help_open,event.button,skins_open)
                if result=="open_help": help_open=True
                elif result=="close_help":help_open=False
                elif result=='open_skins':skins_open=True
                elif result=='close_skins':skins_open=False
                elif isinstance(result,str) and result.startswith('choose_'):
                    _,side,skin=result.split('_')
                    appearance.select(side,skin,game.phase)
                elif isinstance(result,Command):
                    if result.kind in ('Start','Restart'):appearance.on_restart()
                    if result.kind in ('Pause','Restart','ReturnToMenu','Quit'):
                        drag_state=None
                    commands.append(result)
            elif event.type==pygame.MOUSEMOTION and drag_state is not None:
                if input_latency:pending_motion_time=time.perf_counter()
                update_drag(drag_state,logical_position(event.pos,window.get_size()),
                            snapshot,config,level,plant_types)
            elif event.type==pygame.MOUSEBUTTONUP and event.button==1 and drag_state is not None:
                point=logical_position(event.pos,window.get_size())
                update_drag(drag_state,point,snapshot,config,level,plant_types)
                commands.extend(finish_drag(drag_state,point,snapshot['phase'],config,level,snapshot,plant_types))
                drag_state=None
        # Retain the originating session, so a restart cannot apply old board input.
        base_sequence=len(pending_commands)
        pending_commands.extend(Command(c.kind,c.args,game.session_id,None,base_sequence+i)
                                for i,c in enumerate(commands))
        if pending_commands and game.phase!="playing":
            _,events=game.step(pending_commands)
            pending_events.extend(events)
            pending_commands.clear()
        if game.phase=="playing":
            accumulated+=elapsed
            steps=0
            while accumulated>=1/60 and steps<5:
                _,events=game.step(pending_commands)
                pending_commands.clear()
                pending_events.extend(events)
                for result in game.results:
                    if result["reason"] in MESSAGES:
                        message=MESSAGES[result["reason"]]
                        message_until=now+2.5
                accumulated-=1/60
                steps+=1
                if game.phase!="playing": break
            if steps==5: accumulated=0
        else:
            accumulated=0
        mouse=logical_position(pygame.mouse.get_pos(),window.get_size())
        if drag_state is not None:
            update_drag(drag_state,mouse,game.snapshot(),config,level,plant_types)
        if game.phase!="playing":drag_state=None
        canvas=renderer.draw(game.snapshot(),pending_events,mouse,help_open,message,message_until-now,skins_open,drag_state)
        pending_events.clear()
        window.fill((24,40,28))
        w,h=window.get_size()
        scale=min(w/LOGICAL_WIDTH,h/LOGICAL_HEIGHT)
        size=(max(1,int(LOGICAL_WIDTH*scale)),max(1,int(LOGICAL_HEIGHT*scale)))
        image=pygame.transform.smoothscale(canvas,size)
        window.blit(image,((w-size[0])//2,(h-size[1])//2))
        pygame.display.flip()
        presented=time.perf_counter()
        if pending_motion_time is not None:
            if drag_state is not None:
                latency_samples.append((presented-pending_motion_time)*1000)
            pending_motion_time=None
        frames+=1
        if smoke_frames and frames>=smoke_frames:
            if screenshot:
                pygame.image.save(window,str(screenshot))
            break
        if input_latency and presented>=latency_deadline:
            ordered=sorted(latency_samples)
            p95=ordered[min(len(ordered)-1,max(0,math.ceil(.95*len(ordered))-1))] if ordered else None
            try:refresh_rate=pygame.display.get_current_refresh_rate()
            except (AttributeError,pygame.error):refresh_rate=None
            try:display_size=pygame.display.get_desktop_sizes()[0]
            except (AttributeError,IndexError,pygame.error):display_size=None
            result=dict(measurement='drag-preview-input-to-flip',samples=len(ordered),p95_ms=round(p95,2) if p95 is not None else None,
                        target_p95_ms=50,window_size=list(window.get_size()),display_size=list(display_size) if display_size else None,
                        refresh_rate_hz=refresh_rate,machine=platform.platform(),measured_at=time.strftime('%Y-%m-%d %H:%M:%S'))
            result['status']='PASS' if len(ordered)>=200 and p95 is not None and p95<=50 else 'INCONCLUSIVE' if len(ordered)<200 else 'FAIL'
            print('INPUT_LATENCY_JSON='+json.dumps(result,ensure_ascii=False),flush=True)
            break
        clock.tick(60)
    pygame.quit()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--smoke-frames",type=int,default=0)
    parser.add_argument("--screenshot",type=Path)
    parser.add_argument("--smoke-play",action="store_true")
    parser.add_argument('--plant-skin',choices=['default','dogs'],default='default')
    parser.add_argument('--zombie-skin',choices=['default','dogs'],default='default')
    parser.add_argument('--smoke-skins',action='store_true')
    parser.add_argument('--input-latency',action='store_true',help='measure real drag preview event-to-display latency')
    parser.add_argument('--benchmark-scene',choices=('standard','pressure'))
    parser.add_argument('--benchmark-output',type=Path)
    parser.add_argument('--seconds',type=float,default=60,help='measurement duration for --input-latency')
    parser.add_argument('--window-size',default='1260x720',help='initial window size, e.g. 1920x1080')
    args=parser.parse_args()
    if args.seconds<=0:parser.error('--seconds must be positive')
    try:
        window_size=tuple(int(part) for part in args.window_size.lower().split('x'))
        if len(window_size)!=2 or min(window_size)<=0:raise ValueError
    except ValueError:
        parser.error('--window-size must be WIDTHxHEIGHT with positive integers')
    try:
        if args.benchmark_scene:
            benchmark_window(args.benchmark_scene,args.seconds,args.benchmark_output)
            return
        run(args.smoke_frames,args.screenshot,args.smoke_play,args.plant_skin,args.zombie_skin,args.smoke_skins,
            args.input_latency,args.seconds,window_size)
    except Exception as exc:
        from .resources import error_logger
        # Deliberately omit traceback/full user paths from persistent logs.
        error_logger().error("Startup/runtime error: %s",type(exc).__name__)
        message="游戏未能正常运行，请确认已经完整解压并保留全部文件。\n" + str(exc)
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(None,message,"草坪保卫战 · 提示",0x10)
        except Exception:
            print(message)
        raise SystemExit(1) from None
