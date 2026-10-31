import json

from pvz_game.progress import Progress


def test_music_settings_default_migrate_save_and_reload(tmp_path):
    path = tmp_path / 'progress.json'
    path.write_text(json.dumps({
        'schema_version': 1, 'unlocked': ['day_01', 'day_02'], 'levels': {},
        'endless': {'unlocked': False, 'best_wave': 0, 'best_kills': 0},
    }), encoding='utf-8')
    progress = Progress.load(path)
    assert progress.music_enabled is True
    assert progress.music_volume == 0.55
    progress.set_music_enabled(False)
    progress.set_music_volume(0.8)
    assert progress.save()
    loaded = Progress.load(path)
    assert loaded.music_enabled is False
    assert loaded.music_volume == 0.8
    assert loaded.is_unlocked('day_02')


def test_invalid_music_preferences_fall_back_without_losing_progress(tmp_path):
    path = tmp_path / 'progress.json'
    path.write_text(json.dumps({
        'schema_version': 2, 'unlocked': ['day_01', 'day_03'], 'levels': {},
        'endless': {'unlocked': False, 'best_wave': 0, 'best_kills': 0},
        'settings': {'background_id': 'night', 'music_enabled': 'yes', 'music_volume': 2.0},
    }), encoding='utf-8')
    progress = Progress.load(path)
    assert progress.music_enabled is True
    assert progress.music_volume == 0.55
    assert progress.background_id == 'night'
    assert progress.is_unlocked('day_03')


def test_music_volume_is_clamped_and_rejects_non_finite():
    import pytest

    progress = Progress.load()
    progress.set_music_volume(-4)
    assert progress.music_volume == 0.0
    progress.set_music_volume(4)
    assert progress.music_volume == 1.0
    with pytest.raises(ValueError):
        progress.set_music_volume(float('nan'))
