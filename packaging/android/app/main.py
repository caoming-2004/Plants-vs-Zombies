"""Android entry point for the shared Pygame game package."""

import os
import sys
from pathlib import Path


PRIVATE_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PRIVATE_ROOT / "src"))

# Pygame's own compatibility mouse events would duplicate the normalized SDL
# finger events handled by the Android adapter.
os.environ.setdefault("SDL_TOUCH_MOUSE_EVENTS", "0")

from pvz_game.app import main


if __name__ == "__main__":
    main()
