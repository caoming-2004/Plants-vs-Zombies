from pvz_game.presentation.audio import AudioController


class FakeMusic:
    def __init__(self):
        self.loaded = []
        self.played = []
        self.pauses = 0
        self.unpauses = 0
        self.stops = 0

    def load(self, path): self.loaded.append(path)
    def play(self, loops): self.played.append(loops)
    def set_volume(self, volume): self.volume = volume
    def pause(self): self.pauses += 1
    def unpause(self): self.unpauses += 1
    def stop(self): self.stops += 1


def test_scene_transitions_pause_resume_and_play_victory_once(monkeypatch):
    import pygame
    from pvz_game.presentation import audio

    music = FakeMusic()
    monkeypatch.setattr(pygame.mixer, 'get_init', lambda: (44100, -16, 2))
    monkeypatch.setattr(pygame.mixer, 'music', music)
    monkeypatch.setattr(audio, 'resource', lambda relative: relative)
    controller = AudioController()
    controller.update('menu')
    controller.update('menu')
    controller.update('playing')
    controller.update('paused')
    controller.update('paused')
    controller.update('playing')
    controller.update('won')
    controller.update('won')
    assert [path.rsplit('/', 1)[-1] for path in music.loaded] == [
        'menu.mp3', 'gameplay.mp3', 'victory.mp3']
    assert music.pauses == 1 and music.unpauses == 1


def test_missing_audio_device_degrades_to_silence(monkeypatch):
    import pygame

    monkeypatch.setattr(pygame.mixer, 'get_init', lambda: None)
    monkeypatch.setattr(pygame.mixer, 'init', lambda: (_ for _ in ()).throw(pygame.error('no device')))
    controller = AudioController()
    controller.update('menu')
    assert not controller.available
    assert controller.current is None
