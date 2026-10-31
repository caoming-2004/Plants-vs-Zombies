import os
import uuid
from pathlib import Path
import pytest
from pvz_game.config import load

os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


@pytest.fixture
def progress_path():
    path = Path(__file__).resolve().parents[1] / ".tools" / f"progress-{uuid.uuid4().hex}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    yield path
    path.unlink(missing_ok=True)
    path.with_name(path.name + ".tmp").unlink(missing_ok=True)


@pytest.fixture
def game():
    from pvz_game.domain.simulation import Simulation
    from pvz_game.domain.commands import Command
    game = Simulation(*load())
    game.step([Command("Start")])
    return game
