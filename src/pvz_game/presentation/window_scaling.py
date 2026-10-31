"""Shared logical-canvas scaling for the game and its display benchmark."""
import pygame

from ..config import LOGICAL_HEIGHT, LOGICAL_WIDTH


def scaled_size(window_size):
    width, height = window_size
    scale = min(width / LOGICAL_WIDTH, height / LOGICAL_HEIGHT)
    return max(1, round(LOGICAL_WIDTH * scale)), max(1, round(LOGICAL_HEIGHT * scale))


def present_canvas(window, canvas, surface=None, surface_size=None):
    width, height = window.get_size()
    size = scaled_size((width, height))
    if size != surface_size or surface is None:
        surface = pygame.Surface(size).convert()
    window.fill((24, 40, 28))
    pygame.transform.smoothscale(canvas, size, surface)
    window.blit(surface, ((width - size[0]) // 2, (height - size[1]) // 2))
    return surface, size
