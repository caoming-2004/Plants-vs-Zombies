"""Deterministic endless wave director. No pygame and no UI."""
import math


class EndlessDirector:
    def __init__(self, level):
        self.settings = dict(level["endless"])
        self.level = level
        self.wave_number = 0

    def reset(self, game):
        self.wave_number = 0

    def _interval(self, index):
        s = self.settings
        return max(s["min_interval_ticks"], s["base_interval_ticks"] - index * 30)

    def _count(self, index):
        s = self.settings
        return min(s["max_zombies_per_wave"], s["base_zombies"] + index * s["zombie_growth"])

    def _types(self, index, count):
        s = self.settings
        fast = min(0.45, s["fast_ratio_base"] + index * s["fast_ratio_growth"])
        tough = min(0.55, s["tough_ratio_base"] + index * s["tough_ratio_growth"])
        fast_count = round(count * fast)
        tough_count = round(count * tough)
        while fast_count + tough_count > count:
            if tough_count: tough_count -= 1
            else: fast_count -= 1
        basic_count = count - fast_count - tough_count
        return (["zombie_basic"] * basic_count + ["zombie_fast"] * fast_count +
                ["zombie_tough"] * tough_count)

    def _append_wave(self, game):
        index = self.wave_number
        self.wave_number += 1
        interval = self._interval(index)
        if game.waves:
            start_tick = max(game.tick + 30, game.waves[-1]["start_tick"] + interval)
        else:
            start_tick = max(game.tick + 30, self.settings["first_wave_tick"])
        count = self._count(index)
        types = self._types(index, count)
        wave_id = "endless_wave_%03d" % self.wave_number
        game.waves.append(dict(id=wave_id, name="第%d波" % self.wave_number,
                               start_tick=start_tick, strength=1 + index * .1))
        gap = max(24, interval // max(1, count))
        for slot, type_id in enumerate(types):
            tick = start_tick + slot * gap
            row = (index * 2 + slot * 3) % game.level["rows"]
            game.spawns.append(dict(tick=tick, row=row, type_id=type_id, wave_id=wave_id))
        game.spawns.sort(key=lambda item: item["tick"])

    def ensure_ahead(self, game):
        while len(game.waves) - game.wave_index < 2:
            self._append_wave(game)


def make_level(campaign):
    endless = dict(campaign["endless"])
    level = dict(
        schema_version=1, id="endless", order=99, name="无尽挑战", mode="endless",
        rows=5, cols=12,
        initial_sun=endless["initial_sun"],
        sky_sun_interval_ticks=endless["sky_sun_interval_ticks"],
        mower_rows=endless.get("mower_rows", [0, 1, 2, 3, 4]),
        max_active_zombies=endless["max_active_zombies"],
        waves=[], spawn_schedule=[], star_goals=[],
        endless=endless,
    )
    if "available_plants" in endless:
        level["available_plants"] = endless["available_plants"]
    return level
