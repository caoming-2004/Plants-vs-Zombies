from dataclasses import asdict
from copy import deepcopy
from .models import Plant, Zombie, SunPickup, LawnMower, Selection, AppearanceSelection, freeze
from . import systems
from .endless import EndlessDirector
from .plant_rules import placement_reason


class Simulation:
    """The sole owner of gameplay state. All timing uses simulation ticks."""

    def __init__(self, config, level):
        self.config, self.level = deepcopy(config), deepcopy(level)
        self.plant_types = {p["id"]: p for p in self.config["plant_types"]}
        self.zombie_types = {z["id"]: z for z in self.config["zombie_types"]}
        self.spawns = sorted(self.level["spawn_schedule"], key=lambda s: s["tick"])
        self.waves = sorted(self.level.get('waves',()),key=lambda wave:wave['start_tick'])
        self.appearance = AppearanceSelection()
        self.director = EndlessDirector(self.level) if self.level.get("mode") == "endless" else None
        self.session_id = 0
        self.reset("menu")

    def reset(self, phase="playing"):
        self.session_id += 1
        self.tick = 0
        self.phase = phase
        self.spawns = sorted(self.level["spawn_schedule"], key=lambda item: item["tick"])
        self.waves = sorted(self.level.get("waves", ()), key=lambda wave: wave["start_tick"])
        self.sun = self.level.get("initial_sun", self.config["initial_sun"])
        self.selection = Selection()
        self.plants, self.zombies, self.projectiles, self.suns = {}, {}, {}, {}
        x = self.config["mower_trigger_x"]
        self.mowers = [LawnMower(r, x, x) for r in range(self.level["rows"])]
        mower_rows = set(self.level.get("mower_rows", range(self.level["rows"])))
        for mower in self.mowers:
            if mower.row not in mower_rows:
                mower.state = "spent"
        self.available_plants = set(self.level.get("available_plants", self.plant_types))
        self.ready_tick = {key: 0 for key in self.plant_types}
        self.next_spawn_index = self.wave_index = self.event_seq = self._next_id = 0
        self.current_wave_id = None
        self.events, self.results = [], []
        self.kills = 0
        self.stats = dict(sun_collected=0, plants_placed=0, mowers_used=0, plants_lost=0)
        if self.director is not None:
            self.director.reset(self)

    def new_id(self):
        self._next_id += 1
        return self._next_id

    def emit(self, kind, **data):
        self.event_seq += 1
        self.events.append(dict(kind=kind, session_id=self.session_id,
                                event_seq=self.event_seq, tick=self.tick, **data))

    def plant_x(self, plant):
        return self.config["grid_x"] + (plant.col+.5)*self.config["cell_width"]

    def row_y(self, row):
        return self.config["grid_y"] + (row+.5)*self.config["cell_height"]

    def add_sun(self, x, y, value, source_kind="plant", *, start=None,
                motion_duration_ticks=None,arc_height=0):
        start_x, start_y = start if start is not None else (x, y)
        sun = SunPickup(self.new_id(), x, y, value,
                        self.tick+self.config["sun_lifetime_ticks"], self.tick,
                        source_kind=source_kind, start_x=start_x, start_y=start_y,
                        target_x=x, target_y=y,
                        motion_duration_ticks=motion_duration_ticks,
                        arc_height=arc_height)
        sun.x, sun.y = start_x, start_y
        self.suns[sun.id] = sun
        self.emit("sun_created", id=sun.id, x=x, y=y)
        return sun

    def add_zombie(self, row, x=None, type_id="zombie_basic",wave_id=None):
        z = Zombie(self.new_id(), type_id, row,
                   self.config["spawn_x"] if x is None else x,
                   self.zombie_types[type_id]["hp"],wave_id=wave_id)
        self.zombies[z.id] = z
        return z

    def at(self, row, col):
        return next((p for p in self.plants.values() if p.row == row and p.col == col and p.hp>0), None)

    def command(self, cmd):
        if cmd.session_id is not None and cmd.session_id != self.session_id:
            return "stale_session"
        if cmd.tick is not None and cmd.tick != self.tick:
            return "stale_tick"
        kind, args = cmd.kind, cmd.args
        if kind == "Quit":
            self.phase = "quit"
            return None
        if kind == "Start" and self.phase == "menu":
            self.reset()
            return None
        if kind == "Restart" and self.phase in ("playing", "won", "lost"):
            self.reset()
            return None
        if kind == "ReturnToMenu" and self.phase in ("playing", "won", "lost"):
            self.reset("menu")
            return None
        if kind == "Resume" and self.phase == "paused":
            self.phase = "playing"
            return None
        if self.phase != "playing":
            return "wrong_phase"
        if kind == "Pause":
            self.phase = "paused"
        elif kind == "CancelSelection":
            self.selection = Selection()
        elif kind == "SelectPlant":
            if not args or args[0] not in self.plant_types:
                return "invalid_type"
            if args[0] not in self.available_plants:
                return "unavailable"
            self.selection = Selection("plant", args[0])
        elif kind == "SelectShovel":
            self.selection = Selection("shovel")
        elif kind == "CollectSun":
            s = self.suns.get(args[0]) if args else None
            if s is None or s.collected:
                return "sun_missing"
            if self.tick >= s.expires_tick:
                return "sun_expired"
            self.sun += s.value
            self.stats["sun_collected"] += s.value
            s.collected = True
            del self.suns[s.id]
            self.emit("collected", id=s.id, amount=s.value)
        elif kind in ("PlantAt", "ShovelAt"):
            if len(args) != 2 or any(type(v) is not int for v in args):
                return "out_of_bounds"
            row, col = args
            if not (0 <= row < self.level["rows"] and 0 <= col < self.level["cols"]):
                return "out_of_bounds"
            if kind == "ShovelAt":
                if self.selection.kind != "shovel":
                    return "no_selection"
                p = self.at(row,col)
                if p:
                    self.emit("removed", id=p.id, row=row, col=col)
                    del self.plants[p.id]
                return None
            if self.selection.kind != "plant":
                return "no_selection"
            type_id = self.selection.type_id
            if type_id not in self.available_plants:
                return "unavailable"
            reason = placement_reason(self.snapshot(), self.plant_types,
                                      self.level["rows"], self.level["cols"],
                                      type_id, row, col)
            if reason is not None:
                return reason
            cfg = self.plant_types[type_id]
            if cfg["role"] == "row_clearer":
                targets=sorted((z for z in self.zombies.values()
                                if z.hp>0 and z.row==row),key=lambda z:z.id)
                self.sun -= cfg["price"]
                self.ready_tick[type_id] = self.tick + cfg["cooldown_ticks"]
                self.selection = Selection()
                effect_id=self.new_id()
                self.emit("row_clear_started",effect_id=effect_id,type_id=type_id,
                          row=row,col=col,zombie_ids=[z.id for z in targets])
                for zombie in targets:
                    systems.damage(self,zombie,zombie.hp)
                self.stats["plants_placed"] += 1
                return None
            interval = cfg.get("production_interval_ticks", cfg.get("attack_interval_ticks", 0))
            p = Plant(self.new_id(),type_id,row,col,cfg["hp"],self.tick+interval)
            self.plants[p.id] = p
            self.sun -= cfg["price"]
            self.ready_tick[type_id] = self.tick + cfg["cooldown_ticks"]
            self.selection = Selection()
            self.stats["plants_placed"] += 1
            self.emit("planted", id=p.id, row=row, col=col)
        else:
            return "invalid_command"
        return None

    def step(self, commands=(), *, include_snapshot=True):
        self.events, self.results = [], []
        for cmd in sorted(commands, key=lambda c:c.sequence):
            reason = self.command(cmd)
            self.results.append(dict(accepted=reason is None, reason=reason, command=cmd.kind))
        if self.phase == "playing":
            if self.director is not None:
                self.director.ensure_ahead(self)
            systems.advance(self)
            self.tick += 1
        snapshot = self.snapshot() if include_snapshot else None
        return snapshot, tuple(freeze(e) for e in self.events)

    def run_stats(self):
        return dict(self.stats, elapsed_ticks=self.tick)

    def wave_preview(self):
        if self.wave_index >= len(self.waves):
            return None
        wave = self.waves[self.wave_index]
        spawns = [item for item in self.spawns if item.get("wave_id") == wave["id"]]
        type_counts = {}
        for item in spawns:
            type_counts[item["type_id"]] = type_counts.get(item["type_id"], 0) + 1
        return dict(wave_id=wave["id"], name=wave["name"], start_tick=wave["start_tick"],
                    total=len(spawns), type_counts=type_counts,
                    rows=sorted({item["row"] for item in spawns}),
                    lead_ticks=max(0, wave["start_tick"] - self.tick))

    def snapshot(self):
        def entities(items):
            return [asdict(e) for e in items.values()]
        return freeze(dict(session_id=self.session_id, phase=self.phase, tick=self.tick,
                           sun=self.sun, selection=asdict(self.selection), ready_tick=self.ready_tick,
                           plants=entities(self.plants), zombies=entities(self.zombies),
                           projectiles=entities(self.projectiles), suns=entities(self.suns),
                           mowers=[asdict(m) for m in self.mowers],
                           next_spawn_index=self.next_spawn_index, total_spawns=len(self.spawns), kills=self.kills,
                           current_wave=self.current_wave_id,wave_index=self.wave_index,
                           wave_count=len(self.waves)))
