import os
import pygame
from config import *

screen = None
bg = None
bg_ox = 0
BG_MAX_SCROLL = 0
frame1 = None
frame2 = None
BOAT_W = 0
BOAT_H = 0
boat_x = 0
boat_y = 0
player_boat_x = 0
ai_boat_x = 0
font_large = None
font_med = None
font_sm = None
font_timer = None
snd_row = None
snd_win = None
snd_lose = None


def init():
    pygame.init()
    pygame.mixer.init()
    global screen, bg, bg_ox, BG_MAX_SCROLL
    global frame1, frame2, BOAT_W, BOAT_H, boat_x, boat_y
    global font_large, font_med, font_sm, font_timer
    global snd_row, snd_win, snd_lose
    global player_boat_x, ai_boat_x

    root = os.path.dirname(os.path.dirname(__file__))
    img_dir = os.path.join(root, "images")
    aud_dir = os.path.join(root, "audio")

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Dragon Boat Rowing - 龙舟划船")
    pygame.key.start_text_input()

    def load_font(size, bold=False):
        for p in [
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simsun.ttc",
        ]:
            try:
                return pygame.font.Font(p, size)
            except Exception:
                continue
        return pygame.font.Font(None, size)

    font_large = load_font(54, True)
    font_med = load_font(40, True)
    font_sm = load_font(26)
    font_timer = load_font(48, True)

    bg_raw = pygame.image.load(os.path.join(img_dir, "bg.png"))
    bg_w = int(SCREEN_WIDTH * BG_SCALE)
    bg_h = int(bg_raw.get_height() * BG_SCALE)
    bg = pygame.transform.scale(bg_raw, (bg_w, bg_h))
    bg_ox = (bg_w - SCREEN_WIDTH) // 2
    BG_MAX_SCROLL = max(0, bg_h - SCREEN_HEIGHT)

    frame1 = pygame.image.load(os.path.join(img_dir, "1.png")).convert_alpha()
    frame2 = pygame.image.load(os.path.join(img_dir, "2.png")).convert_alpha()

    BOAT_W = int(frame1.get_width() * BOAT_SCALE)
    BOAT_H = int(frame1.get_height() * BOAT_SCALE)
    frame1 = pygame.transform.scale(frame1, (BOAT_W, BOAT_H))
    frame2 = pygame.transform.scale(frame2, (BOAT_W, BOAT_H))

    boat_x = SCREEN_WIDTH // 2 - BOAT_W // 2
    boat_y = SCREEN_HEIGHT - BOAT_H - BOAT_OFFSET_Y
    player_boat_x = int(SCREEN_WIDTH * PLAYER_BOAT_X_RATIO) - BOAT_W // 2
    ai_boat_x = int(SCREEN_WIDTH * AI_BOAT_X_RATIO) - BOAT_W // 2

    snd_row = pygame.mixer.Sound(os.path.join(aud_dir, "effect.wav"))
    snd_row.set_volume(0.5)
    snd_win = pygame.mixer.Sound(os.path.join(aud_dir, "win.wav"))
    snd_lose = pygame.mixer.Sound(os.path.join(aud_dir, "lose.wav"))
    pygame.mixer.music.load(os.path.join(aud_dir, "bg.wav"))
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
