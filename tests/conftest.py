import os
import pytest
from pvz_game.config import load

os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


@pytest.fixture
def game():
    from pvz_game.domain.simulation import Simulation
    from pvz_game.domain.commands import Command
    game = Simulation(*load())
    game.step([Command("Start")])
    return game
