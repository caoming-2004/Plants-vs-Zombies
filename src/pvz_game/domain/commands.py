from dataclasses import dataclass


@dataclass(frozen=True)
class Command:
    kind: str
    args: tuple = ()
    session_id: int | None = None
    tick: int | None = None
    sequence: int = 0
