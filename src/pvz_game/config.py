import math
from .resources import read_json

LOGICAL_WIDTH = 1050
LOGICAL_HEIGHT = 600
GRID_COLUMNS = 12
STAR_GOAL_KINDS = frozenset(("mowers_used_at_most", "clear_within_ticks", "sun_collected_at_least"))


def number(obj, key, minimum=0, integer=False, strict=False):
    value = obj.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"参数 {key} 必须为有限数值")
    if integer and not isinstance(value, int):
        raise ValueError(f"参数 {key} 必须为整数")
    if value < minimum or (strict and value == minimum):
        raise ValueError(f"参数 {key} 超出允许范围")


def _validate_optional_level_fields(config, level):
    rows = level["rows"]
    if "initial_sun" in level:
        number(level, "initial_sun", integer=True)
    if "sky_sun_interval_ticks" in level:
        number(level, "sky_sun_interval_ticks", integer=True, strict=True)
    if "mower_rows" in level:
        mowers = level["mower_rows"]
        if (not isinstance(mowers, list) or not mowers or
                any(type(row) is not int or not 0 <= row < rows for row in mowers) or
                len(set(mowers)) != len(mowers)):
            raise ValueError("割草机行必须是非空、唯一的有效行号")
    if "available_plants" in level:
        available = level["available_plants"]
        plant_ids = {item["id"] for item in config["plant_types"]}
        if (not isinstance(available, list) or not available or
                any(not isinstance(item, str) or item not in plant_ids for item in available) or
                len(set(available)) != len(available)):
            raise ValueError("可用植物必须是非空、唯一的已知植物ID")


def _validate_star_goals(level):
    mode = level.get("mode", "campaign")
    goals = level.get("star_goals")
    if mode == "campaign" and (not isinstance(goals, list) or len(goals) < 2):
        raise ValueError("战役关卡必须配置至少两个星级目标")
    if goals is None:
        return
    if not isinstance(goals, list):
        raise ValueError("星级目标必须为列表")
    ids = []
    for goal in goals:
        if not isinstance(goal, dict):
            raise ValueError("星级目标必须为对象")
        if set(goal) != {"id", "kind", "threshold", "text"}:
            raise ValueError("星级目标字段缺失或多余")
        if not isinstance(goal["id"], str) or not goal["id"]:
            raise ValueError("星级目标ID不能为空")
        if goal["kind"] not in STAR_GOAL_KINDS:
            raise ValueError("未知星级目标类型")
        if not isinstance(goal["text"], str) or not goal["text"].strip():
            raise ValueError("星级目标文本不能为空")
        number(goal, "threshold", integer=True, strict=goal["kind"] == "clear_within_ticks")
        if goal["kind"] == "mowers_used_at_most" and goal["threshold"] < 0:
            raise ValueError("割草机上限不能为负")
        ids.append(goal["id"])
    if len(set(ids)) != len(ids):
        raise ValueError("星级目标ID必须唯一")


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
                    "squash": {"hp", "attack_distance", "attack_duration_ticks", "damage"},
                    "snow_shooter": {"hp", "attack_interval_ticks", "projectile_speed", "damage", "slow_factor", "slow_duration_ticks"},
                    "row_clearer": set(),
                }
                if role not in role_fields:
                    raise ValueError("未知植物职责")
                if set(item) != common | role_fields[role]:
                    raise ValueError(f"植物 {item.get('id')} 的职责字段缺失或多余")
                number(item, "price", integer=True)
                number(item, "cooldown_ticks", integer=True)
                if role in ("producer", "shooter", "blocker", "squash", "snow_shooter"):
                    number(item, "hp", integer=True, strict=True)
                if role == "producer":
                    number(item, "production_interval_ticks", integer=True, strict=True)
                    number(item, "sun_value", integer=True, strict=True)
                elif role == "shooter":
                    number(item, "attack_interval_ticks", integer=True, strict=True)
                    number(item, "projectile_speed", strict=True)
                    number(item, "damage", integer=True, strict=True)
                elif role == "squash":
                    number(item, "attack_distance", strict=True)
                    number(item, "attack_duration_ticks", integer=True, strict=True)
                    number(item, "damage", integer=True, strict=True)
                elif role == "snow_shooter":
                    number(item, "attack_interval_ticks", integer=True, strict=True)
                    number(item, "projectile_speed", strict=True)
                    number(item, "damage", integer=True, strict=True)
                    number(item, "slow_factor", strict=True)
                    if item["slow_factor"] >= 1:
                        raise ValueError("寒冰射手减速系数必须小于1")
                    number(item, "slow_duration_ticks", integer=True, strict=True)
            else:
                number(item, "hp", integer=True, strict=True)
                for key in ("speed", "contact_distance"):
                    number(item, key, strict=True)
                for key in ("bite_damage", "bite_interval_ticks"):
                    number(item, key, integer=True, strict=True)
    if not isinstance(level.get("id"), str) or not level["id"].strip():
        raise ValueError("关卡ID不能为空")
    if level.get("rows") != 5 or level.get("cols") != GRID_COLUMNS:
        raise ValueError("关卡必须使用五行十二列")
    if level.get("mode", "campaign") not in ("campaign", "endless"):
        raise ValueError("未知关卡模式")
    if config["grid_x"] + level["cols"] * config["cell_width"] > LOGICAL_WIDTH:
        raise ValueError("草坪列数超出1050像素逻辑画布")
    if config["grid_y"] + level["rows"] * config["cell_height"] > LOGICAL_HEIGHT:
        raise ValueError("草坪行数超出600像素逻辑画布")
    if config["spawn_x"] >= LOGICAL_WIDTH:
        raise ValueError("出怪位置必须位于战斗逻辑画布内")
    _validate_optional_level_fields(config, level)
    _validate_star_goals(level)
    zombie_ids = {item["id"] for item in config["zombie_types"]}
    if not isinstance(level.get("spawn_schedule"), list) or not level["spawn_schedule"]:
        raise ValueError("关卡必须包含有限且非空的波次表")
    waves=level.get('waves')
    if not isinstance(waves,list) or len(waves)<3 or any(not isinstance(wave,dict) for wave in waves):
        raise ValueError('关卡必须配置至少三个递增波次')
    wave_ids=[wave.get('id') for wave in waves]
    if any(not isinstance(wave_id,str) or not wave_id for wave_id in wave_ids) or len(set(wave_ids))!=len(wave_ids):
        raise ValueError('波次ID必须非空且唯一')
    prior_tick=-1;prior_strength=0
    for wave in waves:
        if not isinstance(wave.get('name'),str) or not wave['name'].strip():
            raise ValueError('波次名称不能为空')
        number(wave,'start_tick',integer=True)
        number(wave,'strength',strict=True)
        if wave['start_tick']<=prior_tick or wave['strength']<=prior_strength:
            raise ValueError('波次开始时点和挑战强度必须递增')
        prior_tick=wave['start_tick'];prior_strength=wave['strength']
    wave_by_id={wave['id']:wave for wave in waves}
    wave_spawn_counts={wave_id:0 for wave_id in wave_ids}
    for spawn in level["spawn_schedule"]:
        number(spawn, "tick", integer=True)
        number(spawn, "row", integer=True)
        if spawn["row"] >= 5 or spawn["type_id"] not in zombie_ids or spawn.get('wave_id') not in wave_by_id:
            raise ValueError("出怪行或类型无效")
        wave=wave_by_id[spawn['wave_id']]
        if spawn['tick']<wave['start_tick']:
            raise ValueError('僵尸不能早于所属波次出现')
        wave_spawn_counts[spawn['wave_id']]+=1
    if any(count==0 for count in wave_spawn_counts.values()):
        raise ValueError('每个波次必须至少包含一个僵尸')
    for sun in level.get("sun_schedule", []):
        number(sun, "tick", integer=True)
        number(sun, "x")
        number(sun, "y")
    return config, level


