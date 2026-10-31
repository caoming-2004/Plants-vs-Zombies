from pvz_game.domain.commands import Command
from pvz_game.presentation.input import card_at, click, visible_plant_cards
from pvz_game.presentation.scenes import BUTTONS
from pvz_game.domain.models import Projectile


def plant(game, kind, row=0, col=0):
    return game.step([
        Command("SelectPlant", (kind,), sequence=0),
        Command("PlantAt", (row, col), sequence=1),
    ])


def test_wallnut_blocks_and_releases_the_cell_when_destroyed(game):
    plant(game, "wallnut", col=2)
    wallnut=game.at(0,2)
    zombie=game.add_zombie(0,x=game.plant_x(wallnut)+25)
    game.step()
    assert zombie.target_plant_id==wallnut.id
    assert zombie.x==game.plant_x(wallnut)+25
    wallnut.hp=20
    game.tick=zombie.next_bite_tick
    game.step()
    assert wallnut.id not in game.plants
    before=zombie.x
    game.step()
    assert zombie.x<before and zombie.target_plant_id is None


def test_jalapeno_empty_row_succeeds_without_persistent_plant_or_kill(game):
    before=game.sun
    tick=game.tick
    snapshot,events=plant(game,"jalapeno",row=3,col=5)
    assert game.sun==before-125
    assert game.ready_tick["jalapeno"]==tick+3000
    assert game.at(3,5) is None
    assert snapshot["plants"]==()
    assert [event["kind"] for event in events].count("row_clear_started")==1
    assert not any(event["kind"] in ("hit","died") for event in events)
    assert game.kills==0


def test_jalapeno_failures_do_not_charge_or_start_cooldown(game):
    before=game.sun
    game.step([Command("SelectPlant",("jalapeno",)),Command("PlantAt",(9,0),sequence=1)])
    assert game.sun==before
    assert game.ready_tick["jalapeno"]==0
    game.step([Command("SelectPlant",("jalapeno",)),Command("PlantAt",(0,0),sequence=1)])
    before=game.sun
    ready=game.ready_tick["jalapeno"]
    game.step([Command("SelectPlant",("jalapeno",)),Command("PlantAt",(0,1),sequence=1)])
    assert game.sun==before and game.ready_tick["jalapeno"]==ready
    game.sun=0
    game.tick=ready
    game.step([Command("SelectPlant",("jalapeno",)),Command("PlantAt",(0,2),sequence=1)])
    assert game.sun==0 and game.ready_tick["jalapeno"]==ready


def test_jalapeno_occupied_cell_is_atomic(game):
    plant(game,"sunflower",row=1,col=2)
    before=game.sun
    game.step([Command("SelectPlant",("jalapeno",)),
               Command("PlantAt",(1,2),sequence=1)])
    assert game.sun==before
    assert game.ready_tick["jalapeno"]==0
    assert game.at(1,2).type_id=="sunflower"


def test_new_dog_cards_are_only_selectable_in_dogs_skin(game):
    assert visible_plant_cards('dogs')[-2:]==('pangbaobao','huanghuang')
    assert visible_plant_cards('default')==visible_plant_cards('dogs_photo')==(
        'sunflower','peashooter','wallnut','jalapeno')
    point=tuple(BUTTONS['pangbaobao'][i]+BUTTONS['pangbaobao'][i+2]/2 for i in (0,1))
    assert card_at(point,'dogs')=='pangbaobao'
    assert card_at(point,'default') is None
    assert click(point,game.snapshot(),game.config,skin_id='dogs').args==('pangbaobao',)
    assert click(point,game.snapshot(),game.config,skin_id='default') is None


