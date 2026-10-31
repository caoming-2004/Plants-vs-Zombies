"""Small SDL2/pygame-ce package and touch smoke app."""

from pathlib import Path
import pygame


def main():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("PVZ Android compatibility check")
    marker = pygame.image.load(str(Path(__file__).parent / "assets" / "marker.ppm"))
    clock = pygame.time.Clock()
    touched = False
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type in (pygame.FINGERDOWN, pygame.FINGERUP):
                touched = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                touched = True
        screen.fill((29, 39, 54) if not touched else (38, 91, 65))
        rect = marker.get_rect(center=screen.get_rect().center)
        screen.blit(marker, rect)
        pygame.display.flip()
        clock.tick(30)
    pygame.quit()


if __name__ == "__main__":
    main()
