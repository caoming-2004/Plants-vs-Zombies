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


@dataclass
class SunPickup:
    id: int
    x: float
    y: float
    value: int
    expires_tick: int
    born_tick: int
    collected: bool = False


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
