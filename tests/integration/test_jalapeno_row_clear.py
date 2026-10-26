from pvz_game.domain.commands import Command
from pvz_game.presentation.animation import JALAPENO_IGNITE_DURATION_TICKS
from pvz_game.presentation.skin_catalog import Catalog, AppearanceController
from pvz_game.presentation.animation import Animator, frame_at
import pygame


def test_jalapeno_clears_only_existing_live_zombies_once(game):
    first=game.add_zombie(2,x=700)
    second=game.add_zombie(2,x=800)
    other_row=game.add_zombie(1,x=750)
    dead=game.add_zombie(2,x=760)
    dead.hp=0
    before_kills=game.kills
    _,events=game.step([
        Command("SelectPlant",("jalapeno",),sequence=0),
        Command("PlantAt",(2,4),sequence=1),
    ])
    started=[event for event in events if event["kind"]=="row_clear_started"]
    assert len(started)==1
    assert started[0]["row"]==2 and started[0]["col"]==4
    assert started[0]["zombie_ids"]==(first.id,second.id)
    assert first.id not in game.zombies and second.id not in game.zombies
    assert other_row.id in game.zombies
    assert [event["id"] for event in events if event["kind"]=="died"]==[first.id,second.id]
    assert game.kills==before_kills+2
    assert sum(event["kind"]=="result" for event in events)<=1


def test_spawn_after_row_clear_command_is_not_retroactively_hit(game):
    game.tick=1200
    initial_zombie=game.add_zombie(0,x=700)
    _,events=game.step([
        Command("SelectPlant",("jalapeno",),sequence=0),
        Command("PlantAt",(0,4),sequence=1),
    ])
    born=next(z for z in game.zombies.values() if z.id!=initial_zombie.id)
    assert initial_zombie.id not in game.zombies
    assert born.id in game.zombies
    assert born.id not in next(e for e in events if e["kind"]=="row_clear_started")["zombie_ids"]


def test_failed_placement_wins_over_neither_result_nor_jalapeno_effect(game):
    game.sun=0
    _,events=game.step([
        Command("SelectPlant",("jalapeno",),sequence=0),
        Command("PlantAt",(0,0),sequence=1),
    ])
    assert not any(event["kind"] in ("row_clear_started","hit","died") for event in events)
    assert not game.plants


def test_dog_jalapeno_effect_plays_all_35_source_poses_for_two_seconds(game):
    catalog=Catalog();appearance=AppearanceController(catalog)
    appearance.select('plant','dogs','menu')
    skin=catalog.load('dogs')
    clip=skin.clip('jalapeno','ignite')
    assert len(clip['frames'])==35
    assert [frame['source_frames'] for frame in clip['frames']]==[[i] for i in range(10,45)]
    assert sum(frame['duration_ticks'] for frame in clip['frames'])==JALAPENO_IGNITE_DURATION_TICKS
    assert all(frame_at(clip,tick)==clip['frames'][i]
               for i,frame in enumerate(clip['frames'])
               for tick in [sum(f['duration_ticks'] for f in clip['frames'][:i])])


def test_row_clear_animator_freezes_at_pause_and_resets_on_new_session(game):
    appearance=AppearanceController(Catalog());animator=Animator(appearance)
    appearance.select('plant','dogs','menu')
    snapshot=game.snapshot();animator.consume(snapshot,[])
    event=dict(kind='row_clear_started',tick=game.tick,session_id=game.session_id,
               row=1,col=2,zombie_ids=())
    animator.consume(snapshot,[event])
    target=pygame.Surface((1000,600),pygame.SRCALPHA)
    animator.draw_row_clear_effects(target,game.tick+40,100,game.row_y)
    effect=animator.row_clears[0]
    # Drawing at an unchanged simulation tick leaves the visual age unchanged.
    paused_tick=game.tick+40
    animator.draw_row_clear_effects(target,paused_tick,100,game.row_y)
    assert animator.row_clears[0] is effect
    next_session=dict(game.snapshot());next_session['session_id']=game.session_id+1
    animator.consume(next_session,[])
    assert animator.row_clears==[]


def test_row_clear_effect_does_not_pause_simulation_or_repeat_rule_resolution(game):
    game.phase='playing';game.sun=500
    game.add_zombie(1,x=700)
    _,events=game.step([Command('SelectPlant',('jalapeno',)),Command('PlantAt',(1,4),sequence=1)])
    assert sum(event['kind']=='row_clear_started' for event in events)==1
    before=game.tick
    _,later=game.step()
    assert game.tick==before+1
    assert not any(event['kind']=='row_clear_started' for event in later)
