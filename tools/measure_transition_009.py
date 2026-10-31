"""Measure click-to-first-presented scene frames in the real window."""
import json
import sys
import time
from pathlib import Path

import pygame

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from pvz_game import app
from pvz_game.presentation.renderer import Renderer


def trial(mode):
    state={"mode":mode,"frames":0,"start":None,"open_start":None,
           "select_start":None,"open_target":False,"select_target":False,
           "skin_ready_target":False,"start_target":False,"start_ms":None,
           "open_ms":None,"select_ms":None,"skin_ready_ms":None}
    event_get,flip,original_draw=pygame.event.get,pygame.display.flip,Renderer.draw

    def events():
        state["frames"]+=1
        result=event_get()
        if mode=="start" and state["frames"]==2:
            state["start"]=time.perf_counter()
            result.append(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                         {"button":1,"pos":(848,298)}))
        elif mode=="skin" and state["frames"]==2:
            state["open_start"]=time.perf_counter()
            result.append(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                         {"button":1,"pos":(848,373)}))
        elif mode=="skin" and state["frames"]==3:
            state["select_start"]=time.perf_counter()
            result.append(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                         {"button":1,"pos":(420,570)}))
        return result

    def draw_wrapper(renderer,snapshot,*args,**kwargs):
        skins_open=args[5] if len(args)>5 else kwargs.get("skins_open",False)
        if mode=="start" and state["start"] is not None and snapshot["phase"]=="playing":
            state["start_target"]=True
        if mode=="skin" and skins_open and state["open_start"] is not None:
            state["open_target"]=True
        if (mode=="skin" and skins_open and state["select_start"] is not None
                and (renderer.appearance.plant_skin_id=="dogs_photo"
                     or renderer.appearance.pending_for('plant')=="dogs_photo")):
            state["select_target"]=True
        if (mode=="skin" and state["select_start"] is not None
                and renderer.appearance.plant_skin_id=="dogs_photo"):
            state["skin_ready_target"]=True
        return original_draw(renderer,snapshot,*args,**kwargs)

    def measured_flip():
        flip()
        now=time.perf_counter()
        if state["start_target"] and state["start_ms"] is None:
            state["start_ms"]=(now-state["start"])*1000
        if state["open_target"] and state["open_ms"] is None:
            state["open_ms"]=(now-state["open_start"])*1000
        if state["select_target"] and state["select_ms"] is None:
            state["select_ms"]=(now-state["select_start"])*1000
        if state["skin_ready_target"] and state["skin_ready_ms"] is None:
            state["skin_ready_ms"]=(now-state["select_start"])*1000

    pygame.event.get=events
    pygame.display.flip=measured_flip
    Renderer.draw=draw_wrapper
    try:
        if mode=="start":
            app.run(smoke_frames=5,plant_skin="dogs_photo",zombie_skin="dogs")
        else:
            app.run(smoke_frames=90)
    finally:
        pygame.event.get=event_get
        pygame.display.flip=flip
        Renderer.draw=original_draw
    return {key:round(state[key],2) if state[key] is not None else None
            for key in ("start_ms","open_ms","select_ms","skin_ready_ms")}


results={"method":"perf_counter at injected mouse-down to display.flip after the matching Renderer.draw; real Windows display",
         "start_trials":[],"skin_trials":[]}
for _ in range(5):results["start_trials"].append(trial("start"))
for _ in range(5):results["skin_trials"].append(trial("skin"))
results['measured_at']=time.strftime('%Y-%m-%d %H:%M:%S')
output=ROOT/'docs'/'validation'/'009'/'transition-check.json'
output.write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(results,ensure_ascii=False,indent=2))
