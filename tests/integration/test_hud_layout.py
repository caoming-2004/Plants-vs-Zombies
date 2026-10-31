from pvz_game.config import load
from pvz_game.domain.commands import Command
from pvz_game.domain.simulation import Simulation
from pvz_game.presentation.scenes import BUTTONS, HUD_STATUS_RECT, HUD_SUN_RECT


def _rects_intersect(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return not (ax + aw <= bx or bx + bw <= ax or ay + ah <= by or by + bh <= ay)


def test_status_strip_stays_outside_lawn_and_hud_buttons():
    config, level = load()
    lawn = (config['grid_x'], config['grid_y'], level['cols'] * config['cell_width'],
            level['rows'] * config['cell_height'])
    assert not _rects_intersect(HUD_STATUS_RECT, lawn)
    for key in ('shovel', 'pause', 'sunflower', 'peashooter', 'wallnut', 'jalapeno',
                'pangbaobao', 'huanghuang'):
        assert not _rects_intersect(HUD_STATUS_RECT, BUTTONS[key])
    assert not _rects_intersect(HUD_STATUS_RECT, HUD_SUN_RECT)
    assert HUD_STATUS_RECT[1] + HUD_STATUS_RECT[3] <= lawn[1] - 8


def test_wave_preview_matches_real_spawns_and_lead_time():
    config, level = load()
    game = Simulation(config, level)
    game.step([Command("Start")])
    preview = game.wave_preview()
    assert preview is not None
    expected = [spawn for spawn in level['spawn_schedule'] if spawn['wave_id'] == preview['wave_id']]
    assert preview['total'] == len(expected)
    assert preview['type_counts'] == {
        type_id: sum(1 for spawn in expected if spawn['type_id'] == type_id)
        for type_id in {spawn['type_id'] for spawn in expected}
    }
    assert preview['rows'] == sorted({spawn['row'] for spawn in expected})
    assert preview['lead_ticks'] >= 120
