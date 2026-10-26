from pvz_game.config import load
from pvz_game.domain.commands import Command
from pvz_game.domain.commands import Command
from pvz_game.presentation.input import (
    begin_drag, cancel_drag, card_at, finish_drag, update_drag,
)


def test_press_move_release_tracks_valid_and_invalid_cells(game):
    config,level=load()
    plant_types={plant["id"]:plant for plant in config["plant_types"]}
    card=begin_drag("sunflower",(180,40))
    update_drag(card,(config["grid_x"]+36,config["grid_y"]+38),
                game.snapshot(),config,level,plant_types)
    assert card.hover_cell==(0,0) and card.preview_valid and card.reason_code is None
    occupied=dict(id=1,type_id="sunflower",row=0,col=0,hp=300)
    snapshot=dict(game.snapshot(),plants=(occupied,))
    update_drag(card,(config["grid_x"]+36,config["grid_y"]+38),
                snapshot,config,level,plant_types)
    assert not card.preview_valid and card.reason_code=="occupied"


def test_release_valid_cell_emits_one_plant_command_and_invalid_targets_do_not(game):
    config,level=load()
    card=begin_drag("jalapeno",(540,40))
    point=(config["grid_x"]+36,config["grid_y"]+38)
    types={plant["id"]:plant for plant in config["plant_types"]}
    update_drag(card,point,game.snapshot(),config,level,types)
    commands=finish_drag(card,point,"playing",config,level)
    assert [command.kind for command in commands]==["SelectPlant","PlantAt"]
    assert commands[1].args==(0,0)
    assert finish_drag(card,(820,40),"playing",config,level)==[]
    assert finish_drag(card,None,"playing",config,level)==[]
    assert finish_drag(card,(config["grid_x"]+36,config["grid_y"]+38),
                       "paused",config,level)==[]


def test_card_click_and_card_to_card_release_never_plant(game):
    config,level=load()
    card=begin_drag("sunflower",(180,40))
    assert card_at((530,40))=="jalapeno"
    commands=finish_drag(card,(530,40),"playing",config,level)
    assert len(commands)==1 and commands[0].kind=="SelectPlant"
    assert commands[0].args==("jalapeno",)


def test_cancel_clears_drag_state(game):
    card=begin_drag("wallnut",(420,40))
    assert cancel_drag(card) is None


def test_shovel_drag_validates_target_and_emits_one_removal(game):
    config,level=load()
    shovel=begin_drag('shovel',(680,50))
    plants={"id":1,"type_id":"wallnut","row":0,"col":0,"hp":400}
    snapshot=dict(game.snapshot(),plants=(plants,))
    point=(config['grid_x']+36,config['grid_y']+38)
    update_drag(shovel,point,snapshot,config,level,{})
    assert shovel.preview_valid
    commands=finish_drag(shovel,point,'playing',config,level,snapshot)
    assert [command.kind for command in commands]==['SelectShovel','ShovelAt']
    assert commands[1].args==(0,0)
    empty=dict(game.snapshot(),plants=())
    update_drag(shovel,point,empty,config,level,{})
    assert not shovel.preview_valid and shovel.reason_code=='no_plant'
    assert finish_drag(shovel,point,'playing',config,level,empty)==[]
    assert finish_drag(shovel,(680,50),'playing',config,level)==[Command('SelectShovel')]


def test_plant_drag_rejects_currently_invalid_release(game):
    config,level=load()
    card=begin_drag('sunflower',(180,40))
    point=(config['grid_x']+36,config['grid_y']+38)
    occupied=dict(id=1,type_id='wallnut',row=0,col=0,hp=400)
    snapshot=dict(game.snapshot(),plants=(occupied,))
    types={plant['id']:plant for plant in config['plant_types']}
    update_drag(card,point,snapshot,config,level,types)
    assert not card.preview_valid
    assert finish_drag(card,point,'playing',config,level,snapshot,types)==[]


def test_click_plant_card_selection_remains_available(game):
    config,_=load()
    assert game.snapshot()["selection"]["kind"]=="none"
    commands=[Command("SelectPlant",(name,)) for name in
              ("sunflower","peashooter","wallnut","jalapeno")]
    for command in commands:
        assert game.step([command])[0]["selection"]["type_id"]==command.args[0]
