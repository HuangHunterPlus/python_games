"""
Paddle object — auto-tracks the ball; player only presses to hit
"""

import pygame
from src.config import (
    PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_TRACK_SPEED, HIT_COOLDOWN,
    PADDLE1_COLOR, PADDLE1_INIT_X, PADDLE1_INIT_Y, PADDLE1_BOUNDS,
    PADDLE2_COLOR, PADDLE2_INIT_X, PADDLE2_INIT_Y, PADDLE2_BOUNDS,
    PADDLE_IMAGE_PATH,
)


class Paddle:
    """Paddle auto-tracks the ball; no manual movement."""

    _paddle_surface: pygame.Surface | None = None

    def __init__(self, player_id: int):
        self.player_id: int = player_id
        self.width: int = PADDLE_WIDTH
        self.height: int = PADDLE_HEIGHT
        self.hit_cooldown: float = 0.0
        self.can_hit_flag: bool = False

        if player_id == 1:
            self.color = PADDLE1_COLOR
            self.x = float(PADDLE1_INIT_X)
            self.y = float(PADDLE1_INIT_Y)
            self.bounds = PADDLE1_BOUNDS
        else:
            self.color = PADDLE2_COLOR
            self.x = float(PADDLE2_INIT_X)
            self.y = float(PADDLE2_INIT_Y)
            self.bounds = PADDLE2_BOUNDS

        self.surface = Paddle._get_surface(self.player_id)

    @staticmethod
    def _get_surface(player_id: int) -> pygame.Surface:
        """Load paddle image and scale; Player 2 paddle is rotated 180°."""
        if Paddle._paddle_surface is None:
            try:
                img = pygame.image.load(PADDLE_IMAGE_PATH).convert_alpha()
            except FileNotFoundError:
                print(f"[Warning] Paddle image not found: {PADDLE_IMAGE_PATH}")
                img = None

            if img is not None:
                target_w = int(max(PADDLE_WIDTH, 80))
                ratio = img.get_height() / img.get_width()
                target_h = int(target_w * ratio)
                img = pygame.transform.smoothscale(img, (target_w, target_h))
                Paddle._paddle_surface = img
            else:
                Paddle._paddle_surface = pygame.Surface(
                    (max(PADDLE_WIDTH, 80), max(PADDLE_HEIGHT, 40)),
                    pygame.SRCALPHA,
                )
                Paddle._paddle_surface.fill((200, 200, 200, 128))

        if player_id == 2:
            return pygame.transform.rotate(Paddle._paddle_surface, 180)
        return Paddle._paddle_surface

    def auto_track(self, ball_x: float, dt: float) -> None:
        """Auto-track the ball's X position."""
        dx = ball_x - self.x
        self.x += dx * PADDLE_TRACK_SPEED
        self.x = max(self.bounds['min_x'], min(self.x, self.bounds['max_x']))

    def update_cooldown(self, dt: float) -> None:
        if self.hit_cooldown > 0:
            self.hit_cooldown -= dt

    def can_hit(self) -> bool:
        return self.hit_cooldown <= 0

    def reset_cooldown(self) -> None:
        self.hit_cooldown = HIT_COOLDOWN

    def reset_position(self) -> None:
        if self.player_id == 1:
            self.x = float(PADDLE1_INIT_X)
            self.y = float(PADDLE1_INIT_Y)
        else:
            self.x = float(PADDLE2_INIT_X)
            self.y = float(PADDLE2_INIT_Y)

    def get_rect(self):
        return pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height,
        )
