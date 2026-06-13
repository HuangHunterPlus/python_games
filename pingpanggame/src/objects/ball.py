"""
Ball object — physics, bounce animation, depth scaling
"""

import math
import random
from src.config import (
    BALL_RADIUS, BALL_BASE_SPEED, BALL_MAX_SPEED, BALL_ACCEL,
    BOUNCE_HEIGHT, BOUNCE_CYCLE_DISTANCE, LANDING_BOUNCE_DURATION,
    LANDING_BOUNCE_MULTIPLIER, LANDING_DIST, OWN_BOUNCE_DIST,
    TABLE_LEFT, TABLE_RIGHT, TABLE_TOP, TABLE_BOTTOM, TABLE_CENTER_X,
    NET_Y,
)


def _parabolic_bounce(t: float) -> float:
    """Parabolic arc (0 at t=0 and t=1, peak at t=0.5)."""
    t = max(0.0, min(1.0, t))
    return 4.0 * t * (1.0 - t)


class Ball:
    """Ball: position, velocity, collisions, pseudo-3D bounce"""

    # Serve phases: 0 = bounce on own side, 1 = fly to opponent side, 2 = ready to return
    SERVE_TO_OWN = 0
    SERVE_TO_OPP = 1
    SERVE_READY = 2

    def __init__(self):
        self.x: float = TABLE_CENTER_X
        self.y: float = TABLE_TOP + 100
        self.vx: float = 0
        self.vy: float = 0
        self.radius: float = BALL_RADIUS
        self.bounce_time: float = 0.0
        self.bounce_travel: float = 0.0
        self.is_moving: bool = False
        self.trail: list[tuple[float, float]] = []

        # Serve state
        self.serve_mode: bool = False
        self.server_id: int = 0
        self.serve_phase: int = 0

        # Rally: ball must bounce on receiver's side before they can hit
        self.landed: bool = False
        self.net_crossed_on_side: int = 0
        self.landing_time: float = 0

    # ── Init / reset ──

    def reset(self, direction: str = "up", server: int = 1) -> None:
        """Reset for a serve — first toward own table, then over the net."""
        speed = BALL_BASE_SPEED
        angle_deg = random.uniform(-15, 15)
        angle_rad = math.radians(angle_deg)

        if server == 1:
            self.x = TABLE_CENTER_X
            self.y = TABLE_BOTTOM - 60
            # Drop toward the back of own half first
            self.vx = math.sin(angle_rad) * speed * 0.2
            self.vy = abs(math.cos(angle_rad)) * speed
        else:
            self.x = TABLE_CENTER_X
            self.y = TABLE_TOP + 60
            self.vx = math.sin(angle_rad) * speed * 0.2
            self.vy = -abs(math.cos(angle_rad)) * speed

        self.is_moving = True
        self.bounce_time = 0.0
        self.bounce_travel = 0.0
        self.trail.clear()

        self.landed = False
        self.net_crossed_on_side = 0
        self.landing_time = 0

        self.serve_mode = True
        self.server_id = server
        self.serve_phase = self.SERVE_TO_OWN

    def stop(self) -> None:
        """Stop the ball."""
        self.vx = 0
        self.vy = 0
        self.is_moving = False
        self.trail.clear()
        self.serve_mode = False
        self.serve_phase = 0
        self.landed = False
        self.net_crossed_on_side = 0
        self.landing_time = 0
        self.bounce_travel = 0.0

    def _trigger_table_bounce(self) -> None:
        """Mark a table bounce for animation and reset bounce travel."""
        self.landing_time = self.bounce_time
        self.bounce_travel = 0.0

    # ── Update ──

    def update(self, dt: float, time_ms: int) -> None:
        """Update position, velocity, and trail."""
        if not self.is_moving:
            return

        dt_factor = dt * 60
        prev_y = self.y

        self.x += self.vx * dt_factor
        self.y += self.vy * dt_factor

        self.bounce_travel += math.hypot(self.vx, self.vy) * dt_factor

        self.trail.append((self.x, self.y))
        if len(self.trail) > 8:
            self.trail.pop(0)

        if self.x - self.radius < TABLE_LEFT:
            self.x = TABLE_LEFT + self.radius
            self.vx = abs(self.vx)
        elif self.x + self.radius > TABLE_RIGHT:
            self.x = TABLE_RIGHT - self.radius
            self.vx = -abs(self.vx)

        if self.serve_mode:
            self._update_serve_bounces()
        else:
            self._update_rally_bounces(prev_y)

        self.bounce_time += dt

    def _update_serve_bounces(self) -> None:
        """Serve: own side bounce, then opponent side bounce."""
        speed = max(BALL_BASE_SPEED, math.hypot(self.vx, self.vy))

        if self.serve_phase == self.SERVE_TO_OWN:
            if self.server_id == 1:
                own_line = TABLE_BOTTOM - OWN_BOUNCE_DIST
                if self.y >= own_line and self.vy > 0:
                    self.vy = -speed
                    self.vx *= 0.9
                    self.serve_phase = self.SERVE_TO_OPP
                    self._trigger_table_bounce()
            else:
                own_line = TABLE_TOP + OWN_BOUNCE_DIST
                if self.y <= own_line and self.vy < 0:
                    self.vy = speed
                    self.vx *= 0.9
                    self.serve_phase = self.SERVE_TO_OPP
                    self._trigger_table_bounce()

        elif self.serve_phase == self.SERVE_TO_OPP:
            if self.server_id == 1:
                if self.y <= NET_Y - LANDING_DIST and self.vy < 0:
                    self.serve_phase = self.SERVE_READY
                    self.landed = True
                    self._trigger_table_bounce()
            else:
                if self.y >= NET_Y + LANDING_DIST and self.vy > 0:
                    self.serve_phase = self.SERVE_READY
                    self.landed = True
                    self._trigger_table_bounce()

    def _update_rally_bounces(self, prev_y: float) -> None:
        """Rally: after a return, ball goes straight to opponent's side."""
        if self.vy < 0 and prev_y > NET_Y and self.y <= NET_Y and self.net_crossed_on_side != 2:
            self.net_crossed_on_side = 2
            self.landed = False
            self.landing_time = 0
        elif self.vy > 0 and prev_y < NET_Y and self.y >= NET_Y and self.net_crossed_on_side != 1:
            self.net_crossed_on_side = 1
            self.landed = False
            self.landing_time = 0

        if not self.landed and self.net_crossed_on_side > 0:
            if self.net_crossed_on_side == 1 and self.y >= NET_Y + LANDING_DIST:
                self.landed = True
                self._trigger_table_bounce()
            elif self.net_crossed_on_side == 2 and self.y <= NET_Y - LANDING_DIST:
                self.landed = True
                self._trigger_table_bounce()

    def has_landed(self) -> bool:
        """True when the ball has bounced on the receiver's side and can be returned."""
        if self.serve_mode:
            return self.serve_phase >= self.SERVE_READY
        return self.landed

    def on_hit(self) -> None:
        """After a return — ball flies directly to the opponent's table."""
        self.serve_mode = False
        self.serve_phase = 0
        self.landed = False
        self.net_crossed_on_side = 0
        self.landing_time = 0
        self.bounce_travel = 0.0

    # ── Pseudo-3D effects ──

    def get_bounce_offset(self, time_ms: int) -> float:
        """Vertical bounce offset synced to travel distance."""
        if not self.is_moving:
            return 0.0

        cycle = max(BOUNCE_CYCLE_DISTANCE, 1)
        t = (self.bounce_travel % cycle) / cycle
        height = _parabolic_bounce(t) * BOUNCE_HEIGHT

        speed = math.hypot(self.vx, self.vy)
        speed_factor = 0.85 + min(speed / BALL_MAX_SPEED, 1.0) * 0.25
        height *= speed_factor

        if self.landing_time > 0:
            elapsed = self.bounce_time - self.landing_time
            if 0 <= elapsed < LANDING_BOUNCE_DURATION:
                land_t = elapsed / LANDING_BOUNCE_DURATION
                land_h = (
                    _parabolic_bounce(land_t)
                    * BOUNCE_HEIGHT
                    * LANDING_BOUNCE_MULTIPLIER
                    * (1.0 - land_t * 0.6)
                )
                height = max(height, land_h)

        if self.serve_mode and self.serve_phase == self.SERVE_TO_OPP:
            if self.server_id == 1:
                dist = NET_Y - self.y
            else:
                dist = self.y - NET_Y
            factor = max(0.2, 1.0 - dist / 120)
            height = max(height, BOUNCE_HEIGHT * (1.2 + factor * 1.8) * _parabolic_bounce(t))

        return height

    def get_bounce_ratio(self, time_ms: int) -> float:
        """Normalized bounce height (0 = on table, 1 = peak) for shadow scaling."""
        if not self.is_moving or BOUNCE_HEIGHT <= 0:
            return 0.0
        return min(1.0, self.get_bounce_offset(time_ms) / (BOUNCE_HEIGHT * 2.5))

    def get_scaled_radius(self) -> float:
        """Scale radius by Y position (near = larger)."""
        progress = (self.y - TABLE_TOP) / (TABLE_BOTTOM - TABLE_TOP)
        progress = max(0.0, min(1.0, progress))
        scale = 0.85 + progress * 0.3
        return self.radius * scale

    # ── Velocity helpers ──

    def reverse_vy(self, accel: float = BALL_ACCEL) -> None:
        self.vy = -self.vy * accel
        self._clamp_speed()

    def add_vx(self, delta: float) -> None:
        self.vx += delta
        self._clamp_speed()

    def _clamp_speed(self) -> None:
        speed = math.hypot(self.vx, self.vy)
        if speed > BALL_MAX_SPEED:
            self.vx *= BALL_MAX_SPEED / speed
            self.vy *= BALL_MAX_SPEED / speed

    def get_rect(self):
        import pygame
        r = self.get_scaled_radius()
        return pygame.Rect(self.x - r, self.y - r, r * 2, r * 2)
