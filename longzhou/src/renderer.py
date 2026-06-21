import math
import pygame
from config import *
import assets


def draw(g):
    prog = min(g["dist"] / GOAL_DIST, 1.0)
    target = -int(assets.BG_MAX_SCROLL * (1.0 - prog))
    g["scroll_y"] += (target - g["scroll_y"]) * 0.08
    assets.screen.blit(assets.bg, (-assets.bg_ox, int(g["scroll_y"])))

    shimmer = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    shimmer.fill((30, 120, 220, int(12 + 8 * math.sin(g["elapsed"] * 3.5))))
    assets.screen.blit(shimmer, (0, 0))

    for p in g["particles"]:
        p.draw(assets.screen)

    if g["state"] == "menu":
        _draw_menu(g)
    elif g.get("mode") == "ai":
        _draw_ai_boats(g)
        _draw_ai_hud(g)
        if g["state"] == "win":
            _draw_ai_win(g)
        elif g["state"] == "gameover":
            _draw_ai_gameover(g)
    else:
        _draw_single_boat(g)
        _draw_hud(g, prog)
        if g["state"] == "win":
            _draw_win(g)
        elif g["state"] == "gameover":
            _draw_gameover(g, prog)

    pygame.display.flip()


# ---------- Menu ----------

def _draw_menu(g):
    g["menu_alpha"] = min(g["menu_alpha"] + 3, 180)
    ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    ov.fill((0, 0, 0, g["menu_alpha"]))
    assets.screen.blit(ov, (0, 0))

    title = assets.font_large.render("龙 舟 划 船", True, GOLD)
    assets.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 160)))

    sub = assets.font_med.render("按键输入字母 · 划向终点", True, (180, 180, 200))
    assets.screen.blit(sub, sub.get_rect(center=(SCREEN_WIDTH // 2, 230)))

    y1, y2 = 310, 400
    bw_btn = 240
    bh_btn = 56
    mx, my = pygame.mouse.get_pos()

    btn1 = pygame.Rect(SCREEN_WIDTH // 2 - bw_btn // 2, y1, bw_btn, bh_btn)
    h1 = btn1.collidepoint(mx, my)
    pygame.draw.rect(assets.screen, (110, 200, 80) if h1 else (70, 150, 50), btn1, border_radius=10)
    pygame.draw.rect(assets.screen, WHITE, btn1, 3, border_radius=10)
    t1 = assets.font_med.render("单人游戏", True, WHITE)
    assets.screen.blit(t1, t1.get_rect(center=btn1.center))

    btn2 = pygame.Rect(SCREEN_WIDTH // 2 - bw_btn // 2, y2, bw_btn, bh_btn)
    h2 = btn2.collidepoint(mx, my)
    pygame.draw.rect(assets.screen, (220, 160, 50) if h2 else (180, 120, 20), btn2, border_radius=10)
    pygame.draw.rect(assets.screen, GOLD, btn2, 3, border_radius=10)
    t2 = assets.font_med.render("人机对战", True, WHITE)
    assets.screen.blit(t2, t2.get_rect(center=btn2.center))

    hint = assets.font_sm.render("Enter / 点击选择模式", True, (150, 150, 160))
    assets.screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, 490)))


# ---------- Single player ----------

def _draw_single_boat(g):
    bob = int(6 * math.sin(g["elapsed"] * 16)) if g["row_timer"] > 0 else int(2 * math.sin(g["elapsed"] * 2.5))
    boat_img = assets.frame1 if g["frame"] == 0 else assets.frame2
    assets.screen.blit(boat_img, (assets.boat_x, assets.boat_y + bob))

    if g["wrong_flash"] > 0:
        flash = pygame.Surface((assets.BOAT_W, assets.BOAT_H), pygame.SRCALPHA)
        flash.fill((255, 40, 40, 120))
        assets.screen.blit(flash, (assets.boat_x, assets.boat_y + bob))

    if g["penalty"] > 0:
        dim = pygame.Surface((assets.BOAT_W, assets.BOAT_H), pygame.SRCALPHA)
        dim.fill((80, 80, 80, 100))
        assets.screen.blit(dim, (assets.boat_x, assets.boat_y + bob))


def _draw_hud(g, prog):
    t_left = max(0, int(GAME_TIME - g["elapsed"]))
    tc = RED if t_left <= 10 else WHITE
    if t_left <= 10 and int(g["elapsed"] * 5) % 2:
        tc = YELLOW

    timer_bg = pygame.Surface((130, 48), pygame.SRCALPHA)
    timer_bg.fill((0, 0, 0, 160))
    assets.screen.blit(timer_bg, (10, 10))
    timer_txt = assets.font_timer.render(f"{t_left}s", True, tc)
    assets.screen.blit(timer_txt, (22, 12))

    bw, bh = 320, 14
    bx = SCREEN_WIDTH // 2 - bw // 2
    by = 22
    pygame.draw.rect(assets.screen, (20, 20, 50), (bx - 2, by - 2, bw + 4, bh + 4), border_radius=8)
    pygame.draw.rect(assets.screen, (40, 40, 70), (bx, by, bw, bh), border_radius=6)
    pw = int(bw * prog)
    if pw > 0:
        pc = RED if prog < 0.3 else (YELLOW if prog < 0.7 else GREEN)
        pygame.draw.rect(assets.screen, pc, (bx, by, pw, bh), border_radius=6)
    pygame.draw.rect(assets.screen, WHITE, (bx - 2, by - 2, bw + 4, bh + 4), 3, border_radius=8)
    pct_txt = assets.font_sm.render(f"距离 {int(prog * 100)}%", True, WHITE)
    assets.screen.blit(pct_txt, (bx + bw + 10, by - 4))

    sc_bg = pygame.Surface((160, 42), pygame.SRCALPHA)
    sc_bg.fill((0, 0, 0, 160))
    assets.screen.blit(sc_bg, (SCREEN_WIDTH - 170, 10))
    sc_txt = assets.font_sm.render(f"完成 {g['completed']} 组", True, WHITE)
    assets.screen.blit(sc_txt, (SCREEN_WIDTH - 162, 16))

    _draw_letter_bar(g)

    if g["penalty"] > 0:
        hint = assets.font_med.render(" 按错了! 暂停...", True, RED)
        hr = hint.get_rect(center=(SCREEN_WIDTH // 2, 215))
        assets.screen.blit(hint, hr)

    if g["debug"]:
        dbg = assets.font_sm.render(g["debug"], True, YELLOW)
        assets.screen.blit(dbg, (SCREEN_WIDTH // 2 - dbg.get_width() // 2, 230))


def _draw_letter_bar(g, offset_x=0, seq_y=115):
    seq_bg = pygame.Surface((SCREEN_WIDTH, 70), pygame.SRCALPHA)
    seq_bg.fill((0, 0, 0, 190))
    assets.screen.blit(seq_bg, (0, seq_y))
    pygame.draw.line(assets.screen, (100, 100, 150), (0, seq_y + 70), (SCREEN_WIDTH, seq_y + 70), 2)

    letter_surfs = []
    total_w = 0
    for i, c in enumerate(g["seq"]):
        color = GREEN if i < g["idx"] else (GOLD if i == g["idx"] else (150, 150, 150))
        s = assets.font_large.render(c.upper(), True, color)
        letter_surfs.append(s)
        total_w += s.get_width() + 12
    total_w -= 12
    sx = SCREEN_WIDTH // 2 - total_w // 2 + offset_x
    x_off = 0
    for i, s in enumerate(letter_surfs):
        y = seq_y + 8
        if i == g["idx"] and g.get("penalty", 0) <= 0:
            y += int(4 * math.sin(g["elapsed"] * 7))
        assets.screen.blit(s, (sx + x_off, y))
        if i < g["idx"]:
            cx = sx + x_off + s.get_width() // 2
            pygame.draw.circle(assets.screen, GREEN, (cx, seq_y + 62), 4)
        x_off += s.get_width() + 12


def _draw_win(g):
    ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 210))
    assets.screen.blit(ov, (0, 0))

    t1 = assets.font_large.render("到达终点!", True, GOLD)
    r1 = t1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    assets.screen.blit(t1, r1)

    t_left = max(0, int(GAME_TIME - g["elapsed"]))
    t2 = assets.font_med.render(f"完成 {g['completed']} 组  剩余 {t_left}s", True, WHITE)
    r2 = t2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
    assets.screen.blit(t2, r2)

    t3 = assets.font_sm.render("按 R 重新开始  |  ESC 退出", True, (180, 180, 180))
    r3 = t3.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))
    assets.screen.blit(t3, r3)


def _draw_gameover(g, prog):
    ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 210))
    assets.screen.blit(ov, (0, 0))

    t1 = assets.font_large.render("时间到! 失败!", True, RED)
    r1 = t1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
    assets.screen.blit(t1, r1)

    t2 = assets.font_med.render(f"完成 {g['completed']} 组  距离 {int(prog * 100)}%", True, WHITE)
    r2 = t2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 25))
    assets.screen.blit(t2, r2)

    t3 = assets.font_sm.render("按 R 重新开始  |  ESC 退出", True, (180, 180, 180))
    r3 = t3.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 75))
    assets.screen.blit(t3, r3)


