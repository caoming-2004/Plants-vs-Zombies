import json
import sys
from pathlib import Path

import pygame

from pvz_game.config import load_campaign
from pvz_game.domain import campaign as rules
from pvz_game.domain.commands import Command
from pvz_game.domain.simulation import Simulation
from pvz_game.presentation.input import click
from pvz_game.presentation.renderer import Renderer
from pvz_game.presentation.scenes import BUTTONS
from pvz_game.presentation.skin_catalog import AppearanceController, Catalog
from pvz_game.progress import Progress

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tests' / 'replay'))
from test_base_replay import strategy


def _play_day_one(config, level):
    game = Simulation(config, level)
    game.step([Command("Start")])
    for _ in range(24000):
        game.step(strategy(game))
        if game.phase in ('won', 'lost'):
            return game
    raise AssertionError('day_01 did not finish')


def test_twenty_real_day_one_clears_keep_result_flow_stable(progress_path):
    config, campaign, levels = load_campaign()
    progress = Progress.load(progress_path)
    pygame.init()
    pygame.display.set_mode((1050, 600))
    renderer = Renderer(config, AppearanceController(Catalog()))
    for index in range(20):
        game = _play_day_one(config, levels['day_01'])
        assert game.phase == 'won', index
        stats = game.run_stats()
        stars = rules.evaluate_stars(levels['day_01'], stats)
        assert progress.record_win('day_01', campaign['stages'], len(stars), stats['elapsed_ticks'])
        assert progress.save()
        assert progress.is_unlocked('day_02')
        assert progress.data['levels']['day_01']['cleared'] is True
        # The next level must load as a fresh board.
        next_game = Simulation(config, levels['day_02'])
        next_game.step([Command("Start")])
        assert next_game.phase == 'playing'
        assert not next_game.plants and not next_game.zombies
    won = game.snapshot()
    canvas = renderer.draw(won, level=levels['day_01'], campaign=campaign, levels=levels,
                           progress=progress, result_stars=stars,
                           next_level_id=rules.next_stage(campaign, 'day_01'))
    assert canvas.get_size() == (1050, 600)
    assert progress.data['levels']['day_01']['best_stars'] <= 2


def test_result_buttons_and_corrupt_progress_are_recoverable(progress_path):
    config, campaign, levels = load_campaign()
    game = _play_day_one(config, levels['day_01'])
    won = game.snapshot()
    assert click((BUTTONS['next_level'][0] + 10, BUTTONS['next_level'][1] + 10), won, config, level=levels['day_01']) == 'next_level'
    assert click((BUTTONS['restart'][0] + 10, BUTTONS['restart'][1] + 10), won, config, level=levels['day_01']).kind == 'Restart'
    assert click((BUTTONS['menu'][0] + 10, BUTTONS['menu'][1] + 10), won, config, level=levels['day_01']).kind == 'ReturnToMenu'
    progress_path.write_text('{broken', encoding='utf-8')
    recovered = Progress.load(progress_path)
    assert recovered.recovered is True
    assert recovered.is_unlocked('day_01')
