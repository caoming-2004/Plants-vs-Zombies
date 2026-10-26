import copy
import json
import pygame
import pytest


@pytest.fixture
def manifest_file(tmp_path):
    image=pygame.Surface((16,16),pygame.SRCALPHA)
    image.fill((120,190,80,255))
    pygame.image.save(image,str(tmp_path/'atlas.png'))
    frame=dict(rect=[0,0,16,16],source_size=[16,16],trim_offset=[0,0],
               anchor=[8,16],muzzle=[16,8],contact=[0,8],duration_ticks=6)
    roles={}
    for role,states in {'sunflower':['idle','produce','hit','die'],
                         'peashooter':['idle','attack','hit','die'],
                         'wallnut':['idle','hit','die'],
                         'jalapeno':['plant','ignite','hit','die'],
                         'zombie_basic':['walk','bite','hit','die']}.items():
        roles[role]=dict(name=role,card=dict(frame),preview=dict(frame),
                         clips={state:dict(loop=state!='die',frames=[dict(frame)]) for state in states})
    data=dict(schema_version=1,skin_id='default',display_name='fixture',atlas='atlas.png',
              source_refs=['fixture'],roles=roles)
    path=tmp_path/'manifest.json'
    path.write_text(json.dumps(data),encoding='utf8')
    return path,data


def test_valid_manifest(manifest_file):
    from pvz_game.presentation.skin_catalog import Skin
    path,_=manifest_file
    skin=Skin(path,{'fixture':{}})
    assert skin.clip('peashooter','attack')['frames']
    assert skin.pixel_scale == 1


def test_manifest_accepts_two_x_source_pixels(manifest_file):
    from pvz_game.presentation.skin_catalog import Skin
    path,data=manifest_file
    data['pixel_scale']=2
    path.write_text(json.dumps(data),encoding='utf8')
    skin=Skin(path,{'fixture':{}})
    assert skin.pixel_scale == 2


@pytest.mark.parametrize('fault',['zero_duration','outside','zero_rect','missing_action','bad_trim','bad_anchor','bad_source','missing_atlas','ui_outside','bad_pixel_scale'])
def test_reject_invalid_manifest(manifest_file,fault):
    from pvz_game.presentation.skin_catalog import Skin, AssetError
    path,data=manifest_file
    frame=data['roles']['peashooter']['clips']['attack']['frames'][0]
    if fault=='zero_duration':frame['duration_ticks']=0
    if fault=='outside':frame['rect']=[10,10,16,16]
    if fault=='zero_rect':frame['rect'][2]=0
    if fault=='missing_action':del data['roles']['peashooter']['clips']['attack']
    if fault=='bad_trim':frame['trim_offset']=[20,0]
    if fault=='bad_anchor':frame['anchor']=[-1,0]
    if fault=='bad_source':data['source_refs']=['unknown']
    if fault=='missing_atlas':data['atlas']='lost.png'
    if fault=='ui_outside':
        data['ui_atlas']='atlas.png'
        data['ui']={'test':{'rect':[0,0,99,16]}}
    if fault=='bad_pixel_scale':data['pixel_scale']=3
    path.write_text(json.dumps(data),encoding='utf8')
    with pytest.raises(AssetError):Skin(path,{'fixture':{}})


def test_default_missing_is_fatal(tmp_path):
    from pvz_game.presentation.skin_catalog import Catalog, AssetError
    (tmp_path/'sources.json').write_text('{}')
    with pytest.raises(AssetError,match='默认'):
        Catalog(tmp_path)


def test_dog_manifest_frames_do_not_overlap_at_adjacent_cell_centers():
    from pvz_game.presentation.dog_validation import validate_dog_non_overlap
    from pvz_game.presentation.skin_catalog import Catalog
    catalog=Catalog()
    diagnostics=validate_dog_non_overlap(
        catalog.load('dogs'),catalog.load('default'),cell_width=72
    )
    assert not any(item.startswith('overlap ') for item in diagnostics)
    assert diagnostics==[]


def test_xiaobao_and_xiaodu_manifest_scale_is_at_least_fifteen_percent():
    from pvz_game.presentation.animation import display_scale_for_role, DOG_SCALE
    from pvz_game.presentation.skin_catalog import Catalog
    skin=Catalog().load('dogs')
    for role in ('wallnut','jalapeno'):
        assert display_scale_for_role(skin,role,DOG_SCALE)>=DOG_SCALE*1.15
    assert display_scale_for_role(skin,'sunflower',DOG_SCALE)==DOG_SCALE


def test_legacy_dog_manifest_without_role_multiplier_defaults_to_one():
    from types import SimpleNamespace
    from pvz_game.presentation.animation import display_scale_for_role
    skin=SimpleNamespace(data={'skin_id':'dogs','roles':{'wallnut':{}}})
    assert display_scale_for_role(skin,'wallnut',.68)==.68


def test_regenerated_dog_atlas_uses_uniform_runtime_transform_only():
    from pvz_game.presentation.animation import DOG_SCALE
    from pvz_game.presentation.dog_validation import validate_dog_non_overlap
    from pvz_game.presentation.skin_catalog import Catalog
    catalog=Catalog()
    diagnostics=validate_dog_non_overlap(
        catalog.load('dogs'),catalog.load('default'),cell_width=72,
        scale=DOG_SCALE
    )
    assert not any(item.startswith('overlap ') for item in diagnostics)
    assert diagnostics==[]


