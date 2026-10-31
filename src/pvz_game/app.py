import argparse
import json
import math
import os
import platform
import time
from pathlib import Path

from .resources import log_exception


def clamp_window_size(size):
    from .config import LOGICAL_WIDTH, LOGICAL_HEIGHT
    return max(LOGICAL_WIDTH,size[0]),max(LOGICAL_HEIGHT,size[1])


def benchmark_window(scene, seconds, output=None, plant_skin='dogs', zombie_skin='dogs',
                     baseline_average_fps=None):
    """Measure the real display path used by the packaged game."""
    import pygame
    from .config import load, LOGICAL_WIDTH, LOGICAL_HEIGHT
    from .presentation.renderer import Renderer
    from .presentation.skin_catalog import Catalog, AppearanceController
    from .presentation.performance import (make_scene, make_simulation,
                                           summarize_frame_intervals, SCENES)
    from .presentation.window_scaling import present_canvas

    if seconds <= 0:
        raise ValueError("Benchmark duration must be positive")
    config, level = load()
    pygame.display.init()
    pygame.font.init()
    window = pygame.display.set_mode((1260, 720), pygame.RESIZABLE)
    pygame.display.set_caption("草坪保卫战 · 实机性能测量")
    appearance = AppearanceController(Catalog())
    appearance.select("plant", plant_skin, "menu")
    appearance.select("zombie", zombie_skin, "menu")
    renderer = Renderer(config, appearance)
    snapshot = make_scene(config, level, scene)
    simulation = make_simulation(config, level, scene)
    clock = pygame.time.Clock()
    scaled_window_surface = None
    scaled_window_size = None
    started = previous = time.perf_counter()
    intervals = []
    stage_samples = {
        name: [] for name in (
            "event_processing_ms", "simulation_step_ms", "scene_update_ms", "renderer_ms",
            "window_scaling_ms", "display_flip_ms", "frame_pacing_ms",
        )
    }
    try:
        while time.perf_counter() - started < seconds:
            frame_started = time.perf_counter()
            stage_started = frame_started
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise RuntimeError("Benchmark interrupted before 60 seconds")
            now = time.perf_counter()
            stage_samples["event_processing_ms"].append((now - stage_started) * 1000)
            stage_started = now
            simulation.step(include_snapshot=False)
            now = time.perf_counter()
            stage_samples["simulation_step_ms"].append((now - stage_started) * 1000)
            stage_started = now
            snapshot["tick"] = int((time.perf_counter() - started) * config["tick_hz"])
            stage_samples["scene_update_ms"].append(
                (time.perf_counter() - stage_started) * 1000
            )
            stage_started = time.perf_counter()
            canvas = renderer.draw(snapshot)
            now = time.perf_counter()
            stage_samples["renderer_ms"].append((now - stage_started) * 1000)
            stage_started = now
            scaled_window_surface, scaled_window_size = present_canvas(
                window, canvas, scaled_window_surface, scaled_window_size)
            now = time.perf_counter()
            stage_samples["window_scaling_ms"].append((now - stage_started) * 1000)
            stage_started = now
            pygame.display.flip()
            now = time.perf_counter()
            stage_samples["display_flip_ms"].append((now - stage_started) * 1000)
            pace_started = time.perf_counter()
            clock.tick_busy_loop(60)
            stage_samples["frame_pacing_ms"].append((time.perf_counter() - pace_started) * 1000)
            now = time.perf_counter()
            intervals.append((now - previous) * 1000)
            previous = now
        report = summarize_frame_intervals(intervals)
        for name, samples in stage_samples.items():
            ordered = sorted(samples)
            report[name] = dict(
                mean=round(sum(samples) / len(samples), 3),
                p95=round(ordered[math.ceil(.95 * len(ordered)) - 1], 3),
                max=round(ordered[-1], 3),
            )
        try:
            refresh_rate = pygame.display.get_current_refresh_rate()
        except (AttributeError, pygame.error):
            refresh_rate = None
        try:
            display_size = pygame.display.get_desktop_sizes()[0]
        except (AttributeError, IndexError, pygame.error):
            display_size = None
        report.update(scene=scene, load=SCENES[scene], machine=platform.platform(),
                      os=platform.platform(), window_size=list(window.get_size()),
                      display_size=list(display_size) if display_size else None,
                      display_driver=pygame.display.get_driver(),
                      refresh_rate_hz=refresh_rate,
                      plant_skin=plant_skin,zombie_skin=zombie_skin,
                      measurement_scope="deterministic render scene plus fixed-load Simulation.step",
                      baseline_average_fps=baseline_average_fps,
                      measured_at=time.strftime("%Y-%m-%d %H:%M:%S"))
        report["average_fps_vs_baseline_pct"] = (
            round(report["average_fps"] / baseline_average_fps * 100, 2)
            if baseline_average_fps and baseline_average_fps > 0 else None
        )
        report["acceptance"] = dict(
            average_fps=(report["average_fps"] >= 58 if scene == "standard" else None),
            average_fps_vs_baseline=(
                report["average_fps_vs_baseline_pct"] >= 97
                if scene == "standard" and report["average_fps_vs_baseline_pct"] is not None
                else None
            ),
            p95_frame_ms=report["p95_frame_ms"] <= (18 if scene == "standard" else 20),
            slow_frame_run=report["longest_over_33ms_run"] < 2,
        )
        gates = [report["acceptance"]["p95_frame_ms"],
                 report["acceptance"]["slow_frame_run"]]
        if scene == "standard":
            gates.append(report["acceptance"]["average_fps"])
            if report["acceptance"]["average_fps_vs_baseline"] is None:
                report["acceptance"]["status"] = "INCONCLUSIVE"
            else:
                gates.append(report["acceptance"]["average_fps_vs_baseline"])
                report["acceptance"]["status"] = "PASS" if all(gates) else "FAIL"
        else:
            report["acceptance"]["status"] = "PASS" if all(gates) else "FAIL"
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
    from .config import load_campaign
    from .config import LOGICAL_WIDTH, LOGICAL_HEIGHT
    from .progress import Progress
    from .domain import campaign as campaign_rules
    from .domain.endless import make_level as make_endless_level
    from .domain.simulation import Simulation
    from .domain.commands import Command
    from .presentation.renderer import Renderer
    from .presentation.audio import AudioController
    from .presentation.window_scaling import present_canvas
    from .presentation.input import (click, logical_position, card_at, begin_drag,
                                     update_drag, finish_drag, inside)
    from .presentation.scenes import MESSAGES, BUTTONS
    from .presentation.skin_catalog import Catalog, AppearanceController
    from .platforms.android.touch import TouchEventAdapter

    config,campaign,levels=load_campaign()
    progress=Progress.load()
    selected_level_id=campaign["stages"][0]
    level=levels[selected_level_id]
    pygame.display.init()
    pygame.font.init()
    is_android=bool(os.environ.get("ANDROID_ARGUMENT"))
    window=(pygame.display.set_mode((0,0),pygame.FULLSCREEN) if is_android else
            pygame.display.set_mode(clamp_window_size(window_size),pygame.RESIZABLE))
    pygame.display.set_caption("植物大战僵尸小游戏 · 经典与小狗换肤")
    appearance=AppearanceController(Catalog())
    appearance.select('plant',plant_skin,'menu')
    appearance.select('zombie',zombie_skin,'menu')
    renderer=Renderer(config,appearance)
    audio=AudioController(progress.music_enabled,progress.music_volume)
    renderer.set_background(progress.background_id)
    if renderer.backgrounds.resolve(progress.background_id) != progress.background_id:
        progress.set_background(renderer.background_id)
        progress.save()
    plant_types={item['id']:item for item in config['plant_types']}
    icon=pygame.Surface((48,48))
    icon.fill((98,150,76))
    pygame.draw.circle(icon,(252,199,62),(24,24),18)
    pygame.draw.circle(icon,(145,88,38),(24,24),11)
    pygame.display.set_icon(icon)
    game=Simulation(config,level)
    menu_view="main"
    result_stars=[]
    next_level_id=None
    recorded_session=None
    if smoke_play:
        game.step([Command("Start")])
        menu_view="playing"
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
    if smoke_play:
        skins_open=False
    message=""
    message_until=0
    if progress.recovered:
        message="进度文件损坏或不可读，已回到初始进度"
        message_until=time.perf_counter()+4.0
    if renderer.backgrounds.error:
        message="背景资源不可用，已使用默认背景"
        message_until=time.perf_counter()+4.0
    frames=0
    pending_events=[]
    pending_commands=[]
    drag_state=None
    latency_deadline=time.perf_counter()+latency_seconds if input_latency else None
    feedback_attempts=[]
    feedback_for_flip=[]
    feedback_samples=[]
    feedback_missing=0
    feedback_duplicates=0
    feedback_ids=0
    scaled_window_surface=None
    scaled_window_size=None
    feedback_event_for_command={
        'PlantAt':'planted',
        'ShovelAt':'removed',
        'CollectSun':'collected',
    }
    skins_prefetched=False
    touch_adapter=TouchEventAdapter(pygame,android=is_android)

    def observe_commands(batch):
        nonlocal feedback_ids
        if not input_latency:return
        observed=time.perf_counter()
        for command in batch:
            event_kind=feedback_event_for_command.get(command.kind)
            if event_kind is not None:
                feedback_ids+=1
                feedback_attempts.append(dict(
                    id=feedback_ids,
                    command=command.kind,
                    event=event_kind,
                    args=command.args,
                    started=observed,
                ))

    def observe_step(events,results):
        nonlocal feedback_missing,feedback_duplicates
        if not input_latency:return
        available=list(events)
        for attempt in list(feedback_attempts):
            matches=[]
            for index,event in enumerate(available):
                if event['kind']!=attempt['event']:
                    continue
                args=attempt['args']
                if attempt['command']=='CollectSun' and event['id']==args[0]:
                    matches.append(index)
                elif attempt['command'] in ('PlantAt','ShovelAt') and (
                    event['row'],event['col']
                )==args:
                    matches.append(index)
            if matches:
                if len(matches)>1:feedback_duplicates+=len(matches)-1
                matched=available.pop(matches[0])
                feedback_attempts.remove(attempt)
                attempt['matched_event_seq']=matched['event_seq']
                feedback_for_flip.append(attempt)
                continue
            rejection=next((result for result in results
                            if result['command']==attempt['command']
                            and not result['accepted']),None)
            if rejection is not None:
                feedback_missing+=1
                feedback_attempts.remove(attempt)

    def start_level(level_id):
        nonlocal game, level, selected_level_id, menu_view, result_stars, next_level_id, recorded_session
        if level_id not in levels:
            return
        try:
            level=levels[level_id]
            selected_level_id=level_id
            game=Simulation(config,level)
            game.step([Command("Start")])
        except Exception:
            log_exception("failed to start level " + str(level_id))
            message="关卡加载失败，请返回菜单重试"
            message_until=now+4.0
            return
        menu_view="playing"
        result_stars=[]
        next_level_id=None
        recorded_session=None
        pending_commands.clear()
        pending_events.clear()
        drag_state=None
        skins_open=False
        help_open=False

    def start_endless():
        nonlocal game, level, selected_level_id, menu_view, result_stars, next_level_id, recorded_session
        try:
            level=make_endless_level(campaign)
            selected_level_id="endless"
            game=Simulation(config,level)
            game.step([Command("Start")])
        except Exception:
            log_exception("failed to start endless")
            message="无尽模式加载失败，请返回菜单重试"
            message_until=now+4.0
            return
        menu_view="playing"
        result_stars=[]
        next_level_id=None
        recorded_session=None
        pending_commands.clear()
        pending_events.clear()
        drag_state=None
        skins_open=False
        help_open=False

    def refresh_result():
        nonlocal result_stars, next_level_id, recorded_session, message, message_until
        try:
            if game.phase=="won" and recorded_session!=game.session_id:
                stats=game.run_stats()
                result_stars=campaign_rules.evaluate_stars(level,stats)
                progress.record_win(selected_level_id,campaign["stages"],len(result_stars),stats["elapsed_ticks"])
                progress.save()
                recorded_session=game.session_id
                next_level_id=campaign_rules.next_stage(campaign,selected_level_id)
            elif game.phase=="lost":
                if selected_level_id=="endless" and recorded_session!=game.session_id:
                    snap=game.snapshot()
                    progress.record_endless(snap["wave_index"],snap["kills"])
                    progress.save()
                    recorded_session=game.session_id
                result_stars=[]
                next_level_id=None
        except Exception:
            log_exception("result flow failed")
            message="结算保存失败，但可以返回菜单或重试"
            message_until=time.perf_counter()+4.0

    while game.phase!="quit":
        now=time.perf_counter()
        elapsed=min(now-last,.25)
        last=now
        commands=[]
        snapshot=game.snapshot()
        audio.update(game.phase if menu_view == "playing" or game.phase != "menu" else "menu")
        for raw_event in pygame.event.get():
            event=touch_adapter.translate(raw_event,window.get_size())
            if event is None:continue
            if event.type==pygame.QUIT:
                commands.append(Command("Quit"))
            elif event.type in (pygame.WINDOWRESIZED,pygame.VIDEORESIZE):
                requested_size=(event.x,event.y) if event.type==pygame.WINDOWRESIZED else (event.w,event.h)
                width,height=clamp_window_size(requested_size)
                if not is_android and (width,height)!=requested_size:
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
            elif (event.type==pygame.WINDOWFOCUSLOST or
                  event.type==getattr(pygame,"WINDOWHIDDEN",-1)) and game.phase=="playing":
                drag_state=None
                commands.append(Command("Pause"))
            elif event.type==pygame.MOUSEBUTTONDOWN:
                point=logical_position(event.pos,window.get_size())
                if event.button==3:
                    drag_state=None
                if event.button==1 and game.phase=="playing":
                    card=card_at(point,appearance.plant_skin_id,level)
                    if card is not None or point is not None and inside(point,BUTTONS["shovel"]):
                        drag_state=begin_drag(card if card is not None else "shovel",point)
                        continue
                result=click(point,snapshot,config,help_open,event.button,skins_open,
                             appearance.plant_skin_id,view=menu_view,level=level)
                if result=="open_help": help_open=True
                elif result=="close_help":help_open=False
                elif result=='open_skins':skins_open=True
                elif result=='close_skins':skins_open=False
                elif result=="close_levels":menu_view="main"
                elif result=="open_backgrounds":
                    menu_view="backgrounds"
                    skins_open=False
                    help_open=False
                elif result=="close_backgrounds":menu_view="main"
                elif result=="toggle_music":
                    progress.set_music_enabled(not progress.music_enabled)
                    progress.save()
                    audio.set_enabled(progress.music_enabled)
                    audio.update("menu")
                elif result in ("music_volume_down", "music_volume_up"):
                    change=-0.1 if result=="music_volume_down" else 0.1
                    progress.set_music_volume(progress.music_volume+change)
                    progress.save()
                    audio.set_volume(progress.music_volume)
                elif isinstance(result,str) and result.startswith('select_background_'):
                    index=int(result.removeprefix('select_background_'))-1
                    if 0<=index<len(renderer.backgrounds.order):
                        background_id=renderer.backgrounds.order[index]
                        renderer.set_background(background_id)
                        progress.set_background(background_id)
                        progress.save()
                        message="背景已切换"
                        message_until=now+2.0
                elif isinstance(result,str) and result.startswith('select_stage_'):
                    index=int(result.removeprefix('select_stage_'))-1
                    stages=campaign["stages"]
                    if 0<=index<len(stages):
                        stage_id=stages[index]
                        if progress.is_unlocked(stage_id):
                            start_level(stage_id)
                        else:
                            message=MESSAGES.get("locked","请先通关前一关")
                            message_until=now+2.5
                elif result=="select_endless":
                    if progress.endless_unlocked:
                        start_endless()
                    else:
                        message=MESSAGES.get("endless_locked","请先通关最后一关")
                        message_until=now+2.5
                elif result=="next_level":
                    if next_level_id:
                        start_level(next_level_id)
                    else:
                        menu_view="levels"
                elif isinstance(result,str) and result.startswith('preview_role_'):
                    renderer.focus_role_preview(result.removeprefix('preview_role_'))
                elif isinstance(result,str) and result.startswith('choose_'):
                    side,_,skin=result.removeprefix('choose_').partition('_')
                    appearance.select_async(side,skin,game.phase)
                elif isinstance(result,Command):
                    if result.kind=="Start":
                        menu_view="levels"
                        continue
                    if result.kind in ('Start','Restart'):
                        key='start' if result.kind=='Start' else 'restart'
                        bx,by,bw,bh=BUTTONS[key]
                        ww,wh=window.get_size()
                        button_scale=min(ww/LOGICAL_WIDTH,wh/LOGICAL_HEIGHT)
                        ox=(ww-LOGICAL_WIDTH*button_scale)/2
                        oy=(wh-LOGICAL_HEIGHT*button_scale)/2
                        pygame.draw.rect(window,(255,232,133),pygame.Rect(
                            round(ox+bx*button_scale),round(oy+by*button_scale),
                            round(bw*button_scale),round(bh*button_scale)),3)
                        pygame.display.flip()
                        appearance.on_restart()
                    if result.kind=="Restart":
                        menu_view="playing"
                        result_stars=[]
                        next_level_id=None
                    if result.kind=="ReturnToMenu":
                        menu_view="main"
                        result_stars=[]
                        next_level_id=None
                    if result.kind in ('Pause','Restart','ReturnToMenu','Quit'):
                        drag_state=None
                    commands.append(result)
            elif event.type==pygame.MOUSEMOTION and drag_state is not None:
                update_drag(drag_state,logical_position(event.pos,window.get_size()),
                            snapshot,config,level,plant_types)
            elif event.type==pygame.MOUSEBUTTONUP and event.button==1 and drag_state is not None:
                point=logical_position(event.pos,window.get_size())
                update_drag(drag_state,point,snapshot,config,level,plant_types)
                released=finish_drag(drag_state,point,snapshot['phase'],config,level,
                                     snapshot,plant_types,appearance.plant_skin_id)
                commands.extend(released)
                if not released and drag_state.reason_code:
                    message=MESSAGES.get(drag_state.reason_code,drag_state.reason_code)
                    message_until=now+2.5
                drag_state=None
        appearance.poll_pending()
        # Retain the originating session, so a restart cannot apply old board input.
        base_sequence=len(pending_commands)
        pending_commands.extend(Command(c.kind,c.args,game.session_id,None,base_sequence+i)
                                for i,c in enumerate(commands))
        observe_commands(commands)
        if pending_commands and game.phase!="playing":
            _,events=game.step(pending_commands,include_snapshot=False)
            observe_step(events,game.results)
            pending_events.extend(events)
            pending_commands.clear()
        if game.phase=="playing":
            accumulated+=elapsed
            steps=0
            while accumulated>=1/60 and steps<5:
                _,events=game.step(pending_commands,include_snapshot=False)
                observe_step(events,game.results)
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
        refresh_result()
        mouse=logical_position(pygame.mouse.get_pos(),window.get_size())
        if drag_state is not None:
            update_drag(drag_state,mouse,game.snapshot(),config,level,plant_types)
        if game.phase!="playing":drag_state=None
        canvas=renderer.draw(game.snapshot(),pending_events,mouse,help_open,message,message_until-now,skins_open,drag_state,
                             level=level,campaign=campaign,levels=levels,progress=progress,
                             preview=game.wave_preview() if game.phase!="menu" else None,
                             result_stars=result_stars,next_level_id=next_level_id,
                             level_select_open=(menu_view=="levels"),
                             backgrounds_open=(menu_view=="backgrounds"))
        pending_events.clear()
        scaled_window_surface,scaled_window_size=present_canvas(
            window,canvas,scaled_window_surface,scaled_window_size)
        pygame.display.flip()
        if skins_open and not skins_prefetched:
            for skin_id in ('dogs','dogs_photo'):
                if renderer.catalog.installed(skin_id):renderer.catalog.preload_async(skin_id)
            skins_prefetched=True
        presented=time.perf_counter()
        for attempt in feedback_for_flip:
            feedback_samples.append(dict(
                operation=attempt['command'],
                latency_ms=round((presented-attempt['started'])*1000,2),
                event_seq=attempt['matched_event_seq'],
            ))
        feedback_for_flip.clear()
        frames+=1
        if smoke_frames and frames>=smoke_frames:
            if screenshot:
                pygame.image.save(window,str(screenshot))
            break
        if input_latency and presented>=latency_deadline:
            feedback_missing+=len(feedback_attempts)
            feedback_attempts.clear()
            ordered=sorted(sample['latency_ms'] for sample in feedback_samples)
            p95=ordered[min(len(ordered)-1,max(0,math.ceil(.95*len(ordered))-1))] if ordered else None
            try:refresh_rate=pygame.display.get_current_refresh_rate()
            except (AttributeError,pygame.error):refresh_rate=None
            try:display_size=pygame.display.get_desktop_sizes()[0]
            except (AttributeError,IndexError,pygame.error):display_size=None
            result=dict(measurement='verified-action-to-visible-flip',samples=len(ordered),p95_ms=round(p95,2) if p95 is not None else None,
                        target_p95_ms=100,missing_actions=feedback_missing,duplicate_events=feedback_duplicates,
                        sample_details=feedback_samples,
                        operations={kind:sum(sample['operation']==kind for sample in feedback_samples)
                                    for kind in ('PlantAt','ShovelAt','CollectSun')},
                        window_size=list(window.get_size()),display_size=list(display_size) if display_size else None,
                        refresh_rate_hz=refresh_rate,display_driver=pygame.display.get_driver(),
                        os=platform.platform(),machine=platform.platform(),
                        measured_at=time.strftime('%Y-%m-%d %H:%M:%S'))
            result['status']=('PASS' if len(ordered)>=20 and p95 is not None and p95<=100
                              and feedback_missing==0 and feedback_duplicates==0
                              else 'INCONCLUSIVE' if len(ordered)<20 else 'FAIL')
            print('INPUT_LATENCY_JSON='+json.dumps(result,ensure_ascii=False),flush=True)
            break
        clock.tick_busy_loop(60)
    pygame.quit()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--smoke-frames",type=int,default=0)
    parser.add_argument("--screenshot",type=Path)
    parser.add_argument("--smoke-play",action="store_true")
    parser.add_argument('--plant-skin',choices=['default','dogs','dogs_photo'],default='default')
    parser.add_argument('--zombie-skin',choices=['default','dogs'],default='default')
    parser.add_argument('--smoke-skins',action='store_true')
    parser.add_argument('--input-latency',action='store_true',help='measure verified real interaction event-to-display latency')
    parser.add_argument('--benchmark-scene',choices=('standard','pressure'))
    parser.add_argument('--benchmark-plant-skin',choices=('default','dogs','dogs_photo'),default='dogs')
    parser.add_argument('--benchmark-zombie-skin',choices=('default','dogs'),default='dogs')
    parser.add_argument('--benchmark-output',type=Path)
    parser.add_argument('--baseline-average-fps',type=float,
                        help='same-condition first-version standard loop FPS baseline')
    parser.add_argument('--seconds',type=float,default=60,help='measurement duration for --input-latency')
    parser.add_argument('--window-size',default='1260x720',help='initial window size, e.g. 1920x1080')
    args=parser.parse_args()
    if args.seconds<=0:parser.error('--seconds must be positive')
    if args.baseline_average_fps is not None and args.baseline_average_fps<=0:
        parser.error('--baseline-average-fps must be positive')
    try:
        window_size=tuple(int(part) for part in args.window_size.lower().split('x'))
        if len(window_size)!=2 or min(window_size)<=0:raise ValueError
    except ValueError:
        parser.error('--window-size must be WIDTHxHEIGHT with positive integers')
    try:
        if args.benchmark_scene:
            benchmark_window(args.benchmark_scene,args.seconds,args.benchmark_output,
                             args.benchmark_plant_skin,args.benchmark_zombie_skin,
                             args.baseline_average_fps)
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
