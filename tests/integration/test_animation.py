import pygame
from pvz_game.presentation.skin_catalog import Catalog, AppearanceController, REQUIRED
from pvz_game.presentation.animation import (Animator, frame_at, anchor_position, blit_frame,
                                             pose_rate_hz, POSE_RATE_MIN_HZ, POSE_RATE_MAX_HZ)
from pvz_game.config import load
from pvz_game.domain.commands import Command


def test_real_action_coverage_and_dog_foot_baselines():
    catalog=Catalog()
    for skin_id in ('default','dogs','dogs_photo'):
        skin=catalog.load(skin_id)
        for role,states in REQUIRED.items():
            for state in states:
                clip=skin.clip(role,state)
                duration=sum(f['duration_ticks'] for f in clip['frames'])
                for tick in range(duration*3):
                    f=frame_at(clip,tick)
                    expected=[128,232] if skin_id in ('dogs','dogs_photo') else ([128,224] if skin.pixel_scale==2 else [64,112])
                    assert f['anchor']==expected
                    assert anchor_position(f,(20,30),'anchor',1/skin.pixel_scale)==(20,30)
                if skin_id in ('dogs','dogs_photo'):
                    bottoms=[
                        f['trim_offset'][1]+max(
                            rect.bottom for rect in pygame.mask.from_surface(
                                skin.surface(f),64).get_bounding_rects())
                        for f in clip['frames']
                    ]
                    assert max(bottoms)-min(bottoms)<=2


def test_dog_repeating_actions_last_at_least_one_second():
    repeating={
        'sunflower':('idle',),
        'peashooter':('idle',),
        'zombie_basic':('walk',),
    }
    for skin_id in ('dogs','dogs_photo'):
        skin=Catalog().load(skin_id)
        for role,states in repeating.items():
            for state in states:
                clip=skin.clip(role,state)
                duration=sum(frame['duration_ticks'] for frame in clip['frames'])
                assert duration>=60, f'{skin_id}/{role}/{state} repeats in {duration} ticks'


def test_animation_hit_does_not_restart_action_and_death_expires(game):
    catalog=Catalog();appearance=AppearanceController(catalog)
    appearance.select('zombie','dogs','menu')
    animator=Animator(appearance);snap=game.snapshot();animator.consume(snap,[])
    z=game.add_zombie(0,x=400)
    animator.actions[z.id]=('bite',game.tick)
    event=dict(kind='hit',id=z.id,tick=game.tick,session_id=game.session_id)
    animator.consume(game.snapshot(),[event])
    assert animator.actions[z.id]==('bite',game.tick)
    animator.consume(game.snapshot(),[dict(kind='died',id=z.id,tick=game.tick,
                  row=0,x=400,type_id='zombie_basic',session_id=game.session_id)])
    target=pygame.Surface((800,600),pygame.SRCALPHA)
    animator.draw_deaths(target,game.tick,game.row_y)
    assert len(animator.deaths)==1
    animator.draw_deaths(target,game.tick+1000,game.row_y)
    assert animator.deaths==[]


def test_shooter_does_not_visually_fire_before_event(game):
    game.step([Command('SelectPlant',('peashooter',)),Command('PlantAt',(0,0),sequence=1)])
    game.add_zombie(0,x=500)
    game.step()
    appearance=AppearanceController(Catalog());appearance.select('plant','dogs','menu')
    animator=Animator(appearance);animator.consume(game.snapshot(),game.events)
    actor=game.snapshot()['plants'][0]
    animator.draw_actor(pygame.Surface((128,128),pygame.SRCALPHA),actor,(64,112),game.tick)
    assert animator.state_since[actor['id']][0]=='idle'


def test_two_x_frame_pixels_and_anchor_are_drawn_in_logical_units():
    from types import SimpleNamespace
    source=pygame.Surface((16,16),pygame.SRCALPHA)
    source.fill((255,255,255,255))
    frame={'rect':[0,0,16,16],'source_size':[16,16],'trim_offset':[0,0],
           'anchor':[8,16],'muzzle':[8,8],'contact':[8,8],'duration_ticks':1}
    skin=SimpleNamespace(pixel_scale=2,surface=lambda unused: source)
    target=pygame.Surface((32,32),pygame.SRCALPHA)
    blit_frame(target,skin,frame,(16,16))
    assert target.get_bounding_rect()==pygame.Rect(12,8,8,8)


