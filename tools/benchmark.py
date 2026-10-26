"""Measure the rendered worst-case scene and cold menu startup."""
from __future__ import annotations

import argparse
import json
import math
import os
import platform
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))


from pvz_game.presentation.performance import make_scene


def cold_start_seconds():
    env=dict(os.environ)
    env['SDL_VIDEODRIVER']='dummy'
    env['SDL_AUDIODRIVER']='dummy'
    start=time.perf_counter()
    subprocess.run([sys.executable,'-m','pvz_game','--smoke-frames','1'],
                   cwd=ROOT,env=env,check=True,timeout=10,
                   stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return time.perf_counter()-start


def benchmark(seconds):
    import pygame
    from pvz_game.config import load
    from pvz_game.presentation.renderer import Renderer
    from pvz_game.presentation.skin_catalog import AppearanceController,Catalog

    config,level=load()
    pygame.display.init()
    pygame.font.init()
    window=pygame.display.set_mode((1050,600))
    appearance=AppearanceController(Catalog())
    appearance.select('plant','dogs','menu')
    appearance.select('zombie','dogs','menu')
    renderer=Renderer(config,appearance)
    snapshot=make_scene(config,level)
    frame_ms=[]
    sampled_ticks=set()
    clock=pygame.time.Clock()
    benchmark_start=time.perf_counter()
    deadline=benchmark_start+seconds
    while time.perf_counter()<deadline:
        started=time.perf_counter()
        snapshot['tick']=int((started-benchmark_start)*config['tick_hz'])
        sampled_ticks.add(snapshot['tick'])
        canvas=renderer.draw(snapshot)
        window.blit(canvas,(0,0))
        pygame.display.flip()
        clock.tick(60)
        frame_ms.append((time.perf_counter()-started)*1000)
    pygame.quit()
    frame_ms.sort()
    total=sum(frame_ms)/1000
    frames=len(frame_ms)
    return dict(frames=frames,elapsed_seconds=round(total,3),
                average_fps=round(frames/total,2),
                p95_frame_ms=round(frame_ms[min(len(frame_ms)-1,math.ceil(.95*len(frame_ms))-1)],2),
                animation_samples_per_second=round(len(sampled_ticks)/total,2),
                simulation_hz=config['tick_hz'],
                target_render_fps=60,target_animation_hz=30,
                pygame=pygame.version.ver)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--seconds',type=float,default=60)
    parser.add_argument('--input-latency',action='store_true',help='measure verified real plant, shovel and sun actions')
    parser.add_argument('--window',action='store_true',help='measure the actual display and presentation path')
    parser.add_argument('--scene',choices=('standard','pressure'),default='pressure')
    parser.add_argument('--plant-skin',choices=('default','dogs','dogs_photo'),default='dogs')
    parser.add_argument('--zombie-skin',choices=('default','dogs'),default='dogs')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    if args.seconds<=0:parser.error('--seconds must be positive')
    if args.input_latency:
        result=subprocess.run([sys.executable,'-m','pvz_game','--input-latency','--seconds',str(args.seconds)],
                              cwd=ROOT,capture_output=True,text=True)
        if result.stdout:print(result.stdout,end='')
        if result.stderr:print(result.stderr,end='',file=sys.stderr)
        if result.returncode:raise SystemExit(result.returncode)
        report=next((line.partition('=')[2] for line in result.stdout.splitlines()
                     if line.startswith('INPUT_LATENCY_JSON=')),None)
        if report is None:raise SystemExit('No input latency report was produced.')
        if json.loads(report).get('status')!='PASS':raise SystemExit('Real-window latency sample set is incomplete or above target.')
        return
    if args.window:
        command=[sys.executable,'-m','pvz_game','--benchmark-scene',args.scene,
             '--seconds',str(args.seconds),'--benchmark-plant-skin',args.plant_skin,
             '--benchmark-zombie-skin',args.zombie_skin]
        if args.output:command.extend(['--benchmark-output',str(args.output.resolve())])
        raise SystemExit(subprocess.run(command,cwd=ROOT).returncode)
    startup=cold_start_seconds()
    result=benchmark(args.seconds)
    result.update(startup_seconds=round(startup,3),machine=platform.platform(),
                  processor=platform.processor() or 'unknown',
                  cpu_count=os.cpu_count(),python=platform.python_version(),display_driver='SDL dummy',
                  scene=dict(canvas='1050x600',plants=45,zombies=30,projectiles=100,suns=20),
                  measured_at=time.strftime('%Y-%m-%d %H:%M:%S'))
    print(result)
    if result['average_fps']<55 or result['p95_frame_ms']>33 or startup>=10:
        raise SystemExit('Performance target not met; see measured values above.')


if __name__=='__main__':
    main()
