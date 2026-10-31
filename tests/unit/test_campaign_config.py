from copy import deepcopy
import pytest
from pvz_game.config import load, load_campaign, validate


def test_campaign_has_five_ordered_stages():
    config, campaign, levels = load_campaign()
    assert campaign["stages"] == ["day_01", "day_02", "day_03", "day_04", "day_05"]
    assert list(levels) == campaign["stages"]
    assert campaign["endless"]["unlock_after"] == "day_05"
    for index, level_id in enumerate(campaign["stages"], start=1):
        level = levels[level_id]
        assert level["id"] == level_id
        assert level["order"] == index
        assert level["rows"] == 5 and level["cols"] == 12
        assert len(level["waves"]) >= 3
        assert len(level.get("star_goals", [])) >= 2
        strengths = [wave["strength"] for wave in level["waves"]]
        assert strengths == sorted(strengths) and len(set(strengths)) == len(strengths)


def test_day01_keeps_existing_wave_values_and_load_contract():
    config, level = load()
    assert level["id"] == "day_01"
    assert len(level["spawn_schedule"]) == 12
    assert level["waves"][0]["start_tick"] == 1200
    assert level["waves"][-1]["start_tick"] == 8400
    assert config["initial_sun"] == 150
    assert level["star_goals"][0]["kind"] == "mowers_used_at_most"


def test_level_optional_fields_are_validated():
    config, level = load()
    bad = deepcopy(level)
    bad["available_plants"] = ["not-a-plant"]
    with pytest.raises(ValueError, match="可用植物"):
        validate(config, bad)
    bad = deepcopy(level)
    bad["mower_rows"] = [0, 0]
    with pytest.raises(ValueError, match="割草机行"):
        validate(config, bad)
    bad = deepcopy(level)
    bad["star_goals"][0]["kind"] = "unknown"
    with pytest.raises(ValueError, match="星级目标类型"):
        validate(config, bad)


def test_campaign_rejects_bad_stage_order():
    config, campaign, levels = load_campaign()
    bad = deepcopy(campaign)
    bad["stages"][-1] = "day_04"
    with pytest.raises(ValueError):
        from pvz_game.config import validate_campaign
        validate_campaign(config, bad)
