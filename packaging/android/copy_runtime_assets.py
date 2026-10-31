"""Copy only files loaded by the Android runtime into the APK staging tree."""

import json
import shutil
import sys
from pathlib import Path


def copy_file(source_root: Path, destination_root: Path, relative: str) -> None:
    source = (source_root / relative).resolve()
    if not source.is_relative_to(source_root.resolve()) or not source.is_file():
        raise FileNotFoundError(f"Required Android runtime asset is missing: {relative}")
    destination = destination_root / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: copy_runtime_assets.py ASSETS_ROOT DESTINATION")
    source_root = Path(sys.argv[1]).resolve()
    destination_root = Path(sys.argv[2]).resolve()
    destination_root.mkdir(parents=True, exist_ok=True)

    for relative in (
        "config/balance.json",
        "levels/day_01.json",
        "sources.json",
        "fonts/NotoSansSC.ttf",
        "fonts/OFL.txt",
    ):
        copy_file(source_root, destination_root, relative)

    # These are the only appearances offered by the Android game. Resolve the
    # exact atlas and UI images through each manifest so unused source sheets,
    # obsolete atlases, and provenance-only images stay out of the APK.
    for skin_id in ("default", "dogs", "dogs_photo"):
        manifest_relative = f"skins/{skin_id}/manifest.json"
        copy_file(source_root, destination_root, manifest_relative)
        manifest = json.loads((source_root / manifest_relative).read_text(encoding="utf-8-sig"))
        relative_images = {manifest["atlas"]}
        if manifest.get("ui_atlas"):
            relative_images.add(manifest["ui_atlas"])
        for value in manifest.get("ui", {}).values():
            if isinstance(value, str):
                relative_images.add(value)
        for relative in sorted(relative_images):
            copy_file(source_root, destination_root, f"skins/{skin_id}/{relative}")


if __name__ == "__main__":
    main()
