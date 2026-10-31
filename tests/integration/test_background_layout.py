from pvz_game.config import load
from pvz_game.presentation.input import cell_at, logical_position
from pvz_game.presentation.renderer import Renderer


def test_background_keeps_logical_board_and_window_input_mapping():
    config, level = load()
    renderer = Renderer(config)
    renderer.background()

    assert renderer.background_surface.get_size() == (1050, 600)
    assert (config["grid_x"], config["grid_y"]) == (105, 160)
    assert (config["cell_width"], config["cell_height"]) == (72, 76)
    assert level["rows"] == 5 and level["cols"] == 12
    assert renderer.default.ui["background"].get_width() >= 1900
    assert renderer.default.ui["background"].get_height() >= 800

    expected = (2, 5)
    point = (
        config["grid_x"] + (expected[1] + .5) * config["cell_width"],
        config["grid_y"] + (expected[0] + .5) * config["cell_height"],
    )
    for window_size in ((1050, 600), (1260, 720), (1920, 1080)):
        scale = min(window_size[0] / 1050, window_size[1] / 600)
        offset = ((window_size[0] - 1050 * scale) / 2,
                  (window_size[1] - 600 * scale) / 2)
        pixel = tuple(round(offset[index] + point[index] * scale) for index in range(2))
        logical = logical_position(pixel, window_size)
        assert logical is not None
        assert cell_at(logical, config, level["rows"], level["cols"]) == expected


def test_background_image_is_loaded_as_a_cached_static_surface():
    config, _ = load()
    renderer = Renderer(config)
    renderer.background()
    first = renderer.background_surface
    renderer.background()
    assert renderer.background_surface is first
