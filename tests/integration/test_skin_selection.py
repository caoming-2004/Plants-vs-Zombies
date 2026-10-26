import json
from pathlib import Path
import pytest
from pvz_game.presentation.skin_catalog import Catalog, AppearanceController
from test_asset_manifest import manifest_file


def catalog_fixture(tmp_path,manifest_file):
    path,data=manifest_file
    root=tmp_path/'assets'
    (root/'skins'/'default').mkdir(parents=True)
    (root/'skins'/'dogs').mkdir()
    for name in ('default','dogs'):
        directory=root/'skins'/name
        (directory/'atlas.png').write_bytes((path.parent/'atlas.png').read_bytes())
        data['skin_id']=name
        (directory/'manifest.json').write_text(json.dumps(data),encoding='utf8')
    (root/'sources.json').write_text('{"fixture":{}}')
    return Catalog(root)


def test_select_independent_and_restart_preserve(tmp_path,manifest_file):
    ctrl=AppearanceController(catalog_fixture(tmp_path,manifest_file))
    assert ctrl.select('plant','dogs','menu')
    assert ctrl.plant_skin_id=='dogs' and ctrl.zombie_skin_id=='default'
    assert not ctrl.select('zombie','dogs','playing')
    assert ctrl.select('zombie','dogs','menu')
    before=ctrl.selection()
    ctrl.on_restart()
    assert ctrl.selection()==before
    assert AppearanceController(ctrl.catalog).selection()==('default','default')


def test_broken_dog_falls_back_only_selected_side(tmp_path,manifest_file):
    catalog=catalog_fixture(tmp_path,manifest_file)
    ctrl=AppearanceController(catalog)
    ctrl.select('plant','dogs','menu')
    ctrl.select('zombie','dogs','menu')
    (catalog.root/'skins/dogs/atlas.png').write_bytes(b'broken')
    ctrl.validate_selection()
    assert ctrl.selection()==('default','default')
    assert ctrl.notice


def test_missing_dog_not_fatal(tmp_path,manifest_file):
    catalog=catalog_fixture(tmp_path,manifest_file)
    (catalog.root/'skins/dogs/manifest.json').unlink()
    ctrl=AppearanceController(catalog)
    assert not ctrl.select('plant','dogs','menu')
    assert ctrl.selection()==('default','default')
