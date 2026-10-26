import os
import pytest
from pvz_game.config import load
from pvz_game.domain.commands import Command
from pvz_game.domain.simulation import Simulation
from pvz_game.presentation.input import begin_drag, finish_drag, update_drag
from pvz_game.presentation.scenes import BUTTONS, HUD_SUN_RECT
from pvz_game.presentation.input import click, logical_position


def test_input_and_letterbox(game):
    config,_=load()
    assert logical_position((0,0),(1200,600)) is None
    assert logical_position((75,0),(1200,600)) == (0,0)
    assert logical_position((0,0),(1050,600)) == (0,0)
    assert logical_position((0,0),(1260,720)) == (0,0)
    assert logical_position((15,0),(1920,1080)) == (0,0)
    assert click((200,50),game.snapshot(),config).kind == "SelectPlant"
    game.add_sun(200,50,25)
    assert click((200,50),game.snapshot(),config).kind == "SelectPlant"
    game.add_sun(220,210,25)
    assert click((220,210),game.snapshot(),config).kind == "CollectSun"
    game.step([Command("Pause")])
    assert click((220,210),game.snapshot(),config) is None


def test_twelve_column_hit_testing_and_sun_hud_priority(game):
    config,_=load()
    game.phase="playing"
    point=(config["grid_x"]+11.5*config["cell_width"],
           config["grid_y"]+.5*config["cell_height"])
    command=click(point,game.snapshot(),config)
    assert command.kind=="PlantAt" and command.args==(0,11)
    assert click((config["grid_x"]+12*config["cell_width"],
                  config["grid_y"]+20),game.snapshot(),config) is None
    hx,hy,hw,hh=HUD_SUN_RECT
    game.add_sun(hx+hw/2,hy+hh/2,25)
    assert click((hx+hw/2,hy+hh/2),game.snapshot(),config) is None
    assert hx+hw < BUTTONS['sunflower'][0]
    assert click((960,50),game.snapshot(),config).kind=="Pause"


def test_window_minimum_size():
    from pvz_game.app import clamp_window_size
    assert clamp_window_size((800,500))==(1050,600)
    assert clamp_window_size((1200,700))==(1200,700)


def test_sun_hud_draws_over_world_pickups(monkeypatch,game):
    monkeypatch.setenv("SDL_VIDEODRIVER","dummy")
    import pygame
    from pvz_game.domain.models import Plant
    from pvz_game.presentation.renderer import Renderer
    pygame.display.init()
    pygame.font.init()
    pygame.display.set_mode((1,1))
    renderer=Renderer(game.config)
    game.phase="playing"
    for row in range(5):
        for col in range(12):
            entity_id=game.new_id()
            role="sunflower" if col%2==0 else "peashooter"
            game.plants[entity_id]=Plant(entity_id,role,row,col,300,0)
    for index in range(30):
        game.add_zombie(index%5,x=650+(index//5)*48)
    without_pickup=renderer.draw(game.snapshot()).copy()
    game.add_sun(40,40,25)
    with_pickup=renderer.draw(game.snapshot()).copy()
    hud_without=without_pickup.subsurface(HUD_SUN_RECT)
    hud_with=with_pickup.subsurface(HUD_SUN_RECT)
    assert all(hud_without.get_at((x,y))==hud_with.get_at((x,y))
               for x in range(hud_without.get_width())
               for y in range(hud_without.get_height()))
    pygame.display.quit()


def test_real_display_renderer_smoke(monkeypatch):
    monkeypatch.setenv("SDL_VIDEODRIVER","dummy")
    from pvz_game.app import run
    run(smoke_frames=2,smoke_play=True)


def test_resources_independent_of_cwd(tmp_path,monkeypatch):
    monkeypatch.chdir(tmp_path)
    c,l=load()
    assert c["initial_sun"]==150 and l["rows"]==5


def test_missing_resource_understandable():
    from pvz_game.resources import resource
    with pytest.raises(RuntimeError,match="资源缺失"):
        resource("missing.file")


def test_biting_removes_plant_then_walks(game):
    game.step([Command("SelectPlant",("sunflower",)),Command("PlantAt",(0,0),sequence=1)])
    p=next(iter(game.plants.values()))
    z=game.add_zombie(0,x=game.plant_x(p)+25)
    p.hp=20
    game.step()
    assert p.id not in game.plants
    before=z.x
    game.step()
    assert z.x<before and z.action=="walking"


@pytest.mark.parametrize('role',['sunflower','peashooter','wallnut','jalapeno'])
def test_click_and_drag_reach_same_planting_result(role):
    config,level=load()
    click_game=Simulation(config,level);drag_game=Simulation(config,level)
    click_game.step([Command('Start')]);drag_game.step([Command('Start')])
    card=BUTTONS[role];card_point=(card[0]+card[2]/2,card[1]+card[3]/2)
    lawn_point=(config['grid_x']+1.5*config['cell_width'],
                config['grid_y']+.5*config['cell_height'])
    selected=click(card_point,click_game.snapshot(),config)
    placed=click(lawn_point,dict(click_game.snapshot(),selection={'kind':'plant','type_id':role}),config)
    click_game.step([selected,placed])
    drag=begin_drag(role,card_point)
    plant_types={plant['id']:plant for plant in config['plant_types']}
    update_drag(drag,lawn_point,drag_game.snapshot(),config,level,plant_types)
    commands=finish_drag(drag,lawn_point,'playing',config,level,drag_game.snapshot(),plant_types)
    drag_game.step(commands)
    left,right=click_game.snapshot(),drag_game.snapshot()
    for key in ('sun','plants','ready_tick','selection'):
        assert left[key]==right[key]
    assert [event['kind'] for event in click_game.events]==[event['kind'] for event in drag_game.events]
