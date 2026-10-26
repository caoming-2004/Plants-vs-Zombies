import pytest

from pvz_game.domain.plant_rules import placement_reason


@pytest.fixture
def placement_state():
    return {
        "phase": "playing",
        "tick": 120,
        "sun": 75,
        "plants": [{"id": 1, "type_id": "sunflower", "row": 1, "col": 2, "hp": 300}],
        "ready_tick": {"sunflower": 0, "wallnut": 180},
    }


@pytest.fixture
def plant_types():
    return {
        "sunflower": {"price": 50},
        "wallnut": {"price": 50},
        "jalapeno": {"price": 125},
    }


def test_legal_empty_cell_is_valid(placement_state, plant_types):
    assert placement_reason(placement_state, plant_types, 5, 12, "sunflower", 4, 11) is None


@pytest.mark.parametrize("row,col", [(-1, 0), (5, 0), (0, -1), (0, 12), (True, 0), (0, 1.5)])
def test_invalid_coordinate_rejected(placement_state, plant_types, row, col):
    assert placement_reason(placement_state, plant_types, 5, 12, "sunflower", row, col) == "out_of_bounds"


def test_non_playing_phase_rejected(placement_state, plant_types):
    placement_state["phase"] = "paused"
    assert placement_reason(placement_state, plant_types, 5, 12, "sunflower", 0, 0) == "wrong_phase"


def test_occupied_cell_rejected(placement_state, plant_types):
    assert placement_reason(placement_state, plant_types, 5, 12, "sunflower", 1, 2) == "occupied"


def test_cooldown_rejected(placement_state, plant_types):
    assert placement_reason(placement_state, plant_types, 5, 12, "wallnut", 0, 0) == "cooldown"


def test_insufficient_sun_rejected(placement_state, plant_types):
    placement_state["sun"] = 0
    assert placement_reason(placement_state, plant_types, 5, 12, "jalapeno", 0, 0) == "insufficient_sun"


def test_unknown_type_rejected(placement_state, plant_types):
    assert placement_reason(placement_state, plant_types, 5, 12, "missing", 0, 0) == "invalid_type"
