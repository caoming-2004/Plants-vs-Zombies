"""Pure placement checks shared by authoritative commands and UI previews."""


def placement_reason(snapshot, plant_types, rows, cols, type_id, row, col):
    """Return a stable rejection code, or ``None`` when placement is legal.

    The function only reads the supplied game snapshot and plant definitions.
    It never mutates resources, cooldowns, selections, or entities.
    """
    if snapshot.get("phase") != "playing":
        return "wrong_phase"
    if type_id not in plant_types:
        return "invalid_type"
    if type(row) is not int or type(col) is not int or not (0 <= row < rows and 0 <= col < cols):
        return "out_of_bounds"
    if any(plant.get("hp", 1) > 0 and plant["row"] == row and plant["col"] == col
           for plant in snapshot.get("plants", ())):
        return "occupied"
    if snapshot.get("tick", 0) < snapshot.get("ready_tick", {}).get(type_id, 0):
        return "cooldown"
    if snapshot.get("sun", 0) < plant_types[type_id]["price"]:
        return "insufficient_sun"
    return None
