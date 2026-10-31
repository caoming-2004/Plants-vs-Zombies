"""Measure ten menu-to-board transitions in the real display loop."""
import json
import time
from pathlib import Path
import pygame
from pvz_game import app

samples=[]
for iteration in range(10):
    original_get=pygame.event.get
    original_flip=pygame.display.flip
    state={'frames':0,'started':None,'elapsed':None,'board_elapsed':None}

    def events():
        result=original_get()
        state['frames']+=1
        if state['frames']==2:
            state['started']=time.perf_counter()
            result.append(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                       {'button':1,'pos':(840,296)}))
        return result

    def flip():
        original_flip()
        if state['started'] is not None:
            measured=(time.perf_counter()-state['started'])*1000
            if state['elapsed'] is None:state['elapsed']=measured
            elif state['board_elapsed'] is None:state['board_elapsed']=measured

    pygame.event.get=events
    pygame.display.flip=flip
    try:
        app.run(smoke_frames=3,plant_skin='dogs_photo',zombie_skin='dogs',
                screenshot=Path('docs/validation/007/start-after-click.png') if iteration==0 else None)
    finally:
        pygame.event.get=original_get
        pygame.display.flip=original_flip
    samples.append({'feedback_ms':round(state['elapsed'],2),
                    'board_ms':round(state['board_elapsed'],2)})

print(json.dumps(samples))
