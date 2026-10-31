from .models import Projectile
import math


def damage(game, entity, amount):
    if entity.hp <= 0:
        return
    entity.hp = max(0, entity.hp-amount)
    game.emit("hit", id=entity.id, hp=entity.hp)
    if entity.hp == 0:
        entity.action = "dying"
        if entity.id in game.plants:
            game.stats["plants_lost"] += 1
        game.emit("died", id=entity.id, row=entity.row,
                  x=getattr(entity,"x",game.plant_x(entity) if hasattr(entity,"col") else 0),
                  type_id=entity.type_id)
        if entity.id in game.zombies:
            game.kills += 1


def target(game,z):
    cfg = game.zombie_types[z.type_id]
    return min((p for p in game.plants.values()
                if p.hp>0 and p.row == z.row and
                abs(z.x-game.plant_x(p)) <= cfg["contact_distance"]),
               key=lambda p:(-p.col,p.id),default=None)


def _apply_slow(game, zombie, shot, tick):
    if shot.slow_factor is None or shot.slow_duration_ticks <= 0:
        return
    was_slowed = tick < zombie.slow_until_tick
    if not was_slowed:
        zombie.slow_bite_restore_tick = zombie.next_bite_tick
        if zombie.next_bite_tick <= tick:
            base = game.zombie_types[zombie.type_id]["bite_interval_ticks"]
            delay = math.ceil(base / shot.slow_factor)
        else:
            delay = math.ceil((zombie.next_bite_tick - tick) / shot.slow_factor)
        zombie.next_bite_tick = tick + delay
    zombie.slow_factor = min(zombie.slow_factor, shot.slow_factor) if was_slowed else shot.slow_factor
    zombie.slow_until_tick = tick + shot.slow_duration_ticks
    game.emit("slowed", id=zombie.id, until_tick=zombie.slow_until_tick,
              slow_factor=zombie.slow_factor)


def _update_suns(game, tick):
    for sun in game.suns.values():
        duration = sun.motion_duration_ticks
        if duration is None:
            continue
        age = max(0, tick - sun.born_tick + 1)
        if duration > 0 and age < duration:
            progress = age / duration
            eased = 1 - (1 - progress) ** 3
            sun.x = sun.start_x + (sun.target_x - sun.start_x) * eased
            linear_y = sun.start_y + (sun.target_y - sun.start_y) * eased
            sun.y = linear_y - sun.arc_height * 4 * progress * (1-progress)
        else:
            sun.x = sun.target_x
            sun.y = sun.target_y + math.sin((age - duration) * math.tau / 120) * 3


