from copy import deepcopy
import pygame
import pytest
from pvz_game.config import load
from pvz_game.domain.simulation import Simulation
from pvz_game.domain.commands import Command
from pvz_game.presentation.skin_catalog import Catalog, AppearanceController
from pvz_game.presentation.animation import Animator
from test_base_replay import strategy


def run_case(catalog,selection,case):
    config,level=load()
    level=deepcopy(level)
    # Three reproducible arrangements exercise different rows and pacing.
    for spawn in level['spawn_schedule']:
        spawn['row']=(spawn['row']+case)%5
        spawn['tick']+=case*30
    appearance=AppearanceController(catalog)
    for side,skin in zip(('plant','zombie'),selection):assert appearance.select(side,skin,'menu')
    game=Simulation(config,level);game.step([Command('Start')])
    animator=Animator(appearance);surface=pygame.Surface((800,600),pygame.SRCALPHA)
    events=[]
    for _ in range(24000):
        snap,batch=game.step(strategy(game))
        events.extend(tuple(sorted(dict(e).items())) for e in batch)
        animator.consume(snap,batch)
        if game.tick%600==0:
            before=game.snapshot()
            for actor in list(snap['plants'])+list(snap['zombies']):
                animator.draw_actor(surface,actor,(200,200),game.tick)
            assert game.snapshot()==before
        if game.phase in ('won','lost'):
            old=appearance.selection()
            game.step([Command('Restart')]);appearance.on_restart()
            assert appearance.selection()==old
            assert all(m.state=='ready' for m in game.mowers)
            return events
    raise AssertionError('Level did not finish')


@pytest.mark.parametrize('case',[0,1,2])
def test_real_skin_combinations_have_identical_gameplay(case):
    catalog=Catalog()
    baseline=run_case(catalog,('default','default'),case)
    for selected in [('dogs','default'),('default','dogs'),('dogs','dogs')]:
        assert run_case(catalog,selected,case)==baseline
