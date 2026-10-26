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
