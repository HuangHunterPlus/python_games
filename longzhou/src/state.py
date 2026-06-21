import random
import string
from config import SEQUENCE_LENGTH, GOAL_DIST, AI_TYPING_INTERVAL, AI_TYPING_JITTER, AI_ACCURACY, AI_CORRECT_DIST, AI_SEQ_BONUS
import assets
from particles import Splash


def gen_seq():
    return "".join(random.choices(string.ascii_lowercase, k=SEQUENCE_LENGTH))


def menu_state():
    return {
        "state": "menu",
        "seq": "",
        "idx": 0,
        "elapsed": 0.0,
        "dist": 0.0,
        "completed": 0,
        "frame": 0,
        "frame_timer": 0.0,
        "row_timer": 0.0,
        "penalty": 0.0,
        "wrong_flash": 0.0,
        "particles": [],
        "debug": "",
        "scroll_y": 0.0,
        "sound_played": False,
        "menu_alpha": 0,
    }


def reset_game():
    return {
        "state": "playing",
        "seq": gen_seq(),
        "idx": 0,
        "elapsed": 0.0,
        "dist": 0.0,
        "completed": 0,
        "frame": 0,
        "frame_timer": 0.0,
        "row_timer": 0.0,
        "penalty": 0.0,
        "wrong_flash": 0.0,
        "particles": [],
        "debug": "",
        "scroll_y": 0.0,
        "sound_played": False,
    }


def reset_ai_game():
    return {
        "state": "playing",
        "mode": "ai",
        "seq": gen_seq(),
        "idx": 0,
        "dist": 0.0,
        "completed": 0,
        "frame": 0,
        "frame_timer": 0.0,
        "row_timer": 0.0,
        "penalty": 0.0,
        "wrong_flash": 0.0,
        "particles": [],
        "debug": "",
        "scroll_y": 0.0,
        "sound_played": False,
        "elapsed": 0.0,
        "ai_seq": gen_seq(),
        "ai_idx": 0,
        "ai_dist": 0.0,
        "ai_completed": 0,
        "ai_timer": AI_TYPING_INTERVAL,
        "ai_row_timer": 0.0,
        "ai_frame": 0,
        "ai_frame_timer": 0.0,
    }


def update_ai(g, dt):
    if g["state"] != "playing":
        return
    g["ai_timer"] -= dt
    if g["ai_timer"] <= 0 and g["ai_idx"] < len(g["ai_seq"]):
        diff = g["ai_dist"] - g["dist"]
        rb = diff / GOAL_DIST * 0.35
        rb = max(-0.15, min(0.15, rb))
        interval = AI_TYPING_INTERVAL + rb + random.uniform(-AI_TYPING_JITTER, AI_TYPING_JITTER)
        g["ai_timer"] = max(0.2, interval)
        if random.random() < AI_ACCURACY:
            g["ai_idx"] += 1
            g["ai_dist"] += AI_CORRECT_DIST
            g["ai_row_timer"] = 0.55
            g["ai_frame_timer"] = 0.15
            if g["ai_idx"] >= len(g["ai_seq"]):
                g["ai_completed"] += 1
                g["ai_dist"] += AI_SEQ_BONUS
                g["ai_seq"] = gen_seq()
                g["ai_idx"] = 0
        else:
            g["ai_timer"] += 0.3


def handle_correct(g, ch):
    assets.snd_row.play()
    g["idx"] += 1
    g["row_timer"] = 0.55
    g["dist"] += 4
    g["frame_timer"] = 0.15
    bx = assets.player_boat_x if g.get("mode") == "ai" else assets.boat_x
    cx = bx + assets.BOAT_W // 2 + random.randint(-25, 25)
    cy = assets.boat_y + assets.BOAT_H - 15
    for _ in range(6):
        g["particles"].append(Splash(cx, cy))
    if g["idx"] >= len(g["seq"]):
        g["completed"] += 1
        g["dist"] += 8
        g["seq"] = gen_seq()
        g["idx"] = 0
        for _ in range(16):
            g["particles"].append(Splash(cx, cy))
    g["debug"] = f"正确: {ch}"


def handle_wrong(g, ch):
    g["penalty"] = 0.7
    g["wrong_flash"] = 0.25
    g["row_timer"] = 0
    g["frame"] = 0
    g["debug"] = f"错误: 需要 {g['seq'][g['idx']]}, 按下 {ch}"