# ---------- AI mode ----------

def _draw_ai_boats(g):
    p_prog = min(g["dist"] / GOAL_DIST, 1.0)
    a_prog = min(g["ai_dist"] / GOAL_DIST, 1.0)
    a_vert = int(AI_VERTICAL_RANGE * max(0, a_prog - p_prog))

    pbob = int(6 * math.sin(g["elapsed"] * 16)) if g["row_timer"] > 0 else int(2 * math.sin(g["elapsed"] * 2.5))
    abob = int(6 * math.sin(g["elapsed"] * 16)) if g["ai_row_timer"] > 0 else int(2 * math.sin(g["elapsed"] * 2.5))

    p_img = assets.frame1 if g["frame"] == 0 else assets.frame2
    a_img = assets.frame1 if g.get("ai_frame", 0) == 0 else assets.frame2

    # Player boat (right) — fixed at bottom
    p_cx = assets.player_boat_x + assets.BOAT_W // 2
    assets.screen.blit(p_img, (assets.player_boat_x, assets.boat_y + pbob))
    lbl_p = assets.font_sm.render("玩 家", True, (80, 200, 255))
    lp = lbl_p.get_rect(center=(p_cx, assets.boat_y + pbob - 15))
    assets.screen.blit(lbl_p, lp)

    if g["wrong_flash"] > 0:
        flash = pygame.Surface((assets.BOAT_W, assets.BOAT_H), pygame.SRCALPHA)
        flash.fill((255, 40, 40, 120))
        assets.screen.blit(flash, (assets.player_boat_x, assets.boat_y + pbob))

    if g["penalty"] > 0:
        dim = pygame.Surface((assets.BOAT_W, assets.BOAT_H), pygame.SRCALPHA)
        dim.fill((80, 80, 80, 100))
        assets.screen.blit(dim, (assets.player_boat_x, assets.boat_y + pbob))

    # AI boat (left) — rises above player's level when ahead
    a_y = assets.boat_y + abob - a_vert
    a_cx = assets.ai_boat_x + assets.BOAT_W // 2

    for i in range(6):
        t = (i + 1) / 6.0
        ty = a_y + assets.BOAT_H + 4 + i * 8
        alpha = int(50 * (1 - t))
        tw = int(assets.BOAT_W * 0.6 * (1 - t * 0.5))
        wake = pygame.Surface((tw, 5), pygame.SRCALPHA)
        wake.fill((200, 220, 255, alpha))
        assets.screen.blit(wake, (a_cx - tw // 2, ty))

    if a_vert > 2:
        base_y = assets.boat_y + assets.BOAT_H
        for i in range(0, a_vert, 8):
            frac = i / AI_VERTICAL_RANGE
            alpha = int(40 * (1 - frac))
            dot = pygame.Surface((3, 3), pygame.SRCALPHA)
            dot.fill((255, 180, 80, alpha))
            assets.screen.blit(dot, (a_cx - 1, base_y - i - 1))

    assets.screen.blit(a_img, (assets.ai_boat_x, a_y))
    lbl_a = assets.font_sm.render("电 脑", True, (255, 180, 80))
    la = lbl_a.get_rect(center=(a_cx, a_y - 15))
    assets.screen.blit(lbl_a, la)


def _draw_ai_hud(g):
    t_left = max(0, int(GAME_TIME - g["elapsed"]))
    tc = RED if t_left <= 10 else WHITE
    if t_left <= 10 and int(g["elapsed"] * 5) % 2:
        tc = YELLOW

    timer_txt = assets.font_timer.render(f"{t_left}s", True, tc)
    tr = timer_txt.get_rect(center=(SCREEN_WIDTH // 2, 28))
    assets.screen.blit(timer_txt, tr)

    p_prog = min(g["dist"] / GOAL_DIST, 1.0)
    a_prog = min(g["ai_dist"] / GOAL_DIST, 1.0)

    # Player progress
    bw, bh = 300, 16
    px = 30
    py = 60
    pygame.draw.rect(assets.screen, (20, 20, 50), (px - 1, py - 1, bw + 2, bh + 2), border_radius=8)
    pygame.draw.rect(assets.screen, (40, 40, 80), (px, py, bw, bh), border_radius=6)
    if p_prog > 0:
        pygame.draw.rect(assets.screen, (80, 200, 255), (px, py, int(bw * p_prog), bh), border_radius=6)
    pygame.draw.rect(assets.screen, (80, 200, 255), (px - 1, py - 1, bw + 2, bh + 2), 2, border_radius=8)
    pt = assets.font_sm.render(f"玩家 {int(p_prog * 100)}%", True, (80, 200, 255))
    assets.screen.blit(pt, (px, py - 20))

    # AI progress
    ay = 100
    pygame.draw.rect(assets.screen, (20, 20, 50), (px - 1, ay - 1, bw + 2, bh + 2), border_radius=8)
    pygame.draw.rect(assets.screen, (40, 40, 80), (px, ay, bw, bh), border_radius=6)
    if a_prog > 0:
        pygame.draw.rect(assets.screen, (255, 180, 80), (px, ay, int(bw * a_prog), bh), border_radius=6)
    pygame.draw.rect(assets.screen, (255, 180, 80), (px - 1, ay - 1, bw + 2, bh + 2), 2, border_radius=8)
    at = assets.font_sm.render(f"电脑 {int(a_prog * 100)}%", True, (255, 180, 80))
    assets.screen.blit(at, (px, ay - 20))

    # Letter sequences
    _draw_letter_bar(g, offset_x=-80, seq_y=145)

    if g["penalty"] > 0:
        hint = assets.font_med.render(" 按错了! 暂停...", True, RED)
        hr = hint.get_rect(center=(SCREEN_WIDTH // 2, 245))
        assets.screen.blit(hint, hr)

    if g["debug"]:
        dbg = assets.font_sm.render(g["debug"], True, YELLOW)
        assets.screen.blit(dbg, (SCREEN_WIDTH // 2 - dbg.get_width() // 2, 260))


def _draw_ai_win(g):
    ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 210))
    assets.screen.blit(ov, (0, 0))

    ai_won = g["ai_dist"] >= GOAL_DIST and g["dist"] < GOAL_DIST
    if ai_won:
        msg = "电脑获胜!"
        color = (255, 180, 80)
    else:
        msg = "玩家获胜!"
        color = (80, 200, 255)
    t1 = assets.font_large.render(msg, True, color)
    r1 = t1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    assets.screen.blit(t1, r1)

    t_left = max(0, int(GAME_TIME - g["elapsed"]))
    t2 = assets.font_med.render(f"玩家 {int(g['completed'])} 组  vs  电脑 {int(g['ai_completed'])} 组  剩余 {t_left}s", True, WHITE)
    r2 = t2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
    assets.screen.blit(t2, r2)

    t3 = assets.font_sm.render("按 R 重新开始  |  ESC 退出", True, (180, 180, 180))
    r3 = t3.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))
    assets.screen.blit(t3, r3)


def _draw_ai_gameover(g):
    ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 210))
    assets.screen.blit(ov, (0, 0))

    p_prog = int(min(g["dist"] / GOAL_DIST, 1.0) * 100)
    a_prog = int(min(g["ai_dist"] / GOAL_DIST, 1.0) * 100)

    if p_prog > a_prog:
        msg = "玩家领先! 胜利!"
        color = (80, 200, 255)
    elif a_prog > p_prog:
        msg = "电脑领先! 失败!"
        color = (255, 180, 80)
    else:
        msg = "平局!"
        color = WHITE
    t1 = assets.font_large.render(msg, True, color)
    r1 = t1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    assets.screen.blit(t1, r1)

    t2 = assets.font_med.render(f"玩家 {p_prog}%  vs  电脑 {a_prog}%", True, WHITE)
    r2 = t2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
    assets.screen.blit(t2, r2)

    t3 = assets.font_sm.render("按 R 重新开始  |  ESC 退出", True, (180, 180, 180))
    r3 = t3.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))
    assets.screen.blit(t3, r3)
