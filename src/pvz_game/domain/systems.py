from .models import Projectile


def damage(game, entity, amount):
    if entity.hp <= 0:
        return
    entity.hp = max(0, entity.hp-amount)
    game.emit("hit", id=entity.id, hp=entity.hp)
    if entity.hp == 0:
        entity.action = "dying"
        game.emit("died", id=entity.id, row=entity.row,
                  x=getattr(entity,"x",game.plant_x(entity) if hasattr(entity,"col") else 0),
                  type_id=entity.type_id)
        if entity.id in game.zombies:
            game.kills += 1


def target(game,z):
    cfg = game.zombie_types[z.type_id]
    return next(iter(sorted((p for p in game.plants.values()
                             if p.hp>0 and p.row == z.row and
                             abs(z.x-game.plant_x(p)) <= cfg["contact_distance"]),
                            key=lambda p:(-p.col,p.id))),None)


def advance(game):
    c, t = game.config, game.tick
    while game.next_spawn_index < len(game.spawns) and game.spawns[game.next_spawn_index]["tick"] <= t:
        item = game.spawns[game.next_spawn_index]
        game.add_zombie(item["row"],type_id=item["type_id"])
        game.next_spawn_index += 1
    # The deterministic drop pattern keeps replay independent of random/global time.
    if t % c["natural_sun_interval_ticks"] == 0:
        index = t // c["natural_sun_interval_ticks"]
        game.add_sun(c["grid_x"]+((index*4)%12+.5)*c["cell_width"],
                     game.row_y((index*3)%5)-12,c["sun_value"])
    for item in game.level.get("sun_schedule",[]):
        if item["tick"] == t:
            game.add_sun(item["x"],item["y"],c["sun_value"])
    game.suns = {i:s for i,s in game.suns.items() if t < s.expires_tick}
    old_shots = sorted(game.projectiles.values(),key=lambda p:p.id)
    for z in sorted(game.zombies.values(),key=lambda z:z.id):
        if z.hp <= 0:
            continue
        p = target(game,z)
        z.target_plant_id = p.id if p else None
        z.action = "biting" if p else "walking"
        if not p:
            z.x -= game.zombie_types[z.type_id]["speed"] / c["tick_hz"]
    for shot in old_shots:
        if not shot.active or shot.born_tick >= t:
            continue
        shot.previous_x = shot.x
        shot.x += shot.speed / c["tick_hz"]
        radius = c["zombie_radius"] + c["projectile_radius"]
        candidates = sorted((z for z in game.zombies.values() if z.hp>0 and z.row==shot.row
                             and shot.previous_x-radius <= z.x <= shot.x+radius),
                            key=lambda z:(max(z.x-shot.previous_x,0),z.id))
        if candidates:
            damage(game,candidates[0],shot.damage)
            shot.active = False
        if shot.x > c["spawn_x"] + radius:
            shot.active = False
    for p in sorted(game.plants.values(),key=lambda p:p.id):
        if p.hp <= 0:
            continue
        cfg = game.plant_types[p.type_id]
        p.action = "idle"
        if cfg["role"] == "producer":
            if t >= p.next_action_tick:
                game.add_sun(game.plant_x(p)+20,game.row_y(p.row)-10,cfg["sun_value"])
                p.next_action_tick = t+cfg["production_interval_ticks"]
                p.action = "producing"
                game.emit('action_started',id=p.id,action='produce')
        elif cfg["role"] == "shooter" and any(
                z.hp>0 and z.row==p.row and z.x>game.plant_x(p)
                for z in game.zombies.values()):
            p.action = "attacking"
            if t >= p.next_action_tick:
                x = game.plant_x(p)+22
                shot = Projectile(game.new_id(),p.id,p.row,x,x,cfg["damage"],cfg["projectile_speed"],t)
                game.projectiles[shot.id] = shot
                game.emit("shot",id=p.id,projectile_id=shot.id,row=p.row,x=x)
                p.next_action_tick = t+cfg["attack_interval_ticks"]
    for z in sorted(game.zombies.values(),key=lambda z:z.id):
        if z.hp <= 0:
            continue
        p = target(game,z)
        z.target_plant_id = p.id if p else None
        z.action = "biting" if p else "walking"
        if p and t >= z.next_bite_tick:
            cfg = game.zombie_types[z.type_id]
            damage(game,p,cfg["bite_damage"])
            game.emit("bite",id=z.id,target=p.id)
            z.next_bite_tick = t+cfg["bite_interval_ticks"]
    for mower in game.mowers:
        if mower.state == "ready" and any(z.hp>0 and z.row==mower.row and z.x <= c["mower_trigger_x"]
                                           for z in game.zombies.values()):
            mower.state = "sweeping"
            game.emit("mower_started",row=mower.row)
        if mower.state == "sweeping":
            mower.previous_x = mower.x
            mower.x += c["mower_speed"] / c["tick_hz"]
            for z in sorted(game.zombies.values(),key=lambda z:z.id):
                if z.hp>0 and z.row==mower.row and mower.previous_x-c["zombie_radius"] <= z.x <= mower.x+c["zombie_radius"]:
                    damage(game,z,z.hp)
            if mower.x > c["spawn_x"]+c["zombie_radius"]:
                mower.state = "spent"
    game.plants = {i:p for i,p in game.plants.items() if p.hp>0}
    game.zombies = {i:z for i,z in game.zombies.items() if z.hp>0}
    game.projectiles = {i:p for i,p in game.projectiles.items() if p.active}
    if any(z.x <= c["failure_x"] and game.mowers[z.row].state != "ready" for z in game.zombies.values()):
        game.phase = "lost"
    elif game.next_spawn_index == len(game.spawns) and not game.zombies:
        game.phase = "won"
    if game.phase in ("won","lost"):
        game.emit("result",result=game.phase)