def validate_campaign(config, campaign):
    if campaign.get("schema_version") != 1:
        raise ValueError("战役配置版本必须为1")
    stages = campaign.get("stages")
    if (not isinstance(stages, list) or len(stages) < 5 or
            any(not isinstance(stage, str) or not stage for stage in stages) or
            len(set(stages)) != len(stages)):
        raise ValueError("战役必须包含至少五个唯一关卡ID")
    endless = campaign.get("endless")
    if not isinstance(endless, dict):
        raise ValueError("战役必须配置无尽模式")
    if endless.get("unlock_after") != stages[-1]:
        raise ValueError("无尽模式必须由最后一关解锁")
    number(endless, "initial_sun", integer=True)
    number(endless, "sky_sun_interval_ticks", integer=True, strict=True)
    number(endless, "first_wave_tick", integer=True)
    number(endless, "base_interval_ticks", integer=True, strict=True)
    number(endless, "min_interval_ticks", integer=True, strict=True)
    number(endless, "base_zombies", integer=True, strict=True)
    number(endless, "zombie_growth", integer=True)
    number(endless, "max_zombies_per_wave", integer=True, strict=True)
    number(endless, "max_active_zombies", integer=True, strict=True)
    for key in ("fast_ratio_base", "fast_ratio_growth", "tough_ratio_base", "tough_ratio_growth"):
        number(endless, key)
        if not 0 <= endless[key] <= 1:
            raise ValueError(f"{key} 必须位于0到1之间")
    if endless["min_interval_ticks"] > endless["base_interval_ticks"]:
        raise ValueError("无尽最短间隔不能大于基础间隔")
    if endless["max_zombies_per_wave"] < endless["base_zombies"]:
        raise ValueError("无尽每波上限不能小于基础数量")
    if "mower_rows" in endless:
        mowers = endless["mower_rows"]
        if (not isinstance(mowers, list) or not mowers or
                any(type(row) is not int or not 0 <= row < 5 for row in mowers) or
                len(set(mowers)) != len(mowers)):
            raise ValueError("无尽割草机行必须是非空、唯一的有效行号")
    if "available_plants" in endless:
        available = endless["available_plants"]
        plant_ids = {item["id"] for item in config["plant_types"]}
        if (not isinstance(available, list) or not available or
                any(not isinstance(item, str) or item not in plant_ids for item in available) or
                len(set(available)) != len(available)):
            raise ValueError("无尽可用植物必须是非空、唯一的已知植物ID")
    return campaign


def load():
    return validate(read_json("config/balance.json"), read_json("levels/day_01.json"))


def load_campaign():
    config = read_json("config/balance.json")
    campaign = read_json("levels/campaign.json")
    validate_campaign(config, campaign)
    levels = {}
    for index, level_id in enumerate(campaign["stages"], start=1):
        level = read_json(f"levels/{level_id}.json")
        validate(config, level)
        if level.get("id") != level_id:
            raise ValueError(f"关卡文件ID与战役清单不一致：{level_id}")
        if level.get("order") != index:
            raise ValueError(f"关卡顺序与战役清单不一致：{level_id}")
        if not isinstance(level.get("name"), str) or not level["name"].strip():
            raise ValueError(f"关卡名称不能为空：{level_id}")
        levels[level_id] = level
    return config, campaign, levels
