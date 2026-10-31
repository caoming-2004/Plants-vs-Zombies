from pvz_game.config import load
from pvz_game.presentation.performance import (
    SCENES,
    make_scene,
    make_simulation,
    summarize_frame_intervals,
)


def test_benchmark_scenes_match_the_declared_fixed_loads():
    config, level = load()
    assert SCENES["standard"] == {
        "sunflowers": 5, "peashooters": 5, "zombies": 5,
        "projectiles": 10, "suns": 3, "mowers": 5,
    }
    assert SCENES["pressure"] == {
        "sunflowers": 23, "peashooters": 22, "zombies": 30,
        "projectiles": 100, "suns": 20, "mowers": 5,
    }
    for name, expected in SCENES.items():
        scene = make_scene(config, level, name)
        game = make_simulation(config, level, name)
        assert len(scene["plants"]) == expected["sunflowers"] + expected["peashooters"]
        assert len(scene["zombies"]) == expected["zombies"]
        assert len(scene["projectiles"]) == expected["projectiles"]
        assert len(scene["suns"]) == expected["suns"]
        assert len(scene["mowers"]) == expected["mowers"]
        assert len(game.plants) == len(scene["plants"])
        assert len(game.zombies) == len(scene["zombies"])
        assert len(game.projectiles) == len(scene["projectiles"])
        assert len(game.suns) == len(scene["suns"])
        game.step()
        assert game.tick == 1 and game.phase == "playing"


def test_frame_interval_summary_reports_p95_and_long_slow_run():
    report = summarize_frame_intervals([16, 34, 53, 20, 17])
    assert report["p95_frame_ms"] == 53
    assert report["longest_over_50ms_frames"] == 1
    assert report["over_33ms_frames"] == 2
    assert report["longest_over_33ms_run"] == 2


def test_hot_path_can_skip_unused_tick_snapshot_without_changing_events():
    config, level = load()
    with_snapshot = make_simulation(config, level, "standard")
    without_snapshot = make_simulation(config, level, "standard")
    snapshot, expected_events = with_snapshot.step()
    empty_snapshot, actual_events = without_snapshot.step(include_snapshot=False)
    assert snapshot["tick"] == 1
    assert empty_snapshot is None
    assert actual_events == expected_events
    assert without_snapshot.snapshot() == snapshot
