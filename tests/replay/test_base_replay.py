import json
from pathlib import Path
from pvz_game.config import load
from pvz_game.domain.simulation import Simulation
from pvz_game.domain.commands import Command


def strategy(game):
    commands=[]
    seq=0
    # Only public operations and the actual starting budget; no cheat income.
    for sun in list(game.suns.values()):
        if game.tick < sun.expires_tick:
            commands.append(Command("CollectSun",(sun.id,),sequence=seq))
            seq+=1
    budget=game.sun+sum(s.value for s in game.suns.values() if game.tick<s.expires_tick)
    # Defend each row in spawn order. Two early sunflowers make a useful income.
    plant=None
    if game.tick>=game.ready_tick["sunflower"] and budget>=50:
        for row in range(2):
            if not game.at(row,0):
                plant=("sunflower",row,0)
                break
    if plant is None and game.tick>=game.ready_tick["peashooter"] and budget>=100:
        for row in range(5):
            if not game.at(row,2):
                plant=("peashooter",row,2)
                break
    if plant:
        kind,row,col=plant
        commands.extend([Command("SelectPlant",(kind,),sequence=seq),
                         Command("PlantAt",(row,col),sequence=seq+1)])
    return commands


def replay(frame_ticks,defend):
    game=Simulation(*load())
    game.step([Command("Start")])
    events=[]
    for _ in range(24000//frame_ticks):
        for _ in range(frame_ticks):
            _,batch=game.step(strategy(game) if defend else ())
            events.extend((e["kind"],e["tick"],e.get("id"),e.get("result")) for e in batch)
            if game.phase in ("won","lost"):
                return game,events
    raise AssertionError("Level did not resolve within 400 simulated seconds")


def test_actual_level_is_winnable_and_replay_is_fps_independent():
    slow,events30=replay(2,True)
    fast,events60=replay(1,True)
    assert slow.phase==fast.phase=="won"
    assert events30==events60
    assert slow.tick==fast.tick and slow.sun==fast.sun
    assert slow.kills==12


def test_actual_undefended_level_loses_then_restarts():
    game,_=replay(1,False)
    assert game.phase=="lost"
    assert game.mowers[0].state=="spent"
    game.step([Command("Restart")])
    assert game.phase=="playing" and game.tick==1
    assert game.sun==150 and all(m.state=="ready" for m in game.mowers)


def _plain(value):
    if hasattr(value,"items"):
        return {str(key):_plain(item) for key,item in value.items()}
    if isinstance(value,(list,tuple)):
        return [_plain(item) for item in value]
    return value


def _baseline_replay():
    game=Simulation(*load())
    game.step([Command("Start")])
    events=[]
    snapshots=[]
    for _ in range(24000):
        snapshot,batch=game.step(strategy(game))
        events.extend(_plain(event) for event in batch)
        if game.tick%60==0 or game.phase in ("won","lost"):
            snapshots.append(_plain(snapshot))
        if game.phase in ("won","lost"):
            break
    else:
        raise AssertionError("Baseline replay did not resolve")
    return game,events,snapshots


def _gameplay_projection(snapshot):
    """Ignore animated sun coordinates and optional effect metadata only."""
    value=_plain(snapshot)
    value['ready_tick'].pop('pangbaobao',None)
    value['ready_tick'].pop('huanghuang',None)
    for sun in value['suns']:
        for key in ('x','y','source_kind','start_x','start_y','target_x','target_y','motion_duration_ticks'):
            sun.pop(key,None)
    for zombie in value['zombies']:
        for key in ('slow_until_tick','slow_factor','slow_bite_restore_tick'):
            zombie.pop(key,None)
    for projectile in value['projectiles']:
        projectile.pop('slow_factor',None)
        projectile.pop('slow_duration_ticks',None)
    return value


def test_feature_replay_matches_pre_change_gameplay_baseline():
    fixture_path=Path(__file__).with_name("fixtures")/"004-baseline.json"
    baseline=json.loads(fixture_path.read_text(encoding="utf-8"))
    game,events,snapshots=_baseline_replay()
    assert events==baseline["events"]
    assert [_gameplay_projection(snapshot) for snapshot in snapshots]==[
        _gameplay_projection(snapshot) for snapshot in baseline["snapshots"]]
    assert game.phase==baseline["final_phase"]
    assert game.tick==baseline["final_tick"]
    assert game.sun==baseline["final_sun"]
    assert game.kills==baseline["final_kills"]
    assert _plain(game.snapshot())["mowers"]==baseline["final_mowers"]
