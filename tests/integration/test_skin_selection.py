import json
from pathlib import Path
import pytest
from pvz_game.presentation.skin_catalog import Catalog, AppearanceController
from pvz_game.config import load
from pvz_game.presentation.input import click
from pvz_game.presentation.scenes import BUTTONS
from test_asset_manifest import manifest_file


def catalog_fixture(tmp_path,manifest_file):
    path,data=manifest_file
    root=tmp_path/'assets'
    (root/'skins'/'default').mkdir(parents=True)
    (root/'skins'/'dogs').mkdir()
    (root/'skins'/'dogs_photo').mkdir()
    for name in ('default','dogs','dogs_photo'):
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


def test_photo_skin_is_plant_only_and_missing_skin_falls_back(tmp_path,manifest_file):
    catalog=catalog_fixture(tmp_path,manifest_file)
    ctrl=AppearanceController(catalog)
    assert ctrl.select('plant','dogs_photo','menu')
    assert not ctrl.select('zombie','dogs_photo','menu')
    assert ctrl.selection()==('dogs_photo','default')
    (catalog.root/'skins/dogs_photo/atlas.png').write_bytes(b'broken')
    ctrl.validate_selection()
    assert ctrl.selection()==('default','default')
    assert ctrl.notice


def test_photo_skin_has_its_own_menu_selection_action():
    rect=BUTTONS['plant_dogs_photo']
    point=(rect[0]+rect[2]/2,rect[1]+rect[3]/2)
    result=click(point,{'phase':'menu'},load()[0],skins_open=True)
    assert result=='choose_plant_dogs_photo'


def test_async_skin_choice_is_acknowledged_before_asset_decode(tmp_path,manifest_file,monkeypatch):
    catalog=catalog_fixture(tmp_path,manifest_file)
    ctrl=AppearanceController(catalog)
    started=[]
    monkeypatch.setattr(catalog,'preload_async',lambda skin_id:started.append(skin_id))
    assert ctrl.select_async('plant','dogs_photo','menu')
    assert started==['dogs_photo']
    assert ctrl.selection()==('default','default')
    assert ctrl.pending_for('plant')=='dogs_photo'
    assert ctrl.notice
    catalog.load('dogs_photo',refresh=True)
    assert ctrl.poll_pending()
    assert ctrl.selection()==('dogs_photo','default')


def test_special_dog_plant_roles_are_shown_in_skin_menu(monkeypatch):
    import pygame
    from pvz_game.presentation.renderer import Renderer
    pygame.font.init()
    config,_=load();renderer=Renderer(config)
    old_selection=renderer.appearance.selection()
    drawn=[]
    monkeypatch.setattr(renderer,'text',lambda value,*args,**kwargs:drawn.append(value))
    renderer.skin_menu(0)
    assert '胖宝宝·倭瓜' in drawn and '黄黄·寒冰射手' in drawn
    for role in ('pangbaobao','huanghuang'):
        rect=BUTTONS['role_preview_'+role]
        point=(rect[0]+rect[2]/2,rect[1]+rect[3]/2)
        result=click(point,{'phase':'menu'},config,skins_open=True)
        assert result=='preview_role_'+role
        assert renderer.focus_role_preview(role)
    assert renderer.appearance.selection()==old_selection
