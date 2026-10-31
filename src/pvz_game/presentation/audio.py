"""Best-effort offline music playback; audio failures never block play."""
from pathlib import Path

import pygame

from ..resources import resource


TRACKS = {
    "menu": ("assets/music/menu.mp3", -1),
    "gameplay": ("assets/music/gameplay.mp3", -1),
    "victory": ("assets/music/victory.mp3", 0),
}


class AudioController:
    def __init__(self, enabled=True, volume=0.55):
        self.enabled = bool(enabled)
        self.volume = max(0.0, min(1.0, float(volume)))
        self.available = False
        self.current = None
        self.victory_seen = False
        self.paused = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.available = True
            pygame.mixer.music.set_volume(self.volume)
        except (pygame.error, OSError):
            self.available = False

    def set_enabled(self, enabled):
        self.enabled = bool(enabled)
        if not self.enabled:
            self.stop()

    def set_volume(self, volume):
        self.volume = max(0.0, min(1.0, float(volume)))
        if self.available:
            try:
                pygame.mixer.music.set_volume(self.volume)
            except pygame.error:
                self.available = False

    def stop(self):
        if self.available:
            try:
                pygame.mixer.music.stop()
            except pygame.error:
                self.available = False
        self.current = None

    def update(self, phase):
        if phase != "won":
            self.victory_seen = False
        if not self.enabled or not self.available:
            return
        if phase in ("paused", "lost", "quit"):
            if phase == "paused" and self.current is not None and not self.paused:
                try:
                    pygame.mixer.music.pause()
                    self.paused = True
                except pygame.error:
                    self.available = False
            elif phase != "paused" and self.current is not None:
                self.stop()
            return
        track = "victory" if phase == "won" else "gameplay" if phase == "playing" else "menu"
        if track == "victory" and self.victory_seen:
            return
        if track == self.current and self.paused:
            try:
                pygame.mixer.music.unpause()
                self.paused = False
            except pygame.error:
                self.available = False
            return
        if track == self.current:
            return
        try:
            filename, loops = TRACKS[track]
            pygame.mixer.music.load(str(resource(filename)))
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play(loops)
            self.current = track
            self.paused = False
            if track == "victory":
                self.victory_seen = True
        except (pygame.error, OSError, FileNotFoundError, RuntimeError):
            self.available = False
            self.current = None

