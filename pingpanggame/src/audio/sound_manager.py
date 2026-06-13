"""
Sound manager — load and play sound effects (extensible)
"""

import pygame


class SoundManager:
    """Sound manager; loads and plays on demand."""

    def __init__(self):
        pygame.mixer.init()
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self.enabled = True

    def load(self, name: str, path: str) -> None:
        """Load a sound file."""
        try:
            self.sounds[name] = pygame.mixer.Sound(path)
        except FileNotFoundError:
            print(f"[Warning] Sound file not found: {path}")

    def play(self, name: str) -> None:
        """Play a sound."""
        if self.enabled and name in self.sounds:
            self.sounds[name].play()

    def toggle(self) -> None:
        """Toggle sound on/off."""
        self.enabled = not self.enabled
