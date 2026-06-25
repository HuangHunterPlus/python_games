import math
import pygame
from config import ANIMAL_CONFIGS

_current_animal = "cat"


def set_animal(animal_type: str):
    global _current_animal
    _current_animal = animal_type


def get_animal_colors():
    cfg = ANIMAL_CONFIGS.get(_current_animal, ANIMAL_CONFIGS["cat"])
    return cfg

# Color palette
ORANGE = (255, 159, 67)
DARK_ORANGE = (230, 130, 40)
CREAM = (255, 243, 224)
PINK = (255, 138, 128)
DARK_PINK = (240, 100, 90)
WHITE = (255, 255, 255)
BLACK = (45, 45, 54)
DARK_GRAY = (99, 110, 114)
LIGHT_PINK = (255, 184, 184, 100)
CORAL = (255, 107, 107)
PALE = (220, 220, 210)
SICK_GREEN = (190, 210, 180)
BROWN = (180, 120, 60)


def _draw_cat_base(surf, frame, modifiers):
    w, h = surf.get_size()
    cx, cy = w // 2, h // 2
    breathe = math.sin(frame * 0.3) * 1.5
    ear_twitch = math.sin(frame * 0.5) * 2

    ac = get_animal_colors()
    body_color = modifiers.get("body_color", ac["body"])
    ear_color = modifiers.get("ear_color", ac["ear"])
    eye_open = modifiers.get("eye_open", 1.0)
    head_tilt = modifiers.get("head_tilt", 0)
    tail_up = modifiers.get("tail_up", 0)
    bounce_y = modifiers.get("bounce_y", 0)
    paw_raise = modifiers.get("paw_raise", 0)
    paw_reach = modifiers.get("paw_reach", 0)
    leg_tap = modifiers.get("leg_tap", 0)

    by = bounce_y

    # ── Tail ──
    tail_base = (cx + 22, cy + 20 + by + breathe * 0.5)
    tail_mid = (cx + 32, cy + by - int(tail_up * 6))
    tail_tip = (cx + 38 + int(tail_up * 8), cy - 5 + by - int(tail_up * 10))
    pygame.draw.aalines(surf, body_color, False,
                        [tail_base, tail_mid, tail_tip], 6)
    pygame.draw.circle(surf, body_color, tail_tip, 5)

    # ── Body (rounder, plumper) ──
    body_rect = pygame.Rect(cx - 22, cy + by + breathe, 44, 46)
    pygame.draw.ellipse(surf, body_color, body_rect)
    pygame.draw.ellipse(surf, CREAM,
                        pygame.Rect(cx - 14, cy + 6 + by + breathe, 28, 28))

    # ── Back legs (with tap/kick animation) ──
    leg_l_y = cy + 36 + by + breathe
    leg_r_y = cy + 36 + by + breathe
    leg_l_x = cx - 20
    leg_r_x = cx + 4
    if leg_tap in (1, 3):
        leg_l_y += math.sin(frame * 0.6) * 4
    if leg_tap in (2, 3):
        leg_r_y += math.sin(frame * 0.6 + math.pi) * 4
    leg_rect_l = pygame.Rect(leg_l_x, leg_l_y, 16, 16)
    leg_rect_r = pygame.Rect(leg_r_x, leg_r_y, 16, 16)
    pygame.draw.ellipse(surf, body_color, leg_rect_l)
    pygame.draw.ellipse(surf, body_color, leg_rect_r)
    pygame.draw.ellipse(surf, CREAM,
                        pygame.Rect(leg_l_x + 4, leg_l_y + 4, 8, 6))
    pygame.draw.ellipse(surf, CREAM,
                        pygame.Rect(leg_r_x + 4, leg_r_y + 4, 8, 6))

    # ── Front legs with paw raise / reach animation ──
    lp_x, lp_y = cx - 14, cy + 30 + by + breathe
    lp_w, lp_h = 10, 18
    rp_x, rp_y = cx + 4, cy + 30 + by + breathe
    rp_w, rp_h = 10, 18

    if paw_raise in (1, 3):
        wave = math.sin(frame * 0.5) * 3
        lp_x, lp_y = cx - 18, cy + 14 + by + breathe + wave
        lp_w, lp_h = 14, 12
    elif paw_reach > 0 and paw_raise != 1:
        lp_x = cx - 17
        lp_y = cy + 26 + by + breathe
        lp_w, lp_h = 10, 22

    if paw_raise in (2, 3):
        wave = math.sin(frame * 0.5 + math.pi) * 3
        rp_x, rp_y = cx + 4, cy + 14 + by + breathe + wave
        rp_w, rp_h = 14, 12
    elif paw_reach > 0 and paw_raise != 2:
        rp_x = cx + 7
        rp_y = cy + 26 + by + breathe
        rp_w, rp_h = 10, 22

    front_l = pygame.Rect(lp_x, lp_y, lp_w, lp_h)
    front_r = pygame.Rect(rp_x, rp_y, rp_w, rp_h)
    pygame.draw.ellipse(surf, body_color, front_l)
    pygame.draw.ellipse(surf, body_color, front_r)

    # Paw pads
    if paw_raise in (1, 3):
        pygame.draw.ellipse(surf, CREAM,
                            pygame.Rect(lp_x + 4, lp_y + 5, 6, 4))
    elif paw_reach > 0:
        pygame.draw.ellipse(surf, CREAM,
                            pygame.Rect(lp_x + 2, lp_y + 12, 6, 4))
    else:
        pygame.draw.ellipse(surf, CREAM,
                            pygame.Rect(cx - 12, cy + 38 + by + breathe, 6, 5))

    if paw_raise in (2, 3):
        pygame.draw.ellipse(surf, CREAM,
                            pygame.Rect(rp_x + 4, rp_y + 5, 6, 4))
    elif paw_reach > 0:
        pygame.draw.ellipse(surf, CREAM,
                            pygame.Rect(rp_x + 2, rp_y + 12, 6, 4))
    else:
        pygame.draw.ellipse(surf, CREAM,
                            pygame.Rect(cx + 6, cy + 38 + by + breathe, 6, 5))

    # ── Head (bigger — chibi style) ──
    head_cx = cx + head_tilt * 3
    head_cy = cy - 26 + by + breathe * 0.8
    head_r = 28
    pygame.draw.circle(surf, body_color, (int(head_cx), int(head_cy)), head_r)

    # ── Ears (larger, more expressive) ──
    ear_l_points = [
        (int(head_cx - 18 + ear_twitch * 0.3), int(head_cy - 14)),
        (int(head_cx - 28 + ear_twitch * 0.5), int(head_cy - 40)),
        (int(head_cx - 6 + ear_twitch * 0.2), int(head_cy - 28)),
    ]
    ear_r_points = [
        (int(head_cx + 18 - ear_twitch * 0.3), int(head_cy - 14)),
        (int(head_cx + 28 - ear_twitch * 0.5), int(head_cy - 40)),
        (int(head_cx + 6 - ear_twitch * 0.2), int(head_cy - 28)),
    ]
    pygame.draw.polygon(surf, body_color, ear_l_points)
    pygame.draw.polygon(surf, body_color, ear_r_points)

    ear_inner_l_points = [
        (ear_l_points[0][0] + 3, ear_l_points[0][1] + 3),
        (ear_l_points[1][0] + 4, ear_l_points[1][1] + 4),
        (ear_l_points[2][0] + 2, ear_l_points[2][1] + 3),
    ]
    ear_inner_r_points = [
        (ear_r_points[0][0] - 3, ear_r_points[0][1] + 3),
        (ear_r_points[1][0] - 4, ear_r_points[1][1] + 4),
        (ear_r_points[2][0] - 2, ear_r_points[2][1] + 3),
    ]
    pygame.draw.polygon(surf, ear_color, ear_inner_l_points)
    pygame.draw.polygon(surf, ear_color, ear_inner_r_points)

    # ── Face ──
    eye_off = 10
    eye_y = int(head_cy)

    if eye_open > 0.5:
        # Big anime-style eyes
        eye_w, eye_h = 14, 12
        eye_l_rect = pygame.Rect(
            int(head_cx - eye_off - eye_w // 2), eye_y - eye_h // 2,
            eye_w, eye_h)
        eye_r_rect = pygame.Rect(
            int(head_cx + eye_off - eye_w // 2), eye_y - eye_h // 2,
            eye_w, eye_h)

        # White of eyes
        pygame.draw.ellipse(surf, WHITE, eye_l_rect)
        pygame.draw.ellipse(surf, WHITE, eye_r_rect)

        # Iris (golden — suits orange cat)
        iris_r = 5
        pupil_y_off = -1
        if modifiers.get("looking_up"):
            pupil_y_off = -2
        pygame.draw.circle(surf, (255, 200, 50),
                           (int(head_cx - eye_off), eye_y + pupil_y_off), iris_r)
        pygame.draw.circle(surf, (255, 200, 50),
                           (int(head_cx + eye_off), eye_y + pupil_y_off), iris_r)

        # Pupil
        pupil_r = 4
        pygame.draw.circle(surf, BLACK,
                           (int(head_cx - eye_off), eye_y + pupil_y_off), pupil_r)
        pygame.draw.circle(surf, BLACK,
                           (int(head_cx + eye_off), eye_y + pupil_y_off), pupil_r)

        # Big shine (top-left)
        pygame.draw.circle(surf, WHITE,
                           (int(head_cx - eye_off + 3), eye_y + pupil_y_off - 3), 3)
        pygame.draw.circle(surf, WHITE,
                           (int(head_cx + eye_off + 3), eye_y + pupil_y_off - 3), 3)

        # Small shine (bottom-right)
        pygame.draw.circle(surf, WHITE,
                           (int(head_cx - eye_off - 2), eye_y + pupil_y_off + 2), 2)
        pygame.draw.circle(surf, WHITE,
                           (int(head_cx + eye_off - 2), eye_y + pupil_y_off + 2), 2)
    else:
        # Closed / sleepy eyes (cute curved arcs)
        eye_y2 = eye_y + 3
        for thick in range(2):
            pygame.draw.arc(surf, BLACK,
                            (int(head_cx - eye_off - 7), eye_y2 - 3 + thick, 14, 8),
                            0, math.pi, 2)
            pygame.draw.arc(surf, BLACK,
                            (int(head_cx + eye_off - 7), eye_y2 - 3 + thick, 14, 8),
                            0, math.pi, 2)

    # ── Blush (bigger, softer) ──
    blush_alpha = modifiers.get("blush", 120)
    blush_surf = pygame.Surface((16, 10), pygame.SRCALPHA)
    pygame.draw.ellipse(blush_surf, (*LIGHT_PINK[:3], blush_alpha), (0, 0, 16, 10))
    surf.blit(blush_surf, (int(head_cx - 20), int(head_cy + 4)))
    surf.blit(blush_surf, (int(head_cx + 4), int(head_cy + 4)))

    # ── Nose (tiny pink triangle) ──
    nose_points = [
        (int(head_cx), int(head_cy + 8)),
        (int(head_cx - 3), int(head_cy + 12)),
        (int(head_cx + 3), int(head_cy + 12)),
    ]
    pygame.draw.polygon(surf, CORAL, nose_points)

    # ── Mouth ──
    mouth_y = head_cy + 14
    mouth_open = modifiers.get("mouth_open", 0)
    if mouth_open > 0:
        pygame.draw.ellipse(surf, DARK_GRAY,
                            (int(head_cx - 4), int(mouth_y - 2), 8, 6))
    else:
        smile_curve = modifiers.get("smile", 0.8)
        if smile_curve > 0:
            pygame.draw.arc(surf, DARK_GRAY,
                            (int(head_cx - 8), int(mouth_y - 2), 16, 10),
                            0.3, math.pi - 0.3, 2)
        else:
            pygame.draw.arc(surf, DARK_GRAY,
                            (int(head_cx - 8), int(mouth_y + 2), 16, 10),
                            math.pi + 0.3, -0.3, 2)

    # ── Whiskers (thin, elegant) ──
    for side in [-1, 1]:
        for i in range(3):
            wx = head_cx + side * 14
            wy = head_cy + 7 + i * 4
            end_x = wx + side * 20
            end_y = wy - 2 + i * 3
            pygame.draw.aaline(surf, DARK_GRAY, (int(wx), int(wy)),
                               (int(end_x), int(end_y)))


def draw_idle(surf, frame):
    mods = {"smile": 0.6, "blush": 80}
    _draw_cat_base(surf, frame, mods)


def draw_happy(surf, frame):
    bounce = abs(math.sin(frame * 0.5)) * 6
    mods = {"bounce_y": -bounce, "eye_open": 1.2, "smile": 1.0,
            "blush": 160, "tail_up": 2, "paw_raise": 1}
    _draw_cat_base(surf, frame, mods)


def draw_sad(surf, frame):
    droop = -1 + math.sin(frame * 0.2) * 0.5
    mods = {"eye_open": 0.3, "smile": -0.5, "blush": 60,
            "head_tilt": droop, "tail_up": -0.5}
    _draw_cat_base(surf, frame, mods)


def draw_playful(surf, frame):
    bounce = abs(math.sin(frame * 0.8)) * 5
    mods = {"bounce_y": -bounce * 0.5, "eye_open": 1.3,
            "smile": 0.9, "blush": 140, "tail_up": 3,
            "looking_up": True, "paw_raise": 2, "leg_tap": 1}
    _draw_cat_base(surf, frame, mods)


def draw_hungry(surf, frame):
    turn = math.sin(frame * 0.15) * 3
    mods = {"head_tilt": turn, "eye_open": 0.9,
            "smile": 0.2, "mouth_open": 0.5, "blush": 60,
            "paw_reach": 0.7}
    _draw_cat_base(surf, frame, mods)


def draw_sleepy(surf, frame):
    droop = math.sin(frame * 0.1) * 1.5
    mods = {"eye_open": 0.1, "smile": 0.2, "blush": 40,
            "head_tilt": droop, "tail_up": -1}
    _draw_cat_base(surf, frame, mods)


def draw_sick(surf, frame):
    mods = {"body_color": PALE, "ear_color": (200, 170, 170),
            "eye_open": 0.2, "smile": -0.8, "blush": 30,
            "tail_up": -2}
    _draw_cat_base(surf, frame, mods)


def draw_curious(surf, frame):
    tilt = math.sin(frame * 0.2) * 4
    mods = {"head_tilt": tilt, "eye_open": 1.4,
            "smile": 0.4, "blush": 100, "tail_up": 1.5,
            "looking_up": True, "paw_raise": 1}
    _draw_cat_base(surf, frame, mods)


# ── New emotion draw functions ──────────────────────────────

def draw_excited(surf, frame):
    bounce = abs(math.sin(frame * 0.9)) * 7
    mods = {"bounce_y": -bounce, "eye_open": 1.4, "smile": 1.2,
            "blush": 180, "tail_up": 3, "looking_up": True,
            "paw_raise": 3, "leg_tap": 3}
    _draw_cat_base(surf, frame, mods)


def draw_cuddly(surf, frame):
    tilt = math.sin(frame * 0.15) * 2
    mods = {"head_tilt": tilt, "eye_open": 1.1, "smile": 0.8,
            "blush": 200, "tail_up": 1.0, "paw_reach": 1.0}
    _draw_cat_base(surf, frame, mods)


def draw_dance(surf, frame):
    sway = math.sin(frame * 0.6) * 5
    bounce = abs(math.sin(frame * 0.4)) * 3
    paw = 1 if int(frame * 0.3) % 2 == 0 else 2
    leg = 2 if int(frame * 0.3) % 2 == 0 else 1
    mods = {"head_tilt": sway * 0.3, "bounce_y": -bounce, "eye_open": 1.2,
            "smile": 1.0, "blush": 150, "tail_up": 2.5, "looking_up": True,
            "paw_raise": paw, "leg_tap": leg}
    _draw_cat_base(surf, frame, mods)


DRAW_FUNCTIONS = {
    "idle": draw_idle,
    "happy": draw_happy,
    "sad": draw_sad,
    "playful": draw_playful,
    "hungry": draw_hungry,
    "sleepy": draw_sleepy,
    "sick": draw_sick,
    "curious": draw_curious,
    "excited": draw_excited,
    "cuddly": draw_cuddly,
    "dance": draw_dance,
}


def draw_pet(surf: pygame.Surface, state: str, frame: int):
    func = DRAW_FUNCTIONS.get(state, draw_idle)
    func(surf, frame)


# ── Interaction overlays ────────────────────────────────────
# Each overlay function receives (surf, frame, progress)
# where progress goes from 0.0 (start) to 1.0 (end)
# Overlays are drawn on the 128x128 pet surface (cat center ~ 64, 64)

def draw_food_overlay(surf, frame, progress):
    cx, cy = 64, 64
    target_x, target_y = cx + 28, cy + 18
    if progress < 0.3:
        t = progress / 0.3
        fx = target_x
        fy = target_y - 50 * (1 - t)
    elif progress < 0.8:
        fx, fy = target_x, target_y
        bounce = abs(math.sin(progress * 30)) * 2
        fy = target_y - bounce
    else:
        fade = 1.0 - (progress - 0.8) / 0.2
        fx, fy = target_x, target_y
    # fish body
    pygame.draw.ellipse(surf, BROWN, (fx - 7, fy - 3, 14, 7))
    # tail
    tail_pts = [(fx + 7, fy), (fx + 14, fy - 5), (fx + 14, fy + 5)]
    pygame.draw.polygon(surf, BROWN, tail_pts)
    # eye
    pygame.draw.circle(surf, BLACK, (fx - 3, fy - 1), 2)


def draw_heart_overlay(surf, frame, progress):
    cx, cy = 64, 50
    alpha = int(255 * (1.0 - progress * 0.5))
    for i in range(3):
        offset_x = math.sin(frame * 0.1 + i * 2.1) * 15
        offset_y = -progress * 30 + i * 10
        hx = int(cx + offset_x)
        hy = int(cy + offset_y)
        size = max(2, int(6 * (1.0 - progress * 0.3)))
        heart_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        # two circles + triangle
        pygame.draw.circle(heart_surf, (255, 80, 80, alpha),
                           (size, 0), size)
        pygame.draw.circle(heart_surf, (255, 80, 80, alpha),
                           (0, 0), size)
        pygame.draw.polygon(heart_surf, (255, 80, 80, alpha),
                            [(0, size // 2), (size * 2, size // 2),
                             (size, size * 2)])
        surf.blit(heart_surf, (hx - size, hy - size))


def draw_gift_overlay(surf, frame, progress):
    cx, cy = 64, 64
    gx, gy = cx - 35, cy + 5
    bounce = abs(math.sin(progress * 20)) * 3
    gy -= bounce
    # box
    pygame.draw.rect(surf, (255, 100, 100), (gx, gy, 20, 16), border_radius=2)
    pygame.draw.rect(surf, (200, 60, 60), (gx, gy, 20, 16), 1, border_radius=2)
    # ribbon
    pygame.draw.line(surf, (255, 220, 100), (gx + 10, gy), (gx + 10, gy + 16), 2)
    pygame.draw.line(surf, (255, 220, 100), (gx, gy + 8), (gx + 20, gy + 8), 2)
    # bow
    bow_pts = [(gx + 10, gy), (gx + 5, gy - 5), (gx + 10, gy - 2),
               (gx + 15, gy - 5)]
    pygame.draw.polygon(surf, (255, 220, 100), bow_pts)
    pygame.draw.circle(surf, (255, 220, 100), (gx + 10, gy), 2)


def draw_toy_overlay(surf, frame, progress):
    cx, cy = 64, 64
    tx, ty = cx + 30, cy + 22
    roll = math.sin(progress * 20) * 3
    tx += int(roll)
    # yarn ball
    r = 7
    pygame.draw.circle(surf, (180, 100, 200), (tx, ty), r)
    pygame.draw.circle(surf, (200, 130, 220), (tx, ty), r, 1)
    # string lines
    for angle in [0, 0.8, 1.6, 2.4, 3.2]:
        ex = tx + int(r * 0.8 * math.cos(angle + progress * 2))
        ey = ty + int(r * 0.8 * math.sin(angle + progress * 2))
        pygame.draw.line(surf, (150, 70, 170), (tx, ty), (ex, ey), 1)
    # trailing string
    end_x = tx + int(math.sin(progress * 10) * 15)
    end_y = ty + 10 + int(progress * 5)
    pygame.draw.aaline(surf, (180, 100, 200), (tx + r, ty), (end_x, end_y))


def draw_star_overlay(surf, frame, progress):
    cx, cy = 64, 40
    alpha = int(255 * (1.0 - progress))
    for i in range(4):
        angle = frame * 0.05 + i * 1.57
        dist = 25 + math.sin(progress * 15 + i) * 5
        sx = int(cx + math.cos(angle) * dist)
        sy = int(cy + math.sin(angle) * dist - progress * 15)
        size = max(2, int(5 * (1.0 - progress * 0.5)))
        star_pts = []
        for j in range(10):
            r = size if j % 2 == 0 else size * 0.4
            a = j * math.pi / 5 - math.pi / 2 + progress * 2 + i
            star_pts.append((sx + int(r * math.cos(a)),
                             sy + int(r * math.sin(a))))
        star_surf = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
        pygame.draw.polygon(star_surf, (255, 255, 100, alpha), star_pts)
        surf.blit(star_surf, (sx - size * 2, sy - size * 2))


def draw_bubble_overlay(surf, frame, progress):
    cx, cy = 64, 64
    for i in range(6):
        bx = int(cx + math.sin(i * 2.3 + frame * 0.05) * 30)
        by = int(cy - progress * 40 + i * 12 - 10)
        r = max(1, int(3 + math.sin(i * 1.7) * 2))
        bubble_surf = pygame.Surface((r * 3, r * 3), pygame.SRCALPHA)
        alpha = max(0, int(120 * (1.0 - progress * 0.6)))
        pygame.draw.circle(bubble_surf, (180, 220, 255, alpha),
                           (r, r), r)
        pygame.draw.circle(bubble_surf, (255, 255, 255, alpha // 2),
                           (r - 1, r - 1), r // 2)
        surf.blit(bubble_surf, (bx - r, by - r))


def draw_book_overlay(surf, frame, progress):
    cx, cy = 64, 64
    bx, by = cx - 32, cy + 5 + abs(math.sin(progress * 10)) * 2
    # left page
    pygame.draw.polygon(surf, (240, 235, 220),
                        [(bx, by), (bx + 12, by - 6),
                         (bx + 12, by + 10), (bx, by + 16)])
    # right page
    pygame.draw.polygon(surf, (220, 215, 200),
                        [(bx + 12, by - 6), (bx + 24, by),
                         (bx + 24, by + 16), (bx + 12, by + 10)])
    # spine
    pygame.draw.line(surf, (180, 170, 150), (bx + 12, by - 6),
                     (bx + 12, by + 10), 1)
    # cover edges
    pygame.draw.polygon(surf, (200, 180, 150),
                        [(bx, by), (bx + 12, by - 6),
                         (bx + 24, by), (bx + 12, by + 6)], 1)


def draw_anger_overlay(surf, frame, progress):
    cx, cy = 64, 40
    shake = math.sin(frame * 1.5) * 3
    ax = int(cx + shake)
    ay = int(cy - progress * 10)
    # anger symbol: jagged lines like an "explosion" mark
    pts = [
        (ax - 8, ay + 2), (ax - 4, ay - 6), (ax, ay - 1),
        (ax + 3, ay - 8), (ax + 5, ay - 2), (ax + 10, ay - 3),
        (ax + 6, ay + 2), (ax + 10, ay + 6), (ax + 4, ay + 5),
        (ax + 2, ay + 10), (ax - 1, ay + 4), (ax - 6, ay + 8),
    ]
    pygame.draw.polygon(surf, (255, 60, 60), pts)


def draw_sparkle_overlay(surf, frame, progress):
    cx, cy = 64, 60
    alpha = int(255 * (1.0 - progress * 0.7))
    for i in range(5):
        angle = frame * 0.08 + i * 1.26
        dist = 20 + math.sin(progress * 20 + i) * 8
        sx = int(cx + math.cos(angle) * dist)
        sy = int(cy + math.sin(angle) * dist - progress * 10)
        size = 3 + int(math.sin(frame * 0.3 + i * 2) * 1.5)
        sp_surf = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
        # diamond shape
        sp_pts = [(size, 0), (size * 2, size), (size, size * 2), (0, size)]
        pygame.draw.polygon(sp_surf, (255, 255, 200, alpha), sp_pts)
        surf.blit(sp_surf, (sx - size, sy - size))


OVERLAY_FUNCTIONS = {
    "food": draw_food_overlay,
    "heart": draw_heart_overlay,
    "gift": draw_gift_overlay,
    "toy": draw_toy_overlay,
    "star": draw_star_overlay,
    "bubble": draw_bubble_overlay,
    "book": draw_book_overlay,
    "anger": draw_anger_overlay,
    "sparkle": draw_sparkle_overlay,
}
