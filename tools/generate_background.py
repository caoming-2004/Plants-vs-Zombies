"""Prepare the generated high-detail lawn background for the game."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import pygame

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets/skins/default/source/background-006-high-detail.png"
IMAGEGEN_SOURCE = ROOT / "assets/skins/default/source/background-006-imagegen.png"
OUTPUT = ROOT / "assets/skins/default/ui-background.png"
TARGET_SIZE = (2800, 1200)

def build_background():
    image = pygame.image.load(str(SOURCE))
    if image.get_size() != TARGET_SIZE:
        raise ValueError(f"Expected a {TARGET_SIZE[0]}x{TARGET_SIZE[1]} master, got {image.get_size()}")
    generated = pygame.image.load(str(IMAGEGEN_SOURCE))
    if generated.get_size() != (1915, 821):
        raise ValueError(f"Unexpected ImageGen master size: {generated.get_size()}")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(image, str(OUTPUT))
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    sources_path = ROOT / "assets/sources.json"
    sources = json.loads(sources_path.read_text(encoding="utf-8-sig"))
    sources["generated-background-006"] = {
        "source": "OpenAI ImageGen, re-rendered from the 7305e3d background reference",
        "author": "Plants vs Zombies project",
        "license": "Project-generated artwork; no third-party image asset was used",
        "generator": "OpenAI ImageGen master followed by pygame smoothscale to the 2800x1200 production canvas",
        "file": "skins/default/source/background-006-high-detail.png",
        "sha256": digest,
        "source_file": "skins/default/source/background-006-imagegen.png",
        "source_sha256": hashlib.sha256(IMAGEGEN_SOURCE.read_bytes()).hexdigest(),
        "source_dimensions": list(generated.get_size()),
        "dimensions": list(TARGET_SIZE),
        "roles": ["background", "lawn", "house", "road"],
        "derivation": "High-detail generated redraw preserving the first-version composition; 1915x821 generated master smoothly resized to 2800x1200",
        "adaptation": "Static offline PNG; renderer scales a cached surface without changing logical grid coordinates",
    }
    sources_path.write_text(json.dumps(sources, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {OUTPUT.relative_to(ROOT)} ({TARGET_SIZE[0]}x{TARGET_SIZE[1]}), SHA-256 {digest}")

if __name__ == "__main__":
    build_background()
