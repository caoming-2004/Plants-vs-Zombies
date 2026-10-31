import json
import shutil
import uuid
from pathlib import Path

from pvz_game.presentation.backgrounds import BackgroundCatalog
from pvz_game.progress import Progress


def test_bundled_backgrounds_have_three_hd_options():
    catalog = BackgroundCatalog()
    assert catalog.error == ''
    assert catalog.default_id == 'day'
    assert len(catalog.order) >= 3
    assert {'day', 'night', 'dusk'} <= {catalog.options[item]['theme'] for item in catalog.order}
    for item in catalog.order:
        option = catalog.options[item]
        assert option['width'] >= 2560 and option['height'] >= 1440
        assert option['sha256']
    assert catalog.surface('night').get_size() == (1050, 600)
    assert catalog.thumbnail('dusk').get_size() == (220, 124)


def test_unknown_background_falls_back_to_default():
    catalog = BackgroundCatalog()
    assert catalog.resolve('unknown') == catalog.default_id


def test_progress_v1_migrates_background_setting(progress_path):
    progress_path.write_text(json.dumps({
        'schema_version': 1,
        'unlocked': ['day_01'],
        'levels': {},
        'endless': {'unlocked': False, 'best_wave': 0, 'best_kills': 0},
    }), encoding='utf-8')
    progress = Progress.load(progress_path)
    assert progress.data['schema_version'] == 2
    assert progress.background_id == 'day'
    progress.set_background('night')
    assert progress.background_id == 'night'


def test_missing_background_manifest_is_reported():
    root = Path('.tools') / ('bg-test-' + uuid.uuid4().hex)
    root.mkdir(parents=True)
    try:
        manifest = {
            'schema_version': 1, 'default': 'day',
            'options': [
                {'id': theme, 'name': theme, 'file': theme + '.png', 'thumb': 'thumbs/' + theme + '.png',
                 'width': 2560, 'height': 1440, 'theme': theme, 'source': 'test',
                 'sha256': '0' * 64, 'license': 'test'} for theme in ('day', 'night', 'dusk')
            ],
        }
        (root / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
        catalog = BackgroundCatalog(root)
        assert catalog.error
        assert catalog.surface('day') is None
    finally:
        shutil.rmtree(root, ignore_errors=True)
