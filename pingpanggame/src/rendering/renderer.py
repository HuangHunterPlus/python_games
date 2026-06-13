"""
Main renderer — orchestrates all draw calls
"""

import pygame
from src.config import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    TABLE_LEFT, TABLE_RIGHT, TABLE_TOP, TABLE_BOTTOM, TABLE_CENTER_X,
    NET_Y, NET_COLOR, COUNTDOWN_SECONDS,
    BALL_COLOR,
    PADDLE1_COLOR, PADDLE2_COLOR,
    BACKGROUND_PATH, BLACK, WHITE, GOLD,
)
from src.game_state import State
from src.rendering.hud import HUD
from src.rendering.effects import ParticleSystem


class Renderer:
    """Orchestrates all drawing operations."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.background: pygame.Surface | None = None
        self.hud = HUD()
        self.effects = ParticleSystem()
        self._load_background()

    # ── Asset loading ──

    def _load_background(self) -> None:
        """Load and scale the background image."""
        try:
            img = pygame.image.load(BACKGROUND_PATH)
        except FileNotFoundError:
            print(f"[Warning] Background not found: {BACKGROUND_PATH}")
            print("[Info] Using solid-color fallback background")
            self.background = None
            return

        img_w, img_h = img.get_size()

        scale = max(WINDOW_WIDTH / img_w, WINDOW_HEIGHT / img_h)
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)

        img = pygame.transform.scale(img, (new_w, new_h))

        crop_x = (new_w - WINDOW_WIDTH) // 2
        crop_y = (new_h - WINDOW_HEIGHT) // 2
        self.background = img.subsurface((crop_x, crop_y, WINDOW_WIDTH, WINDOW_HEIGHT))

        print(f"[Info] Background loaded and scaled: {BACKGROUND_PATH}")

    # ── Main render ──

    def render(self, ball, paddles, state, time_ms: int,
               show_serve_hint: bool = False, server: int = 1) -> None:
        """Full render pipeline for one frame."""
        self._draw_background()
        self._draw_net()
        self.effects.draw(self.screen)
        self._draw_ball_shadow(ball, time_ms)
        self._draw_ball(ball, time_ms)
        self._draw_paddle(paddles[0])
        self._draw_paddle(paddles[1])

        self.hud.draw_scores(self.screen, state.scores)
        self.hud.draw_controls(self.screen)

        if show_serve_hint:
            key_name = "Space" if server == 1 else "1"
            player_name = f"Player {server}"
            color = PADDLE1_COLOR if server == 1 else PADDLE2_COLOR
            self.hud.draw_center_message(
                self.screen,
                f"{player_name} press [{key_name}] to serve",
                'medium', color, y_offset=-40,
            )

        self._draw_state_overlay(state, time_ms)

    # ── Background ──

    def _draw_background(self) -> None:
        """Draw the background."""
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill((20, 24, 40))
            pygame.draw.rect(self.screen, (30, 60, 40),
                             (TABLE_LEFT, TABLE_TOP,
                              TABLE_RIGHT - TABLE_LEFT,
                              TABLE_BOTTOM - TABLE_TOP))
            pygame.draw.rect(self.screen, (255, 255, 255),
                             (TABLE_LEFT, TABLE_TOP,
                              TABLE_RIGHT - TABLE_LEFT,
                              TABLE_BOTTOM - TABLE_TOP), 2)

    # ── Net ──

    def _draw_net(self) -> None:
        """Draw the net."""
        net_surf = pygame.Surface((TABLE_RIGHT - TABLE_LEFT, 4), pygame.SRCALPHA)
        net_surf.fill(NET_COLOR)
        self.screen.blit(net_surf, (TABLE_LEFT, NET_Y - 2))

        for x in (TABLE_LEFT, TABLE_RIGHT):
            pygame.draw.circle(self.screen, (180, 180, 180),
                               (x, NET_Y), 4)

    # ── Ball ──

    def _draw_ball(self, ball, time_ms: int) -> None:
        """Draw the ball with bounce offset and scaling."""
        bounce_y = ball.get_bounce_offset(time_ms) if ball.is_moving else 0
        draw_y = ball.y - bounce_y
        scaled_r = ball.get_scaled_radius()

        for i, (tx, ty) in enumerate(ball.trail):
            alpha = int(100 * i / len(ball.trail))
            trail_r = scaled_r * (0.3 + 0.5 * i / len(ball.trail))
            trail_surf = pygame.Surface((int(trail_r * 2), int(trail_r * 2)),
                                         pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, (*BALL_COLOR, alpha),
                               (int(trail_r), int(trail_r)), int(trail_r))
            self.screen.blit(trail_surf,
                             (int(tx - trail_r), int(ty - trail_r)))

        pygame.draw.circle(self.screen, BALL_COLOR,
                           (int(ball.x), int(draw_y)), int(scaled_r))

        hl_r = scaled_r * 0.35
        hl_surf = pygame.Surface((int(hl_r * 2), int(hl_r * 2)), pygame.SRCALPHA)
        pygame.draw.circle(hl_surf, (255, 255, 255, 180),
                           (int(hl_r), int(hl_r)), int(hl_r))
        self.screen.blit(hl_surf,
                         (int(ball.x - hl_r * 0.5), int(draw_y - hl_r * 0.5)))

    # ── Ball shadow ──

    def _draw_ball_shadow(self, ball, time_ms: int) -> None:
        """Draw ball shadow on the table; shrinks and fades when the ball is higher."""
        if not ball.is_moving:
            return

        scaled_r = ball.get_scaled_radius()
        bounce_ratio = ball.get_bounce_ratio(time_ms)
        shadow_scale = max(0.3, 1.0 - bounce_ratio * 0.55)
        shadow_r = scaled_r * 0.65 * shadow_scale
        shadow_alpha = max(25, int(70 * shadow_scale))

        shadow_surf = pygame.Surface((int(shadow_r * 2), int(shadow_r)),
                                      pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, shadow_alpha),
                            (0, 0, int(shadow_r * 2), int(shadow_r)))
        self.screen.blit(shadow_surf,
                         (int(ball.x - shadow_r),
                          int(ball.y - shadow_r // 2)))

    # ── Paddle ──

    def _draw_paddle(self, paddle) -> None:
        """Draw paddle image over the hit rectangle."""
        if hasattr(paddle, 'surface') and paddle.surface is not None:
            surf = paddle.surface
            rect = surf.get_rect(center=(int(paddle.x), int(paddle.y)))
            shadow = surf.copy()
            shadow.fill((0, 0, 0, 120), special_flags=pygame.BLEND_RGBA_MULT)
            self.screen.blit(shadow, (rect.x + 4, rect.y + 4))
            self.screen.blit(surf, rect)
        else:
            main_rect = pygame.Rect(
                paddle.x - paddle.width // 2,
                paddle.y - paddle.height // 2,
                paddle.width, paddle.height,
            )
            pygame.draw.rect(self.screen, paddle.color, main_rect,
                             border_radius=4)

    # ── State overlay ──

    def _draw_state_overlay(self, state, time_ms: int) -> None:
        """Draw overlay for the current game state."""
        if state.current == State.TITLE:
            self.hud.draw_overlay(self.screen, 120)
            self.hud.draw_center_message(self.screen, "🏓 Top-Down Ping Pong", 'large', GOLD)
            self.hud.draw_center_message(self.screen, "Press SPACE to start",
                                         'medium', WHITE, y_offset=60)
            self.hud.draw_center_message(self.screen, "Player 1 [Space]  ·  Player 2 [1]",
                                         'small', WHITE, y_offset=95)

        elif state.current == State.COUNTDOWN:
            if state.timer < COUNTDOWN_SECONDS:
                self.hud.draw_countdown(self.screen, state.countdown_num)
            else:
                self.hud.draw_go(self.screen)

        elif state.current == State.SCORED:
            self.hud.draw_score_popup(self.screen,
                                      state.last_scorer, state.timer)

        elif state.current == State.GAME_OVER:
            self.hud.draw_overlay(self.screen, 120)
            self.hud.draw_center_message(
                self.screen,
                f"🏆 Player {state.winner} wins!",
                'large', GOLD,
            )
            scores_text = f"{state.scores[0]} : {state.scores[1]}"
            self.hud.draw_center_message(self.screen, scores_text,
                                         'medium', WHITE, y_offset=60)
            self.hud.draw_center_message(self.screen, "Press R to restart",
                                         'small', WHITE, y_offset=100)
