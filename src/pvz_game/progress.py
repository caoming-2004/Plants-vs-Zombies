"""Local campaign progress; no gameplay rules live here."""
from pathlib import Path
import json
import math
import os

from .resources import user_data_dir

SCHEMA_VERSION = 2
DEFAULT_BACKGROUND_ID = "day"


def default_progress():
    return {
        "schema_version": SCHEMA_VERSION,
        "unlocked": ["day_01"],
        "levels": {},
        "endless": {"unlocked": False, "best_wave": 0, "best_kills": 0},
        "settings": {"background_id": DEFAULT_BACKGROUND_ID,
                     "music_enabled": True, "music_volume": 0.55},
    }


def _valid_record(record):
    if not isinstance(record, dict):
        return False
    if not isinstance(record.get("cleared"), bool):
        return False
    stars = record.get("best_stars", 0)
    if type(stars) is not int or stars < 0:
        return False
    ticks = record.get("best_ticks")
    if ticks is not None and (type(ticks) is not int or ticks <= 0):
        return False
    return True


class Progress:
    def __init__(self, data, path=None, recovered=False):
        self.data = data
        self.path = Path(path) if path is not None else user_data_dir() / "progress.json"
        self.recovered = recovered

    @classmethod
    def load(cls, path=None):
        target = Path(path) if path is not None else user_data_dir() / "progress.json"
        if not target.is_file():
            return cls(default_progress(), target, recovered=False)
        try:
            data = json.loads(target.read_text(encoding="utf-8-sig"))
            if not isinstance(data, dict) or data.get("schema_version") not in (1, SCHEMA_VERSION):
                raise ValueError("progress schema")
            if data.get("schema_version") == 1:
                data["schema_version"] = SCHEMA_VERSION
                data.setdefault("settings", {})
            settings = data.setdefault("settings", {})
            if not isinstance(settings, dict):
                raise ValueError("settings")
            background = settings.get("background_id", DEFAULT_BACKGROUND_ID)
            if not isinstance(background, str) or not background:
                raise ValueError("background_id")
            settings["background_id"] = background
            enabled = settings.get("music_enabled", True)
            settings["music_enabled"] = enabled if type(enabled) is bool else True
            volume = settings.get("music_volume", 0.55)
            if (isinstance(volume, bool) or not isinstance(volume, (int, float))
                    or not math.isfinite(volume) or not 0 <= volume <= 1):
                volume = 0.55
            settings["music_volume"] = float(volume)
            unlocked = data.get("unlocked")
            levels = data.get("levels")
            endless = data.get("endless")
            if not isinstance(unlocked, list) or any(not isinstance(i, str) for i in unlocked):
                raise ValueError("unlocked")
            if not isinstance(levels, dict) or any(not _valid_record(record) for record in levels.values()):
                raise ValueError("levels")
            if not isinstance(endless, dict) or not isinstance(endless.get("unlocked"), bool):
                raise ValueError("endless")
            for key in ("best_wave", "best_kills"):
                if type(endless.get(key)) is not int or endless[key] < 0:
                    raise ValueError("endless values")
            if "day_01" not in unlocked:
                unlocked.append("day_01")
            return cls(data, target)
        except (OSError, ValueError, TypeError):
            return cls(default_progress(), target, recovered=True)

    def save(self):
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.path.with_name(self.path.name + ".tmp")
            temporary.write_text(json.dumps(self.data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            os.replace(temporary, self.path)
            return True
        except OSError:
            return False

    @property
    def background_id(self):
        return self.data.get("settings", {}).get("background_id", DEFAULT_BACKGROUND_ID)

    def set_background(self, background_id):
        self.data.setdefault("settings", {})["background_id"] = background_id

    @property
    def music_enabled(self):
        return self.data.get("settings", {}).get("music_enabled", True)

    @property
    def music_volume(self):
        return self.data.get("settings", {}).get("music_volume", 0.55)

    def set_music_enabled(self, enabled):
        self.data.setdefault("settings", {})["music_enabled"] = bool(enabled)

    def set_music_volume(self, volume):
        if isinstance(volume, bool) or not isinstance(volume, (int, float)) or not math.isfinite(volume):
            raise ValueError("music volume must be finite")
        self.data.setdefault("settings", {})["music_volume"] = min(1.0, max(0.0, float(volume)))

    def is_unlocked(self, level_id):
        return level_id in self.data["unlocked"]

    @property
    def endless_unlocked(self):
        return bool(self.data["endless"]["unlocked"])

    def record_win(self, level_id, stages, stars=0, ticks=None):
        if level_id not in stages:
            return False
        self.data["unlocked"] = list(dict.fromkeys([*self.data["unlocked"], level_id]))
        record = self.data["levels"].setdefault(
            level_id, {"cleared": False, "best_stars": 0, "best_ticks": None}
        )
        record["cleared"] = True
        record["best_stars"] = max(record.get("best_stars", 0), max(0, int(stars)))
        if ticks is not None:
            old = record.get("best_ticks")
            record["best_ticks"] = int(ticks) if old is None else min(old, int(ticks))
        index = stages.index(level_id)
        if index + 1 < len(stages):
            next_id = stages[index + 1]
            if next_id not in self.data["unlocked"]:
                self.data["unlocked"].append(next_id)
        else:
            self.data["endless"]["unlocked"] = True
        return True

    def record_endless(self, waves, kills):
        self.data["endless"]["unlocked"] = True
        self.data["endless"]["best_wave"] = max(self.data["endless"]["best_wave"], max(0, int(waves)))
        self.data["endless"]["best_kills"] = max(self.data["endless"]["best_kills"], max(0, int(kills)))
        return True
