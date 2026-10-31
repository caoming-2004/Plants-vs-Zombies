"""Build day/night/dusk backgrounds from the project's generated master art.

Generation is a separate development step. This asset builder is fully offline.
"""
from pathlib import Path
import hashlib
import json
import pygame

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "backgrounds"
SOURCE = OUT / "source" / "yard-defense-master.png"
SOURCE_PAGE = "Project-generated environment art (OpenAI ImageGen, 2026-10-31)"
AUTHOR = "OpenAI ImageGen"
LICENSE = "Generated for this project; no third-party source image"
WIDTH, HEIGHT = 2560, 1440


def ensure_source():
    if not SOURCE.is_file():
        raise FileNotFoundError(f"Generated background master is missing: {SOURCE}")


def crop_to_sixteen_nine(image):
    width, height = image.get_size()
    target_width = round(height * 16 / 9)
    target_height = round(width * 9 / 16)
    if target_width <= width:
        left = (width - target_width) // 2
        return image.subsurface(pygame.Rect(left, 0, target_width, height))
    top = (height - target_height) // 2
    return image.subsurface(pygame.Rect(0, top, width, target_height))


def grade(image, theme):
    surface = pygame.transform.smoothscale(crop_to_sixteen_nine(image), (WIDTH, HEIGHT)).copy()
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    if theme == "day":
        multiply = (255, 244, 224)
        add = (24, 22, 12)
        tint = (255, 224, 160, 18)
    elif theme == "dusk":
        multiply = (255, 182, 128)
        add = (18, 2, 0)
        tint = (255, 110, 35, 44)
    else:
        multiply = (80, 98, 150)
        add = (0, 7, 22)
        tint = (8, 18, 48, 78)
    shade = pygame.Surface((WIDTH, HEIGHT))
    shade.fill(multiply)
    surface.blit(shade, (0, 0), special_flags=pygame.BLEND_MULT)
    glow = pygame.Surface((WIDTH, HEIGHT))
    glow.fill(add)
    surface.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)
    overlay.fill(tint)
    surface.blit(overlay, (0, 0))
    vignette = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for index in range(10):
        alpha = max(0, 28 - index * 3)
        pygame.draw.rect(vignette, (0, 0, 0, alpha),
                         (index * 18, index * 18, WIDTH - index * 36, HEIGHT - index * 36), 24)
    surface.blit(vignette, (0, 0))
    return surface


def main():
    ensure_source()
    pygame.init()
    pygame.display.set_mode((1, 1))
    source = pygame.image.load(str(SOURCE)).convert()
    names = {"day": "日间草坪", "night": "夜间草坪", "dusk": "黄昏草坪"}
    options = []
    records = []
    thumbs = OUT / "thumbs"
    thumbs.mkdir(exist_ok=True)
    for theme in ("day", "night", "dusk"):
        surface = grade(source, theme)
        path = OUT / f"{theme}.png"
        pygame.image.save(surface, str(path))
        pygame.image.save(pygame.transform.smoothscale(surface, (440, 248)), str(thumbs / f"{theme}.png"))
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        options.append(dict(
            id=theme, name=names[theme], file=f"{theme}.png", thumb=f"thumbs/{theme}.png",
            width=WIDTH, height=HEIGHT, theme=theme,
            source=SOURCE_PAGE,
            sha256=digest, license=LICENSE,
            author=AUTHOR,
        ))
        records.append(dict(id=theme, source=SOURCE_PAGE, author=AUTHOR,
                            license=LICENSE, width=WIDTH, height=HEIGHT, sha256=digest,
                            derivation="crop to 16:9 and " + theme + " color grade from the generated master",
                            generated_at="2026-10-31"))
    (OUT / "manifest.json").write_text(
        json.dumps(dict(schema_version=1, default="day", options=options), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    provenance = dict(
        master=dict(file=SOURCE.relative_to(OUT).as_posix(), source=SOURCE_PAGE,
                    generator=AUTHOR, license=LICENSE,
                    sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                    prompt="Mature cinematic photorealistic residential lawn defense environment; broad uncluttered grass playfield; realistic garden fence and mature trees; no characters, text, roads, horror, or childish cartoon style."),
        variants=records,
    )
    (OUT / "source" / "provenance.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("backgrounds built from generated master:", [item["id"] for item in options])
    pygame.quit()


if __name__ == "__main__":
    main()