def advance(game):
    c, t = game.config, game.tick
    while game.wave_index < len(game.waves) and game.waves[game.wave_index]['start_tick'] <= t:
        wave=game.waves[game.wave_index]
        game.wave_index += 1
        game.current_wave_id=wave['id']
        game.emit('wave_started',wave_id=wave['id'],name=wave['name'],
                  wave_index=game.wave_index,wave_count=len(game.waves))
    max_active = game.level.get("max_active_zombies")
    while game.next_spawn_index < len(game.spawns) and game.spawns[game.next_spawn_index]["tick"] <= t:
        if max_active and sum(1 for zombie in game.zombies.values() if zombie.hp > 0) >= max_active:
            break
        item = game.spawns[game.next_spawn_index]
        game.add_zombie(item["row"],type_id=item["type_id"],wave_id=item.get('wave_id'))
        game.next_spawn_index += 1
    # The deterministic drop pattern keeps replay independent of random/global time.
    sun_interval = game.level.get("sky_sun_interval_ticks", c["natural_sun_interval_ticks"])
    if t % sun_interval == 0:
        index = t // sun_interval
        x = c["grid_x"]+((index*4)%12+.5)*c["cell_width"]
        y = game.row_y((index*3)%5)-12
        game.add_sun(x,y,c["sun_value"],"sky",start=(x,-28),motion_duration_ticks=90)
    for item in game.level.get("sun_schedule",[]):
        if item["tick"] == t:
            game.add_sun(item["x"],item["y"],c["sun_value"],"sky",
                         start=(item["x"],-28),motion_duration_ticks=90)
    game.suns = {i:s for i,s in game.suns.items() if t < s.expires_tick}
    _update_suns(game,t)
    old_shots = sorted(game.projectiles.values(),key=lambda p:p.id)
    for z in sorted(game.zombies.values(),key=lambda z:z.id):
        if z.hp <= 0:
            continue
        if z.slow_until_tick and t >= z.slow_until_tick:
            z.slow_until_tick = 0
            z.slow_factor = 1.0
            if z.slow_bite_restore_tick is not None:
                z.next_bite_tick = z.slow_bite_restore_tick
            z.slow_bite_restore_tick = None
        p = target(game,z)
        z.target_plant_id = p.id if p else None
        z.action = "biting" if p else "walking"
        if not p:
            speed = game.zombie_types[z.type_id]["speed"] * (z.slow_factor if z.slow_until_tick > t else 1)
            z.x -= speed / c["tick_hz"]
    for shot in old_shots:
        if not shot.active or shot.born_tick >= t:
            continue
        shot.previous_x = shot.x
        shot.x += shot.speed / c["tick_hz"]
        radius = c["zombie_radius"] + c["projectile_radius"]
        candidate = min((z for z in game.zombies.values() if z.hp>0 and z.row==shot.row
                         and shot.previous_x-radius <= z.x <= shot.x+radius),
                        key=lambda z:(max(z.x-shot.previous_x,0),z.id),default=None)
        if candidate is not None:
            damage(game,candidate,shot.damage)
            _apply_slow(game,candidate,shot,t)
            shot.active = False
        if shot.x > c["spawn_x"] + radius:
            shot.active = False
    for p in sorted(game.plants.values(),key=lambda p:p.id):
        if p.hp <= 0:
            continue
        cfg = game.plant_types[p.type_id]
        p.action = "idle"
        if cfg["role"] == "squash":
            plant_x=game.plant_x(p)
            if p.target_zombie_id is not None:
                target_zombie=game.zombies.get(p.target_zombie_id)
                in_range=(target_zombie is not None and target_zombie.hp>0
                          and target_zombie.row==p.row
                          and abs(target_zombie.x-plant_x)<=cfg["attack_distance"])
                if not in_range:
                    p.target_zombie_id=None
                    p.next_action_tick=t
                elif t>=p.next_action_tick:
                    damage(game,target_zombie,cfg["damage"])
                    game.emit("squash_hit",id=p.id,target_id=target_zombie.id,row=p.row,x=plant_x)
                    del game.plants[p.id]
                    continue
                else:
                    p.action="attacking"
                    continue
            targets=sorted((z for z in game.zombies.values()
                            if z.hp>0 and z.row==p.row
                            and abs(z.x-plant_x)<=cfg["attack_distance"]),
                           key=lambda z:(abs(z.x-plant_x),z.id))
            if targets:
                p.target_zombie_id=targets[0].id
                p.next_action_tick=t+cfg["attack_duration_ticks"]
                p.action="attacking"
                game.emit("action_started",id=p.id,action="attack",target_id=targets[0].id)
            continue
        if cfg["role"] == "producer":
            if t >= p.next_action_tick:
                x,y=game.plant_x(p)+20,game.row_y(p.row)-10
                source_x=game.plant_x(p)+14
                source_y=game.row_y(p.row)-34
                game.add_sun(x+14,y,cfg["sun_value"],"plant",
                             start=(source_x,source_y),motion_duration_ticks=42,
                             arc_height=26)
                p.next_action_tick = t+cfg["production_interval_ticks"]
                p.action = "producing"
                game.emit('action_started',id=p.id,action='produce')
        elif cfg["role"] in ("shooter","snow_shooter") and any(
                z.hp>0 and z.row==p.row and z.x>game.plant_x(p)
                for z in game.zombies.values()):
            p.action = "attacking"
            if t >= p.next_action_tick:
                x = game.plant_x(p)+22
                shot = Projectile(game.new_id(),p.id,p.row,x,x,cfg["damage"],cfg["projectile_speed"],t,
                                  slow_factor=cfg.get("slow_factor"),
                                  slow_duration_ticks=cfg.get("slow_duration_ticks",0))
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
            if z.slow_until_tick > t:
                interval = math.ceil(cfg["bite_interval_ticks"] / z.slow_factor)
                z.next_bite_tick = t+interval
                z.slow_bite_restore_tick = t+cfg["bite_interval_ticks"]
            else:
                z.next_bite_tick = t+cfg["bite_interval_ticks"]
    for mower in game.mowers:
        if mower.state == "ready" and any(z.hp>0 and z.row==mower.row and z.x <= c["mower_trigger_x"]
                                           for z in game.zombies.values()):
            mower.state = "sweeping"
            game.stats["mowers_used"] += 1
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
    elif game.level.get("mode") != "endless" and game.next_spawn_index == len(game.spawns) and not game.zombies:
        game.phase = "won"
    if game.phase in ("won","lost"):
        game.emit("result",result=game.phase)
