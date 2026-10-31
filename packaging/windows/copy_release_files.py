"""Copy localized release notes without PowerShell code-page filename conversion."""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
GUIDE_NAME = "".join(map(chr, (0x5F00, 0x59CB, 0x6E38, 0x620F))) + ".txt"
LICENSE_NAME = "".join(map(chr, (0x5B57, 0x4F53, 0x8BB8, 0x53EF))) + ".txt"

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-name", required=True)
    artifact = parser.parse_args().artifact_name
    bundle = ROOT / "dist" / "windows" / artifact
    guides = list((ROOT / "packaging" / "windows").glob("*.txt"))
    if len(guides) != 1 or guides[0].name != GUIDE_NAME:
        raise SystemExit("Expected exactly one correctly named game guide")
    shutil.copy2(guides[0], bundle / GUIDE_NAME)
    shutil.copy2(ROOT / "assets" / "fonts" / "OFL.txt", bundle / LICENSE_NAME)
    shutil.copy2(ROOT / "packaging" / "windows" / "music-attribution.md",
                 bundle / "音乐来源.md")

if __name__ == "__main__":
    main()
