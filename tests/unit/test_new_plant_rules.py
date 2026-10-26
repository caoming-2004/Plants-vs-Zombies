from pvz_game.domain.commands import Command


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
