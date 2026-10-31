from pvz_game.config import load_campaign
from pvz_game.domain.commands import Command
from pvz_game.domain.endless import EndlessDirector, make_level
from pvz_game.domain.simulation import Simulation


def test_endless_level_and_director_keep_future_waves():
    config, campaign, _ = load_campaign()
    level = make_level(campaign)
    assert level["mode"] == "endless"
    assert level["max_active_zombies"] == campaign["endless"]["max_active_zombies"]
    game = Simulation(config, level)
    game.step([Command("Start")])
    assert isinstance(game.director, EndlessDirector)
    assert len(game.waves) >= 2
    assert game.waves[0]["start_tick"] <= game.waves[1]["start_tick"]
    assert game.wave_preview()["wave_id"] == "endless_wave_001"


def test_endless_never_reaches_won_and_scales_waves():
    config, campaign, _ = load_campaign()
    level = make_level(campaign)
    game = Simulation(config, level)
    game.step([Command("Start")])
    for _ in range(2000):
        game.step()
    assert game.phase != "won"
    assert len(game.waves) > 2
    assert game.wave_index >= 2


def test_endless_active_cap_is_respected():
    config, campaign, _ = load_campaign()
    level = make_level(campaign)
    level["max_active_zombies"] = 1
    game = Simulation(config, level)
    game.step([Command("Start")])
    for _ in range(1200):
        game.step()
        assert sum(1 for zombie in game.zombies.values() if zombie.hp > 0) <= 1


def test_endless_restart_resets_generated_waves():
    config, campaign, _ = load_campaign()
    game = Simulation(config, make_level(campaign))
    game.step([Command("Start")])
    before = len(game.waves)
    game.step([Command("Restart")])
    assert game.tick == 1
    assert len(game.waves) >= 2
    assert game.next_spawn_index == 0
    assert before >= 2