def test_dog_overlap_counts_any_nontransparent_alpha(manifest_file,tmp_path):
    from pvz_game.presentation.dog_validation import validate_dog_non_overlap
    from pvz_game.presentation.skin_catalog import Skin
    path,data=manifest_file
    default_skin=Skin(path,{'fixture':{}})

    dog_directory=tmp_path/'dogs'
    dog_directory.mkdir()
    dog_path=dog_directory/'manifest.json'
    dog_data=copy.deepcopy(data)
    dog_data['skin_id']='dogs'
    dog_data['display_name']='dogs'
    for role_data in dog_data['roles'].values():
        frames=[role_data['card'],role_data['preview']]
        frames.extend(
            frame
            for clip in role_data['clips'].values()
            for frame in clip['frames']
        )
        for frame in frames:
            frame.update(
                rect=[0,0,100,16],source_size=[128,16],
                trim_offset=[0,0],anchor=[64,16]
            )
    atlas=pygame.Surface((128,16),pygame.SRCALPHA)
    atlas.fill((0,0,0,0))
    atlas.fill((120,190,80,255),(0,0,61,16))
    atlas.fill((120,190,80,20),(70,0,20,16))
    pygame.image.save(atlas,str(dog_directory/'atlas.png'))
    dog_path.write_text(json.dumps(dog_data),encoding='utf8')
    dog_skin=Skin(dog_path,{'fixture':{}})

    diagnostics=validate_dog_non_overlap(
        dog_skin,default_skin,cell_width=72,scale=0.81
    )
    assert any('left=sunflower.idle[0] right=sunflower.produce[0]' in item
               for item in diagnostics)
    assert any('left=sunflower.idle[0] right=peashooter.idle[0]' in item
               for item in diagnostics)


def test_dog_height_diagnostic_uses_default_role_height(manifest_file):
    from pvz_game.presentation.dog_validation import validate_dog_non_overlap
    from pvz_game.presentation.skin_catalog import Skin
    path,_=manifest_file
    skin=Skin(path,{'fixture':{}})

    diagnostics=validate_dog_non_overlap(skin,skin,cell_width=72,scale=0.5)
    assert any('height_below_75_percent role=sunflower state=die frame=0'
               in item for item in diagnostics)


def test_uploaded_xiaobao_and_xiaodu_source_frames_are_fully_traceable():
    import hashlib
    from pathlib import Path
    root=Path(__file__).resolve().parents[2]
    from pvz_game.presentation.skin_catalog import Catalog
    skin=Catalog().load('dogs')
    sources=json.loads((root/'assets/sources.json').read_text(encoding='utf8'))
    provenance=json.loads((root/'assets/skins/dogs/provenance.json').read_text(encoding='utf8'))
    records={item['role']:item for item in provenance if item.get('origin')=='user-uploaded'}
    expected={'wallnut':('xiaobao-user-60.png',{'idle','hit','die'}),
              'jalapeno':('xiaodu-user-60.png',{'plant','ignite','hit','die'})}
    for role,(filename,states) in expected.items():
        path=root/'assets/skins/dogs/source'/filename
        record=records[role]
        assert record['source']==filename and record['source_frame_count']==60
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        assert record['sha256']==digest
        assert sources['user-dog-animation-sheets']['files'][role]['sha256']==digest
        assert set(skin.data['roles'][role]['clips'])==states
        used=set()
        for state,clip in skin.data['roles'][role]['clips'].items():
            declared=set(record['clip_source_frames'][state])
            for frame in clip['frames']:
                refs=set(frame['source_frames'])
                assert refs and refs<=declared
                used.update(refs)
        assert used==set(range(60))


def test_user_sheet_import_rejects_an_empty_source_frame(tmp_path,monkeypatch):
    import importlib.util
    from pathlib import Path
    source_dir=tmp_path/'source';source_dir.mkdir()
    sheet=pygame.Surface((1600,960),pygame.SRCALPHA)
    for row in range(6):
        for col in range(10):
            if row==5 and col==9:continue
            pygame.draw.ellipse(sheet,(180,120,70,255),(col*160+45,row*160+35,70,110))
    pygame.image.save(sheet,str(source_dir/'missing.png'))
    module_path=Path(__file__).resolve().parents[2]/'tools'/'import_dog_assets.py'
    spec=importlib.util.spec_from_file_location('dog_asset_importer',module_path)
    importer=importlib.util.module_from_spec(spec);spec.loader.exec_module(importer)
    monkeypatch.setattr(importer,'OUT',tmp_path)
    with pytest.raises(ValueError,match='empty source frame 59'):
        importer.user_sheet('missing.png')


def test_dog_overlap_uses_trim_offset_and_anchor(manifest_file):
    from pvz_game.presentation.dog_validation import validate_dog_non_overlap
    from pvz_game.presentation.skin_catalog import Skin
    path,_=manifest_file
    default_skin=Skin(path,{'fixture':{}})
    dog_skin=Skin(path,{'fixture':{}})
    dog_skin.data['skin_id']='dogs'
    for role_data in dog_skin.data['roles'].values():
        for frame in (role_data['card'],role_data['preview']):
            frame.update(
                source_size=[128,16],trim_offset=[0,0],anchor=[64,16]
            )
        for state,clip in role_data['clips'].items():
            for frame in clip['frames']:
                frame.update(
                    source_size=[128,16],
                    trim_offset=[90 if state=='die' else 0,0],
                    anchor=[64,16]
                )

    diagnostics=validate_dog_non_overlap(dog_skin,default_skin,cell_width=72)
    assert any('left=sunflower.die[0] right=sunflower.hit[0]' in item
               for item in diagnostics)
