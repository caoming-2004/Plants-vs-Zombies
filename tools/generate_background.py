"""Generate the original high-resolution lawn background used by the game."""
from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path

import pygame


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets/skins/default/source/background-005.png"
OUTPUT = ROOT / "assets/skins/default/ui-background.jpg"
SCALE = 2
WIDTH = 1400
HEIGHT = 600


def rect(surface, color, box, border_radius=0):
    pygame.draw.rect(surface, color, pygame.Rect(*(round(value * SCALE) for value in box)),
                     border_radius=round(border_radius * SCALE))


def line(surface, color, start, end, width=1):
    pygame.draw.line(surface, color,
                     tuple(round(value * SCALE) for value in start),
                     tuple(round(value * SCALE) for value in end),
                     max(1, round(width * SCALE)))


def ellipse(surface, color, box):
    pygame.draw.ellipse(surface, color, pygame.Rect(*(round(value * SCALE) for value in box)))


def polygon(surface, color, points):
    pygame.draw.polygon(surface, color,
                        [tuple(round(value * SCALE) for value in point) for point in points])


def build_background():
    pygame.init()
    surface = pygame.Surface((WIDTH * SCALE, HEIGHT * SCALE))
    surface.fill((155, 190, 116))
    rect(surface, (177, 198, 135), (0, 0, WIDTH, 93))

    rng = random.Random(20261026)
    for x in range(0, WIDTH, 52):
        rect(surface, (225, 218, 174), (x, 5, 39, 81), 9)
        rect(surface, (187, 183, 150), (x + 4, 9, 31, 73), 8)
        line(surface, (244, 231, 191), (x + 5, 13), (x + 30, 13), 2)
    line(surface, (104, 127, 80), (0, 88), (1010, 88), 5)

    rect(surface, (130, 96, 67), (0, 94, 1005, 17))
    for x in range(0, 1005, 52):
        rect(surface, (188, 144, 91), (x + 4, 96, 34, 13), 3)

    rect(surface, (86, 148, 65), (235, 92, 750, 480))
    for row in range(5):
        for col in range(12):
            x = 250 + col * 61.25
            y = 92 + row * 96
            base = (91, 151, 68) if (row + col) % 2 == 0 else (99, 158, 72)
            rect(surface, base, (x, y, 61.25, 96))
            for _ in range(70):
                px = rng.uniform(x + 2, x + 59)
                py = rng.uniform(y + 2, y + 94)
                color = rng.choice(((105, 168, 76), (79, 140, 62), (119, 171, 83),
                                    (92, 146, 65), (129, 177, 87)))
                line(surface, color, (px, py), (px + rng.uniform(-1, 2), py - rng.uniform(1, 4)), 0.8)
            for _ in range(5):
                px, py = rng.uniform(x + 4, x + 57), rng.uniform(y + 5, y + 90)
                ellipse(surface, rng.choice(((153, 188, 94), (193, 198, 107))), (px, py, 2, 2))
    rect(surface, (218, 202, 155), (985, 92, 89, 480))
    for y in range(96, 572, 52):
        line(surface, (184, 167, 128), (987, y), (1072, y), 1)
    for x in (1015, 1044):
        line(surface, (193, 175, 137), (x, 95), (x, 570), 1)

    rect(surface, (86, 96, 88), (1074, 45, 326, 555))
    polygon(surface, (118, 128, 115), [(1074, 45), (1400, 0), (1400, 600), (1074, 600)])
    for y in range(75, 580, 82):
        rect(surface, (218, 218, 195), (1208, y, 30, 41), 2)
    line(surface, (214, 204, 176), (1075, 50), (1075, 600), 7)

    rect(surface, (225, 220, 192), (0, 111, 235, 489))
    rect(surface, (190, 83, 54), (0, 0, 208, 31))
    for x in range(-16, 220, 32):
        polygon(surface, (162, 64, 48), [(x, 31), (x + 16, 8), (x + 32, 31)])
    rect(surface, (241, 231, 203), (46, 62, 164, 380))
    rect(surface, (202, 191, 162), (61, 89, 46, 82))
    rect(surface, (89, 124, 142), (68, 96, 32, 54))
    rect(surface, (111, 71, 50), (128, 240, 55, 113), 20)
    ellipse(surface, (221, 171, 90), (138, 250, 36, 36))
    rect(surface, (121, 159, 181), (44, 387, 57, 91))
    line(surface, (231, 218, 184), (73, 387), (73, 478), 3)
    line(surface, (231, 218, 184), (44, 431), (101, 431), 3)

    for _ in range(75):
        px = rng.uniform(10, 229)
        py = rng.uniform(120, 590)
        color = rng.choice(((201, 191, 161), (233, 222, 193), (175, 163, 135)))
        ellipse(surface, color, (px, py, rng.uniform(1, 3), rng.uniform(1, 3)))

    pygame.image.save(surface, str(SOURCE))
    pygame.image.save(surface, str(OUTPUT))
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    sources_path = ROOT / "assets/sources.json"
    sources = json.loads(sources_path.read_text(encoding="utf-8-sig"))
    sources["generated-background-005"] = {
        "source": "Original project-authored procedural artwork",
        "author": "Plants vs Zombies project contributors",
        "license": "Project original artwork; no third-party source material",
        "generator": "tools/generate_background.py",
        "file": "skins/default/source/background-005.png",
        "sha256": digest,
        "dimensions": [WIDTH * SCALE, HEIGHT * SCALE],
        "roles": ["background", "lawn", "house", "road"],
        "derivation": "Deterministic 2x pixel-resolution pygame drawing generated by tools/generate_background.py",
        "adaptation": "Custom house, fence, sidewalk, road and detailed lawn; maintains the 12x5 playable lawn footprint",
    }
    sources_path.write_text(json.dumps(sources, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pygame.quit()
    print(f"Generated {SOURCE.relative_to(ROOT)} ({WIDTH * SCALE}x{HEIGHT * SCALE}), SHA-256 {digest}")


if __name__ == "__main__":
    build_background()
