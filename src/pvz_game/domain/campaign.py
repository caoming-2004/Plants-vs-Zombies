"""Campaign rules: stage order, unlock lookup and star evaluation. No pygame."""


def stages(campaign):
    return tuple(campaign["stages"])


def next_stage(campaign, level_id):
    order = list(campaign["stages"])
    if level_id not in order:
        return None
    index = order.index(level_id)
    return order[index + 1] if index + 1 < len(order) else None


def is_last_stage(campaign, level_id):
    order = list(campaign["stages"])
    return bool(order) and order[-1] == level_id


def is_unlocked(unlocked, level_id):
    return level_id in unlocked


def evaluate_stars(level, stats):
    earned = []
    for goal in level.get("star_goals", []):
        kind, threshold = goal["kind"], goal["threshold"]
        if kind == "mowers_used_at_most":
            passed = stats.get("mowers_used", 0) <= threshold
        elif kind == "clear_within_ticks":
            passed = stats.get("elapsed_ticks", 0) <= threshold
        elif kind == "sun_collected_at_least":
            passed = stats.get("sun_collected", 0) >= threshold
        else:
            passed = False
        if passed:
            earned.append(goal["id"])
    return earned


def star_count(level, stats):
    return len(evaluate_stars(level, stats))
