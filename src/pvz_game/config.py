import math
from .resources import read_json

LOGICAL_WIDTH = 1050
LOGICAL_HEIGHT = 600
GRID_COLUMNS = 12


def number(obj, key, minimum=0, integer=False, strict=False):
    value = obj.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"参数 {key} 必须为有限数值")
    if integer and not isinstance(value, int):
        raise ValueError(f"参数 {key} 必须为整数")
    if value < minimum or (strict and value == minimum):
        raise ValueError(f"参数 {key} 超出允许范围")


def validate(config, level):
    if config.get("schema_version") != 1 or config.get("tick_hz") != 60:
        raise ValueError("配置版本必须为1，模拟频率必须为60")
    number(config, "initial_sun", integer=True)
    for key in ("sun_value", "sun_lifetime_ticks", "natural_sun_interval_ticks"):
        number(config, key, integer=True, strict=True)
    for key in ("mower_speed", "cell_width", "cell_height", "projectile_radius", "zombie_radius", "sun_radius", "spawn_x"):
        number(config, key, strict=True)
    for key, expected in (("canvas_width", LOGICAL_WIDTH), ("canvas_height", LOGICAL_HEIGHT),
                          ("min_window_width", LOGICAL_WIDTH), ("min_window_height", LOGICAL_HEIGHT)):
        number(config, key, integer=True, strict=True)
        if config[key] != expected:
            raise ValueError(f"参数 {key} 必须为{expected}")
    for key in ("grid_x", "grid_y", "mower_trigger_x", "failure_x"):
        number(config, key)
    if not config["failure_x"] < config["mower_trigger_x"] < config["grid_x"]:
        raise ValueError("防线必须位于割草机触发线左侧，触发线位于草坪左侧")
    for group in ("plant_types", "zombie_types"):
        types = config[group]
        ids = [item["id"] for item in types]
        if not ids or any(not isinstance(i, str) or not i for i in ids) or len(set(ids)) != len(ids):
            raise ValueError("类型ID必须非空且唯一")
        for item in types:
            if group == "plant_types":
                if not isinstance(item.get("name"), str) or not item["name"].strip():
                    raise ValueError("植物名称不能为空")
                role=item.get("role")
                common={"id", "name", "price", "cooldown_ticks", "role"}
                role_fields={
                    "producer": {"hp", "production_interval_ticks", "sun_value"},
                    "shooter": {"hp", "attack_interval_ticks", "projectile_speed", "damage"},
                    "blocker": {"hp"},
                    "row_clearer": set(),
                }
                if role not in role_fields:
                    raise ValueError("未知植物职责")
                if set(item) != common | role_fields[role]:
                    raise ValueError(f"植物 {item.get('id')} 的职责字段缺失或多余")
                number(item, "price", integer=True)
                number(item, "cooldown_ticks", integer=True)
                if role in ("producer", "shooter", "blocker"):
                    number(item, "hp", integer=True, strict=True)
                if role == "producer":
                    number(item, "production_interval_ticks", integer=True, strict=True)
                    number(item, "sun_value", integer=True, strict=True)
                elif role == "shooter":
                    number(item, "attack_interval_ticks", integer=True, strict=True)
                    number(item, "projectile_speed", strict=True)
                    number(item, "damage", integer=True, strict=True)
            else:
                number(item, "hp", integer=True, strict=True)
                for key in ("speed", "contact_distance"):
                    number(item, key, strict=True)
                for key in ("bite_damage", "bite_interval_ticks"):
                    number(item, key, integer=True, strict=True)
    if level.get("id") != "day_01" or level.get("rows") != 5 or level.get("cols") != GRID_COLUMNS:
        raise ValueError("首版关卡必须为day_01，五行十二列")
    if config["grid_x"] + level["cols"] * config["cell_width"] > LOGICAL_WIDTH:
        raise ValueError("草坪列数超出1050像素逻辑画布")
    if config["grid_y"] + level["rows"] * config["cell_height"] > LOGICAL_HEIGHT:
        raise ValueError("草坪行数超出600像素逻辑画布")
    if config["spawn_x"] >= LOGICAL_WIDTH:
        raise ValueError("出怪位置必须位于战斗逻辑画布内")
    zombie_ids = {item["id"] for item in config["zombie_types"]}
    if not isinstance(level.get("spawn_schedule"), list) or not level["spawn_schedule"]:
        raise ValueError("关卡必须包含有限且非空的波次表")
    for spawn in level["spawn_schedule"]:
        number(spawn, "tick", integer=True)
        number(spawn, "row", integer=True)
        if spawn["row"] >= 5 or spawn["type_id"] not in zombie_ids:
            raise ValueError("出怪行或类型无效")
    for sun in level.get("sun_schedule", []):
        number(sun, "tick", integer=True)
        number(sun, "x")
        number(sun, "y")
    return config, level


def load():
    return validate(read_json("config/balance.json"), read_json("levels/day_01.json"))
