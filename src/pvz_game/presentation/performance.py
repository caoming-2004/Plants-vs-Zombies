"""Deterministic display scenes and frame timing for packaged benchmarks."""
from __future__ import annotations

import math


SCENES = {
    "standard": dict(sunflowers=5, peashooters=5, zombies=5, projectiles=10, suns=3),
    "pressure": dict(sunflowers=23, peashooters=22, zombies=30, projectiles=100, suns=20),
}


def make_scene(config, level, scene="pressure"):
    if scene not in SCENES:
        raise ValueError(f"Unknown benchmark scene: {scene}")
    counts = SCENES[scene]
    plants = []
    roles = (["sunflower"] * counts["sunflowers"] +
             ["peashooter"] * counts["peashooters"])
    for index, role in enumerate(roles):
        row, col = divmod(index, 9)
        plants.append(dict(id=index + 1, type_id=role, row=row, col=col,
                           hp=300, action="idle"))
    zombies = [dict(id=100 + i, type_id="zombie_basic", row=i % 5,
                    x=570 + (i // 5) * 48, hp=200, action="walking")
               for i in range(counts["zombies"])]
    shooters = [plant for plant in plants if plant["type_id"] == "peashooter"]
    projectiles = [dict(id=200 + i, source_id=shooters[i % len(shooters)]["id"],
                        row=i % 5, x=350 + (i % 8) * 72, y=0)
                   for i in range(counts["projectiles"])]
    suns = [dict(id=400 + i, x=130 + (i % 10) * 80, y=170 + (i % 5) * 72)
            for i in range(counts["suns"])]
    return dict(session_id=1, phase="playing", tick=0, sun=500,
                selection=dict(kind="none", type_id=None),
                ready_tick={plant["id"]: 0 for plant in config["plant_types"]},
                plants=plants, zombies=zombies, projectiles=projectiles, suns=suns,
                mowers=[dict(row=row, x=45, previous_x=45, state="ready")
                        for row in range(5)], next_spawn_index=0,
                total_spawns=len(level["spawn_schedule"]), kills=0)


def summarize_frame_intervals(intervals_ms):
    if not intervals_ms:
        raise ValueError("No frames were presented")
    ordered = sorted(intervals_ms)
    elapsed = sum(intervals_ms) / 1000
    longest_slow_run = slow_run = 0
    for value in intervals_ms:
        slow_run = slow_run + 1 if value > 50 else 0
        longest_slow_run = max(longest_slow_run, slow_run)
    return dict(frames=len(intervals_ms), elapsed_seconds=round(elapsed, 3),
                average_fps=round(len(intervals_ms) / elapsed, 2),
                p95_frame_ms=round(ordered[math.ceil(.95 * len(ordered)) - 1], 2),
                longest_over_50ms_frames=longest_slow_run,
                frame_intervals_ms=[round(value, 3) for value in intervals_ms])
