"""
Collision detection — hit zone checks and out-of-bounds
"""

import math
import random
from src.config import (
    BALL_ACCEL, BALL_MAX_SPEED, HIT_COOLDOWN, HIT_ZONE_HEIGHT,
)


def is_ball_in_hit_zone(ball, paddle) -> bool:
    """
    Return True if the ball is in the paddle hit zone.
    Serve: only the receiver, after the ball bounced on both sides.
    Rally: receiver must wait for the ball to land on their side.
    """
    if not ball.is_moving:
        return False

    if ball.serve_mode and paddle.player_id == ball.server_id:
        return False

    dy = abs(ball.y - paddle.y)
    if dy > HIT_ZONE_HEIGHT / 2:
        return False

    margin = paddle.width * 0.3
    if abs(ball.x - paddle.x) > paddle.width / 2 + margin:
        return False

    if paddle.player_id == 1 and ball.vy < 0:
        return False
    if paddle.player_id == 2 and ball.vy > 0:
        return False

    if not ball.has_landed():
        return False

    return True


def hit_ball(ball, paddle) -> None:
    """Successful hit: reverse direction and add slight random angle."""
    ball.vy = -ball.vy * BALL_ACCEL

    offset = random.uniform(-1.5, 1.5)
    current_speed = max(abs(ball.vy), 1)
    ball.vx += offset * current_speed * 0.3

    speed = math.hypot(ball.vx, ball.vy)
    if speed > BALL_MAX_SPEED:
        ball.vx *= BALL_MAX_SPEED / speed
        ball.vy *= BALL_MAX_SPEED / speed

    paddle.hit_cooldown = HIT_COOLDOWN
    ball.on_hit()


def check_ball_wall(ball, table_bounds) -> str | None:
    """
    Check if the ball is out of bounds.
    Returns 'top' / 'bottom' / 'left' / 'right' or None.
    """
    top, bottom, left, right = table_bounds

    if ball.y - ball.radius < top:
        return 'top'
    if ball.y + ball.radius > bottom:
        return 'bottom'
    if ball.x - ball.radius < left:
        return 'left'
    if ball.x + ball.radius > right:
        return 'right'

    return None
