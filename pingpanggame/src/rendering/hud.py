"""
HUD — scoreboard, control hints, message overlays
"""

import pygame
from src.config import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    WHITE, BLACK, GOLD, HUD_BG,
    FONT_NAME, FONT_SMALL, FONT_MEDIUM, FONT_LARGE,
    BALL_COLOR, PADDLE1_COLOR, PADDLE2_COLOR,
)


class HUD:
    """Draws scores, hints, and on-screen messages."""

    def __init__(self):
        self.fonts = {}
        self._init_fonts()

    def _init_fonts(self) -> None:
        """Preload fonts."""
        pygame.font.init()
        self.fonts['small'] = pygame.font.Font(FONT_NAME, FONT_SMALL)
        self.fonts['medium'] = pygame.font.Font(FONT_NAME, FONT_MEDIUM)
        self.fonts['large'] = pygame.font.Font(FONT_NAME, FONT_LARGE)
        self.fonts['score'] = pygame.font.Font(FONT_NAME, 48)

    # ── Utilities ──

    def _draw_text(self, screen: pygame.Surface, text: str,
                   font_key: str, color: tuple,
                   x: int, y: int,
                   center: bool = True,
                   shadow: bool = True) -> None:
        """Draw text with optional drop shadow."""
        font = self.fonts[font_key]
        if shadow:
            shadow_surf = font.render(text, True, BLACK)
            shadow_rect = shadow_surf.get_rect()
            if center:
                shadow_rect.center = (x + 2, y + 2)
            else:
                shadow_rect.topleft = (x + 2, y + 2)
            shadow_surf.set_alpha(160)
            screen.blit(shadow_surf, shadow_rect)

        surf = font.render(text, True, color)
        rect = surf.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        screen.blit(surf, rect)

    # ── Scores ──

    def draw_scores(self, screen: pygame.Surface, scores: list[int]) -> None:
        """Draw both players' scores (top and bottom)."""
        text = f"Player 2: {scores[1]}"
        surf = self.fonts['score'].render(text, True, PADDLE2_COLOR)
        rect = surf.get_rect()
        rect.top = 8
        rect.right = WINDOW_WIDTH - 20
        bg = pygame.Surface((rect.width + 12, rect.height + 6), pygame.SRCALPHA)
        bg.fill(HUD_BG)
        screen.blit(bg, (rect.left - 6, rect.top - 3))
        screen.blit(surf, rect)

        text = f"Player 1: {scores[0]}"
        surf = self.fonts['score'].render(text, True, PADDLE1_COLOR)
        rect = surf.get_rect()
        rect.bottom = WINDOW_HEIGHT - 8
        rect.right = WINDOW_WIDTH - 20
        bg = pygame.Surface((rect.width + 12, rect.height + 6), pygame.SRCALPHA)
        bg.fill(HUD_BG)
        screen.blit(bg, (rect.left - 6, rect.top - 3))
        screen.blit(surf, rect)

    # ── Control hints ──

    def draw_controls(self, screen: pygame.Surface) -> None:
        """Draw key hints for each player."""
        text1 = "[ Space ] Hit"
        self._draw_text(screen, text1, 'small', PADDLE1_COLOR,
                        10, WINDOW_HEIGHT - 10, center=False)

        text2 = "[ 1 ] Hit"
        self._draw_text(screen, text2, 'small', PADDLE2_COLOR,
                        10, 10, center=False)

    # ── Center messages ──

    def draw_center_message(self, screen: pygame.Surface,
                            text: str,
                            font_key: str = 'large',
                            color: tuple = WHITE,
                            y_offset: int = 0) -> None:
        """Show a large centered message."""
        self._draw_text(
            screen, text, font_key, color,
            WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + y_offset,
        )

    def draw_countdown(self, screen: pygame.Surface, number: int) -> None:
        """Draw countdown number."""
        color = GOLD if number == 1 else WHITE
        self._draw_text(screen, str(number), 'large', color,
                        WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

    def draw_go(self, screen: pygame.Surface) -> None:
        """Show GO!"""
        self._draw_text(screen, "GO!", 'large', GOLD,
                        WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

    # ── Score popup ──

    def draw_score_popup(self, screen: pygame.Surface,
                         player: int, timer: float) -> None:
        """Score popup animation (scale up + fade out)."""
        if player == 1:
            text = "Player 1 +1!"
            color = PADDLE1_COLOR
        else:
            text = "Player 2 +1!"
            color = PADDLE2_COLOR

        progress = min(timer / 1.5, 1.0)
        alpha = int(255 * (1 - progress))
        scale = 1.0 + progress * 1.5

        font = self.fonts['large']
        surf = font.render(text, True, color)

        new_w = int(surf.get_width() * scale)
        new_h = int(surf.get_height() * scale)
        surf = pygame.transform.scale(surf, (new_w, new_h))
        surf.set_alpha(alpha)

        rect = surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        screen.blit(surf, rect)

    # ── Dim overlay ──

    def draw_overlay(self, screen: pygame.Surface,
                     alpha: int = 150) -> None:
        """Draw a semi-transparent dark overlay."""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(alpha)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
