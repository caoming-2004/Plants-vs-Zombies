from pvz_game.domain.commands import Command
from pvz_game.domain.models import Projectile
from test_economy_and_planting import do, plant


def test_shot_birth_and_next_tick(game):
    plant(game,kind="peashooter")
    p = next(iter(game.plants.values()))
    z = game.add_zombie(0,x=500)
    game.tick = p.next_action_tick
    game.step()
    shot = next(iter(game.projectiles.values()))
    x = shot.x
    assert shot.born_tick == game.tick-1 and shot.previous_x == x
    game.step()
    assert shot.x > x
    assert z.hp == 200


def test_projectile_kill_prevents_bite(game):
    plant(game,kind="peashooter")
    p = next(iter(game.plants.values()))
    z = game.add_zombie(0,x=game.plant_x(p)+30)
    z.hp = 20
    shot = Projectile(game.new_id(),p.id,0,z.x-50,z.x-50,20,6000,game.tick-1)
    game.projectiles[shot.id] = shot
    game.step()
    assert z.id not in game.zombies and p.hp == 300


def test_same_distance_stable_id_and_no_double_hit(game):
    a = game.add_zombie(0, x=500)
    b = game.add_zombie(0, x=500)
    a.hp = b.hp = 20
    for _ in range(2):
        shot = Projectile(game.new_id(),0,0,400,400,20,12000,game.tick-1)
        game.projectiles[shot.id] = shot
    game.step()
    deaths = [e["id"] for e in game.events if e["kind"] == "died"]
    assert deaths == [a.id,b.id]


def test_wrong_row_not_hit_and_dead_source_shot_continues(game):
    z = game.add_zombie(1,x=450)
    shot = Projectile(game.new_id(),999,0,400,400,20,6000,game.tick-1)
    game.projectiles[shot.id] = shot
    game.step()
    assert z.hp == 200 and shot.x > 400


def test_mower_once_and_next_breach_loses(game):
    game.add_zombie(0,x=game.config["mower_trigger_x"])
    game.step()
    assert game.mowers[0].state == "sweeping"
    assert all(m.state == "ready" for m in game.mowers[1:])
    game.add_zombie(0,x=game.config["failure_x"]-1)
    game.step()
    assert game.phase == "lost"


def test_mower_multiple_and_cross_row(game):
    for _ in range(2): game.add_zombie(0,x=72)
    game.add_zombie(1,x=72)
    game.step()
    assert not game.zombies
    assert [m.state for m in game.mowers[:2]] == ["sweeping","sweeping"]
    assert sum(e["kind"] == "mower_started" for e in game.events) == 2


def test_pause_restart_and_stale_commands(game):
    plant(game)
    old_id = game.session_id
    do(game,"Pause")
    frozen = game.snapshot()
    for _ in range(100): game.step()
    assert game.snapshot() == frozen
    do(game,"Resume")
    do(game,"Restart")
    assert game.session_id != old_id and not game.plants
    assert game.sun == 150 and all(m.state == "ready" for m in game.mowers)
    game.step([Command("SelectShovel",session_id=old_id)])
    assert game.selection.kind == "none" and game.results[0]["reason"] == "stale_session"


def test_last_kill_wins_once(game):
    game.next_spawn_index = len(game.spawns)
    game.step()
    assert game.phase == "won"
    game.step()
    assert not game.events


def test_no_mower_loss_priority(game):
    game.next_spawn_index = len(game.spawns)
    game.mowers[0].state = "spent"
    game.add_zombie(0,x=20)
    game.step()
    assert game.phase == "lost"