def test_coordinate_mapping_keeps_letterbox_and_round_trips():
    from pvz_game.presentation.coordinates import to_logical,to_window,viewport
    assert to_logical((0,0),(1200,600)) is None
    point=(500,300)
    pixel=to_window(point,(1920,1080))
    mapped=to_logical(pixel,(1920,1080))
    assert mapped==point
    assert viewport((1260,720))==(0.0,0.0,1.2)


def test_every_required_clip_has_12_to_18_distinct_visible_poses_per_second():
    import pygame
    config,_=load()
    for skin_id in ('default','dogs','dogs_photo'):
        skin=Catalog().load(skin_id)
        assert skin.pixel_scale==2
        for role,states in REQUIRED.items():
            for state in states:
                clip=skin.clip(role,state);frames=clip['frames']
                duration=sum(frame['duration_ticks'] for frame in frames)
                unique=len({pygame.image.tobytes(skin.surface(frame),'RGBA') for frame in frames})
                rate=pose_rate_hz(unique,duration,config['tick_hz'])
                assert POSE_RATE_MIN_HZ<=rate<=POSE_RATE_MAX_HZ, f'{skin_id}/{role}/{state}: {rate:.2f}/s'
                if clip['loop']:
                    assert duration>=60, f'{skin_id}/{role}/{state} loop is shorter than one second'


def test_plant_pose_rate_is_about_12_distinct_poses_per_second():
    plant_loops={
        'sunflower':('idle',), 'peashooter':('idle',), 'wallnut':('idle',),
        'jalapeno':('plant',), 'pangbaobao':('idle',), 'huanghuang':('idle',),
    }
    config,_=load()
    for skin_id in ('default','dogs','dogs_photo'):
        skin=Catalog().load(skin_id)
        for role,states in plant_loops.items():
            if role not in skin.data['roles']:continue
            for state in states:
                clip=skin.clip(role,state)
                if not clip['loop']:continue
                duration=sum(frame['duration_ticks'] for frame in clip['frames'])
                unique=len({pygame.image.tobytes(skin.surface(frame),'RGBA') for frame in clip['frames']})
                rate=pose_rate_hz(unique,duration,config['tick_hz'])
                assert abs(rate-12)<=.2, f'{skin_id}/{role}/{state}: {rate:.2f}/s'


def test_scaled_dog_roles_keep_every_pose_on_stable_foot_baseline():
    from pvz_game.presentation.animation import display_scale_for_role, DOG_SCALE
    from pvz_game.presentation.skin_catalog import Catalog
    for skin_id in ('dogs','dogs_photo'):
        skin=Catalog().load(skin_id)
        for role in ('peashooter','wallnut','jalapeno'):
            rendered_bottoms=[]
            scale=display_scale_for_role(skin,role,DOG_SCALE)/skin.pixel_scale
            for clip in skin.data['roles'][role]['clips'].values():
                for frame in clip['frames']:
                    visible=skin.surface(frame).get_bounding_rect(min_alpha=1)
                    rendered_bottoms.append(round((frame['trim_offset'][1]+visible.bottom-frame['anchor'][1])*scale))
            assert max(rendered_bottoms)-min(rendered_bottoms)<=2


def test_adjusted_dog_roles_fit_all_visible_frames():
    from pvz_game.presentation.animation import DOG_SCALE,display_scale_for_role,fit_visible_frame
    from pvz_game.presentation.dog_validation import dog_visual_bounds
    from pvz_game.presentation.skin_catalog import REQUIRED_BY_SKIN
    target=pygame.Surface((1050,600),pygame.SRCALPHA)
    for skin_id in ('dogs','dogs_photo'):
        skin=Catalog().load(skin_id)
        roles=dict(REQUIRED);roles.update(REQUIRED_BY_SKIN.get(skin_id,{}))
        largest_heights={}
        for role,states in roles.items():
            scale=display_scale_for_role(skin,role,DOG_SCALE)
            heights=[]
            for state in states:
                for frame in skin.clip(role,state)['frames']:
                    for position in ((0,0),(1050,600),(141,238),(933,542)):
                        fitted=fit_visible_frame(target,skin,frame,position,scale)
                        left,top,right,bottom=dog_visual_bounds(skin,role,frame,fitted,scale)
                        assert left>=-1 and top>=-1 and right<=1051 and bottom<=601
                    visible=skin.surface(frame).get_bounding_rect(min_alpha=1)
                    heights.append(visible.h*scale/skin.pixel_scale)
            largest_heights[role]=max(heights)
        assert min(largest_heights.values())>0
        assert (max(largest_heights.values())-min(largest_heights.values()))/max(largest_heights.values())<=.20
        expected_map_height=188*DOG_SCALE/skin.pixel_scale
        assert all(abs(height-expected_map_height)<=1.2 for height in largest_heights.values())
    photo=Catalog().load('dogs_photo')
    assert not {'pangbaobao','huanghuang'} & set(photo.data['roles'])