def test_pangbaobao_squash_waits_for_target_then_hits_once_and_is_consumed(game):
    before=game.sun
    plant(game,'pangbaobao',row=1,col=2)
    dog=game.at(1,2)
    cfg=game.plant_types['pangbaobao']
    assert dog and dog.hp==cfg['hp'] and dog.action=='idle'
    assert game.sun==before-game.plant_types['pangbaobao']['price']
    game.step()
    assert dog.id in game.plants and dog.action=='idle' and dog.target_zombie_id is None
    x=game.plant_x(dog)
    zombie=game.add_zombie(1,x=x+130)
    _,events=game.step()
    assert dog.action=='attacking' and dog.target_zombie_id==zombie.id
    assert any(e['kind']=='action_started' and e.get('action')=='attack' for e in events)
    game.tick=dog.next_action_tick
    _,events=game.step()
    assert dog.id not in game.plants
    assert zombie.id not in game.zombies
    assert [event['kind'] for event in events].count('squash_hit')==1
    assert [event['kind'] for event in events].count('died')==1


def test_huanghuang_uses_snow_shooter_rules_and_new_roles_reject_invalid_planting(game):
    game.sun=500
    before=game.sun
    plant(game,'huanghuang',row=0,col=1)
    shooter=game.at(0,1)
    assert shooter and game.sun==before-game.plant_types['huanghuang']['price']
    zombie=game.add_zombie(0,x=game.config['spawn_x'])
    game.tick=shooter.next_action_tick
    _,events=game.step()
    assert shooter.action=='attacking'
    assert any(event['kind']=='shot' and event['id']==shooter.id for event in events)
    assert game.projectiles
    shot=next(iter(game.projectiles.values()))
    assert shot.slow_factor==game.plant_types['huanghuang']['slow_factor']
    assert shot.slow_duration_ticks==game.plant_types['huanghuang']['slow_duration_ticks']
    for kind in ('pangbaobao','huanghuang'):
        before=game.sun
        game.ready_tick[kind]=game.tick+10
        game.step([Command('SelectPlant',(kind,)),Command('PlantAt',(0,2),sequence=1)])
        results=game.results
        assert not results[1]['accepted'] and results[1]['reason']=='cooldown'
        assert game.sun==before
        game.ready_tick[kind]=0
    game.sun=1000
    for kind in ('pangbaobao','huanghuang'):
        game.ready_tick[kind]=0
        game.step([Command('SelectPlant',(kind,)),Command('PlantAt',(0,1),sequence=1)])
        results=game.results
        assert not results[1]['accepted'] and results[1]['reason']=='occupied'
    game.sun=0
    for kind in ('pangbaobao','huanghuang'):
        game.step([Command('SelectPlant',(kind,)),Command('PlantAt',(4,11),sequence=1)])
        results=game.results
        assert not results[1]['accepted'] and results[1]['reason']=='insufficient_sun'
    assert game.sun==0


def test_ice_hit_refreshes_slow_and_expiry_restores_base_bite_cadence(game):
    game.sun=500
    plant(game,'huanghuang',row=0,col=0)
    shooter=game.at(0,0)
    zombie=game.add_zombie(0,x=game.plant_x(shooter)+120)
    zombie.next_bite_tick=game.tick+15
    original_due=zombie.next_bite_tick
    shot_id=game.new_id()
    game.projectiles[shot_id]=Projectile(
        shot_id,shooter.id,0,zombie.x-20,zombie.x-20,20,6000,
        game.tick-1,slow_factor=.5,slow_duration_ticks=240)
    _,events=game.step()
    assert zombie.hp==180 and zombie.slow_factor==.5
    assert zombie.next_bite_tick>original_due
    assert any(e['kind']=='slowed' for e in events)
    first_expiry=zombie.slow_until_tick
    game.tick=first_expiry-1
    shot_id=game.new_id()
    game.projectiles[shot_id]=Projectile(
        shot_id,shooter.id,0,zombie.x-20,zombie.x-20,20,6000,
        game.tick-1,slow_factor=.5,slow_duration_ticks=240)
    game.step()
    assert zombie.slow_until_tick==first_expiry-1+240
    assert zombie.slow_factor==.5
    restore=zombie.slow_bite_restore_tick
    game.tick=zombie.slow_until_tick
    game.step()
    assert zombie.slow_until_tick==0 and zombie.slow_factor==1
    assert zombie.next_bite_tick==restore
