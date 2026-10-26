from copy import deepcopy
from pathlib import Path
import pytest
from pvz_game.config import load, validate


def test_bad_configs():
    c,l = load()
    assert l["rows"] == 5 and l["cols"] == 12
    assert c["grid_x"]+l["cols"]*c["cell_width"]==969
    assert c["canvas_width"]==1050 and c["canvas_height"]==600
    bad = deepcopy(l)
    bad["cols"] = 9
    with pytest.raises(ValueError,match="十二列"): validate(c,bad)
    bad = deepcopy(l)
    bad["cols"] = 13
    with pytest.raises(ValueError): validate(c,bad)
    for key,value in [("tick_hz",30),("initial_sun",-1),("sun_value",0),("mower_speed",float("nan"))]:
        bad = deepcopy(c)
        bad[key] = value
        with pytest.raises(ValueError): validate(bad,l)
    bad = deepcopy(c)
    bad["plant_types"].append(bad["plant_types"][0])
    with pytest.raises(ValueError): validate(bad,l)
    for row in (-1,5):
        bad = deepcopy(l)
        bad["spawn_schedule"][0]["row"] = row
        with pytest.raises(ValueError): validate(c,bad)


def test_snapshot_detached_and_immutable(game):
    snapshot = game.snapshot()
    with pytest.raises(TypeError): snapshot["sun"] = 0
    with pytest.raises(TypeError): snapshot["mowers"][0]["state"] = "spent"
    game.sun = 1000
    assert snapshot["sun"] == 150


def test_domain_has_no_pygame_import():
    import pvz_game.domain
    for path in Path(pvz_game.domain.__file__).parent.glob("*.py"):
        assert "import pygame" not in path.read_text(encoding="utf-8")


def test_all_four_plant_roles_have_valid_role_specific_fields():
    config, level = load()
    config = deepcopy(config)
    config["plant_types"] = config["plant_types"][:2] + [
        {"id": "wallnut", "name": "坚果墙", "price": 50, "hp": 1200,
         "cooldown_ticks": 1800, "role": "blocker"},
        {"id": "jalapeno", "name": "火爆辣椒", "price": 125,
         "cooldown_ticks": 3000, "role": "row_clearer"},
    ]
    assert validate(config, level)[0] is config


@pytest.mark.parametrize("bad_plant", [
    {"id": "wallnut", "name": "坚果墙", "price": 50, "cooldown_ticks": 1800,
     "role": "blocker"},
    {"id": "jalapeno", "name": "火爆辣椒", "price": 125, "hp": 100,
     "cooldown_ticks": 3000, "role": "row_clearer"},
    {"id": "wallnut", "name": "坚果墙", "price": 50, "hp": 1200,
     "cooldown_ticks": 1800, "role": "blocker", "attack_interval_ticks": 10},
    {"id": "jalapeno", "name": "火爆辣椒", "price": 125, "cooldown_ticks": 3000,
     "role": "row_clearer", "production_interval_ticks": 10},
    {"id": "wallnut", "name": "坚果墙", "price": -1, "hp": 1200,
     "cooldown_ticks": 1800, "role": "blocker"},
    {"id": "wallnut", "name": "坚果墙", "price": 50, "hp": 1200,
     "cooldown_ticks": 0, "role": "blocker"},
])
def test_invalid_plant_role_fields_are_rejected(bad_plant):
    config, level = load()
    config = deepcopy(config)
    config["plant_types"].append(bad_plant)
    with pytest.raises(ValueError):
        validate(config, level)