def test_dog_frame_bounds_keep_full_silhouettes_and_source_pose_mapping():
    import json
    from pathlib import Path
    from pvz_game.presentation.skin_catalog import REQUIRED_BY_SKIN
    root=Path(__file__).resolve().parents[2]
    skin=Catalog().load('dogs')
    manifest=json.loads((root/'assets/skins/dogs/manifest.json').read_text(encoding='utf-8-sig'))
    provenance=json.loads((root/'assets/skins/dogs/provenance.json').read_text(encoding='utf-8-sig'))
    atlas=pygame.image.load(str(root/'assets/skins/dogs'/manifest['atlas']))
    records={record['role']:record for record in provenance}
    roles=dict(REQUIRED);roles.update(REQUIRED_BY_SKIN['dogs'])
    for role,states in roles.items():
        assert role in records
        for state in states:
            allowed=set(records[role]['clip_source_frames'][state])
            for frame in skin.clip(role,state)['frames']:
                rect=pygame.Rect(frame['rect'])
                assert rect.left>=0 and rect.top>=0
                assert rect.right<=atlas.get_width() and rect.bottom<=atlas.get_height()
                visible=skin.surface(frame).get_bounding_rect(min_alpha=96)
                assert visible.w and visible.h, f'{role}/{state} contains an empty frame'
                assert visible.left>=8 and visible.top>=8
                assert visible.right<=248 and visible.bottom<=232, f'{role}/{state} silhouette touches crop edge'
                assert set(frame['source_frames'])<=allowed, f'{role}/{state} uses an unmapped source pose'


def test_dog_zombie_faces_left_in_all_actor_states(monkeypatch,game):
    from pvz_game.presentation import animation
    observed=[]
    def capture(target,skin,frame,position,scale=1,alpha=255,hit=False,flip_x=False):
        observed.append(flip_x)
    monkeypatch.setattr(animation,'blit_frame',capture)
    appearance=AppearanceController(Catalog())
    assert appearance.select('zombie','dogs','menu')
    animator=Animator(appearance)
    target=pygame.Surface((1050,600),pygame.SRCALPHA)
    zombie={'id':99,'type_id':'zombie_basic','row':2,'x':700,'action':'walking'}
    animator.draw_actor(target,zombie,(700,400),0)
    zombie['action']='biting'
    animator.draw_actor(target,zombie,(700,400),1)
    animator.consume(game.snapshot(),[dict(kind='hit',id=99,tick=2,session_id=game.session_id)])
    animator.draw_actor(target,zombie,(700,400),2)
    animator.deaths.append(dict(type_id='zombie_basic',row=2,x=700,tick=3))
    animator.draw_deaths(target,3,lambda row:400)
    assert len(observed)>=4 and all(observed)


def test_scaled_dog_card_and_preview_fit_their_viewports():
    from pvz_game.presentation.animation import display_scale_for_role
    from pvz_game.presentation.skin_catalog import Catalog
    skin=Catalog().load('dogs_photo')
    # HUD art window is 62 logical pixels high; skin preview window is 156x125.
    for role,card_scale,preview_scale in [('peashooter',.61,.56),('wallnut',.61,.56),('jalapeno',.61,.56)]:
        multiplier=skin.data['roles'][role]['display_scale_multiplier']
        frame=skin.data['roles'][role]['preview']
        image=skin.surface(frame)
        base_width=image.get_width()/skin.pixel_scale
        base_height=image.get_height()/skin.pixel_scale
        final_card=display_scale_for_role(skin,role,card_scale)/skin.pixel_scale
        final_preview=display_scale_for_role(skin,role,preview_scale)/skin.pixel_scale
        assert base_height*final_card<=62
        assert base_width*final_card<=86
        assert base_height*final_preview<=125
        assert base_width*final_preview<=156
        assert multiplier>0


