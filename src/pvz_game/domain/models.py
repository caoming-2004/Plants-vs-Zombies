from dataclasses import dataclass
from types import MappingProxyType
from collections.abc import Mapping


def freeze(value):
    if isinstance(value, Mapping):
        return MappingProxyType({key: freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(freeze(item) for item in value)
    return value


@dataclass
class Plant:
    id: int
    type_id: str
    row: int
    col: int
    hp: int
    next_action_tick: int
    action: str = "idle"
    target_zombie_id: int | None = None


@dataclass
class Zombie:
    id: int
    type_id: str
    row: int
    x: float
    hp: int
    next_bite_tick: int = 0
    target_plant_id: int | None = None
    action: str = "walking"
    slow_until_tick: int = 0
    slow_factor: float = 1.0
    slow_bite_restore_tick: int | None = None
    wave_id: str | None = None


@dataclass
class Projectile:
    id: int
    source_id: int
    row: int
    x: float
    previous_x: float
    damage: int
    speed: float
    born_tick: int
    active: bool = True
    slow_factor: float | None = None
    slow_duration_ticks: int = 0


@dataclass
class SunPickup:
    id: int
    x: float
    y: float
    value: int
    expires_tick: int
    born_tick: int
    collected: bool = False
    source_kind: str = "plant"
    start_x: float | None = None
    start_y: float | None = None
    target_x: float | None = None
    target_y: float | None = None
    motion_duration_ticks: int | None = None
    arc_height: float = 0.0


@dataclass
class LawnMower:
    row: int
    x: float
    previous_x: float
    state: str = "ready"


@dataclass(frozen=True)
class Selection:
    kind: str = "none"
    type_id: str | None = None


@dataclass
class AppearanceSelection:
    plant_skin_id: str = "default"
    zombie_skin_id: str = "default"
