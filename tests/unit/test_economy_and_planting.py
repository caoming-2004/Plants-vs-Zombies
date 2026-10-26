import pytest
from pvz_game.domain.commands import Command


def do(game, kind, *args):
    return game.step([Command(kind, args)])[0]


def plant(game, row=0, col=0, kind="sunflower"):
    do(game, "SelectPlant", kind)
    return do(game, "PlantAt", row, col)


def test_plant_atomic_failure_and_shovel(game):
    initial = game.sun
    plant(game)
    assert game.sun == initial - 50
    assert len(game.plants) == 1
    ready = game.ready_tick["sunflower"]
    plant(game, col=1)
    assert len(game.plants) == 1
    assert game.sun == initial - 50
    do(game, "SelectShovel")
    do(game, "ShovelAt", 0, 0)
    assert not game.plants
    assert game.sun == initial - 50
    assert game.ready_tick["sunflower"] == ready
    assert game.selection.kind == "shovel"
    do(game, "ShovelAt", 0, 0)
    assert game.sun == initial - 50


@pytest.mark.parametrize("offset,success", [(-1,True),(0,False),(1,False)])
def test_sun_expiry_boundary(game, offset, success):
    sun = game.add_sun(200, 200, 25)
    game.tick = sun.expires_tick + offset
    before = game.sun
    do(game, "CollectSun", sun.id)
    assert game.sun == before + (25 if success else 0)
    do(game, "CollectSun", sun.id)
    assert game.sun == before + (25 if success else 0)


@pytest.mark.parametrize("row,col", [(-1,0),(5,0),(0,12),(0,-1)])
def test_invalid_grid_does_not_charge(game,row,col):
    before = game.sun
    plant(game,row,col)
    assert game.sun == before
    assert not game.plants


def test_occupied_and_insufficient(game):
    plant(game)
    game.ready_tick["sunflower"] = 0
    before = game.sun
    plant(game)
    assert game.sun == before
    assert len(game.plants) == 1
    game.sun = 0
    plant(game, col=2)
    assert len(game.plants) == 1
    assert game.sun == 0


def test_producer_sun_survives_shovel(game):
    plant(game)
    p = next(iter(game.plants.values()))
    game.tick = p.next_action_tick
    game.step()
    produced = set(game.suns)
    assert produced
    do(game,"SelectShovel")
    do(game,"ShovelAt",0,0)
    assert produced <= set(game.suns)


def test_pause_freezes_sun_and_cooldowns(game):
    plant(game)
    sun = game.add_sun(200,200,25)
    do(game,"Pause")
    tick, amount = game.tick, game.sun
    for _ in range(100):
        do(game,"CollectSun",sun.id)
    assert game.tick == tick and game.sun == amount and sun.id in game.suns
    do(game,"Resume")
    do(game,"CollectSun",sun.id)
    assert game.sun == amount + 25