def test_hit_event_plays_hit_clip_then_resumes_base_animation(game):
    appearance=AppearanceController(Catalog())
    appearance.select('zombie','dogs','menu')
    animator=Animator(appearance)
    entity={'id':9001,'type_id':'zombie_basic','action':'walking'}
    target=pygame.Surface((256,256),pygame.SRCALPHA)
    animator.draw_actor(target,entity,(128,200),0)
    event_tick=3
    animator.consume(game.snapshot(),[dict(kind='hit',id=entity['id'],tick=event_tick,
                                           session_id=game.session_id)])
    skin=appearance.skin_for('zombie_basic')
    hit_clip=skin.clip('zombie_basic','hit')
    duration=sum(frame['duration_ticks'] for frame in hit_clip['frames'])
    observed=[]
    for elapsed in range(duration):
        observed.append(animator.draw_actor(target,entity,(128,200),event_tick+elapsed))
    assert observed==[frame_at(hit_clip,tick) for tick in range(duration)]
    paused_frame=animator.draw_actor(target,entity,(128,200),event_tick+duration//2)
    assert paused_frame==observed[duration//2]
    resumed=animator.draw_actor(target,entity,(128,200),event_tick+duration)
    assert resumed==frame_at(skin.clip('zombie_basic','walk'),event_tick+duration)


def test_squash_attack_uses_dog_pose_and_hit_has_visual_feedback(game):
    game.sun=500
    game.step([Command('SelectPlant',('pangbaobao',)),Command('PlantAt',(1,2),sequence=1)])
    squash=game.at(1,2)
    zombie=game.add_zombie(1,x=game.plant_x(squash)+100)
    _,events=game.step()
    start=next(event['tick'] for event in events
               if event['kind']=='action_started' and event.get('action')=='attack')
    appearance=AppearanceController(Catalog())
    assert appearance.select('plant','dogs','menu')
    animator=Animator(appearance)
    animator.consume(game.snapshot(),events)
    skin=appearance.skin_for('pangbaobao')
    drawn=animator.draw_actor(pygame.Surface((1050,600),pygame.SRCALPHA),
                              game.snapshot()['plants'][0],(285,300),game.tick)
    assert drawn==frame_at(skin.clip('pangbaobao','attack'),game.tick-start)

    game.tick=squash.next_action_tick
    _,events=game.step()
    animator.consume(game.snapshot(),events)
    surface=pygame.Surface((1050,600),pygame.SRCALPHA)
    animator.draw_squash_effects(surface,game.tick,game.row_y)
    assert surface.get_bounding_rect().w>0
    assert squash.id not in game.plants and zombie.id not in game.zombies


def test_jalapeno_event_draws_only_a_timed_visual_effect(game):
    pygame.font.init()
    from pvz_game.presentation.renderer import Renderer
    game.phase='playing';game.sun=500
    renderer=Renderer(game.config)
    game.step([Command('SelectPlant',('jalapeno',)),Command('PlantAt',(1,0),sequence=1)])
    snapshot=game.snapshot();events=list(game.events)
    assert any(event['kind']=='row_clear_started' for event in events)
    state=game.snapshot()
    renderer.draw(snapshot,events)
    assert game.snapshot()==state
    assert len(renderer.animator.row_clears)==1
    renderer.animator.draw_row_clear_effects(pygame.Surface((1050,600),pygame.SRCALPHA),1000,
                                               game.config['grid_x'],game.row_y)
    assert renderer.animator.row_clears==[]

def test_target_dog_frames_preserve_full_source_aspect_ratio():
    import json
    from pathlib import Path
    from pvz_game.presentation.skin_catalog import Catalog
    root = Path(__file__).resolve().parents[2]
    skin = Catalog().load('dogs')
    provenance = json.loads((root / 'assets/skins/dogs/provenance.json').read_text(encoding='utf-8-sig'))
    records = {record['role']: record for record in provenance}
    for role in ('sunflower', 'zombie_basic'):
        bboxes = records[role].get('source_bboxes')
        assert bboxes and len(bboxes) == 12
        seen = set()
        for clip in skin.data['roles'][role]['clips'].values():
            for frame in clip['frames']:
                refs = frame.get('source_frames', [])
                if len(refs) != 1:
                    continue
                index = refs[0]
                if index in seen:
                    continue
                seen.add(index)
                source_ratio = bboxes[index][2] / bboxes[index][3]
                visible = skin.surface(frame).get_bounding_rect(min_alpha=1)
                assert visible.w and visible.h
                assert abs((visible.w / visible.h) / source_ratio - 1) < 0.08
        assert seen == set(range(12))
