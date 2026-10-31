import json
from pathlib import Path
from pvz_game.config import load_campaign
from pvz_game.progress import Progress, default_progress


def test_default_progress_and_win_unlock(progress_path):
    path = progress_path
    progress = Progress.load(path)
    assert progress.is_unlocked("day_01")
    assert not progress.is_unlocked("day_02")
    assert not progress.endless_unlocked
    config, campaign, levels = load_campaign()
    assert progress.record_win("day_01", campaign["stages"], stars=1, ticks=9000)
    assert progress.is_unlocked("day_02")
    progress.save()
    reloaded = Progress.load(path)
    assert reloaded.is_unlocked("day_02")
    assert reloaded.data["levels"]["day_01"] == {"cleared": True, "best_stars": 1, "best_ticks": 9000}


def test_best_stars_and_ticks_never_regress(progress_path):
    path = progress_path
    progress = Progress.load(path)
    _, campaign, _ = load_campaign()
    progress.record_win("day_01", campaign["stages"], stars=2, ticks=8000)
    progress.record_win("day_01", campaign["stages"], stars=1, ticks=12000)
    record = progress.data["levels"]["day_01"]
    assert record["best_stars"] == 2
    assert record["best_ticks"] == 8000


def test_last_stage_unlocks_endless_and_records_max(progress_path):
    path = progress_path
    progress = Progress.load(path)
    _, campaign, _ = load_campaign()
    for level_id in campaign["stages"]:
        progress.record_win(level_id, campaign["stages"], stars=1, ticks=5000)
    assert progress.endless_unlocked
    progress.record_endless(8, 40)
    progress.record_endless(5, 90)
    assert progress.data["endless"]["best_wave"] == 8
    assert progress.data["endless"]["best_kills"] == 90


def test_corrupt_or_missing_progress_falls_back(progress_path):
    path = progress_path
    missing = Progress.load(path)
    assert missing.recovered is False
    path.write_text("{not valid json", encoding="utf-8")
    corrupt = Progress.load(path)
    assert corrupt.recovered is True
    assert corrupt.data == default_progress()


def test_bad_schema_and_unknown_levels_are_tolerated(progress_path):
    path = progress_path
    path.write_text(json.dumps({"schema_version": 99}), encoding="utf-8")
    assert Progress.load(path).recovered is True
    good = default_progress()
    good["unlocked"].append("season_99")
    good["levels"]["old_map"] = {"cleared": True, "best_stars": 3, "best_ticks": 100}
    path.write_text(json.dumps(good), encoding="utf-8")
    loaded = Progress.load(path)
    assert "day_01" in loaded.data["unlocked"]
    assert "old_map" in loaded.data["levels"]

def test_star_goals_evaluate_from_run_stats():
    from pvz_game.domain import campaign as rules
    from pvz_game.config import load
    _, level = load()
    stats = {"mowers_used": 0, "elapsed_ticks": 9000, "sun_collected": 500}
    assert rules.evaluate_stars(level, stats) == ["no_mower", "fast_clear"]
    stats = {"mowers_used": 1, "elapsed_ticks": 16000, "sun_collected": 500}
    assert rules.evaluate_stars(level, stats) == []
