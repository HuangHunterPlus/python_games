import sys
import pygame
from config import *
import assets
from state import menu_state, reset_game, reset_ai_game, update_ai, handle_correct, handle_wrong
from input_handler import KEY_TO_CHAR, SCAN_TO_CHAR
from renderer import draw


def main():
    clock = pygame.time.Clock()
    g = menu_state()
    running = True
    last_input = -200

    while running:
        dt = min(clock.tick(FPS) / 1000.0, 0.05)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if g["state"] == "menu":
                    mx, my = ev.pos
                    bw = 240
                    y1, y2 = 310, 400
                    btn1 = pygame.Rect(SCREEN_WIDTH // 2 - bw // 2, y1, bw, 56)
                    btn2 = pygame.Rect(SCREEN_WIDTH // 2 - bw // 2, y2, bw, 56)
                    if btn1.collidepoint(mx, my):
                        g = reset_game()
                    elif btn2.collidepoint(mx, my):
                        g = reset_ai_game()
            if ev.type == pygame.TEXTINPUT:
                if g["state"] == "playing" and g["penalty"] <= 0:
                    ch = ev.text.lower()
                    if ch and ch.isalpha() and len(ch) == 1:
                        now = pygame.time.get_ticks()
                        if now - last_input < DEBOUNCE_MS:
                            continue
                        last_input = now
                        if ch == g["seq"][g["idx"]]:
                            handle_correct(g, ch)
                        else:
                            handle_wrong(g, ch)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    if g["state"] == "menu":
                        running = False
                    else:
                        g = menu_state()
                if g["state"] == "menu":
                    if ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                        g = reset_game()
                    elif ev.key == pygame.K_2:
                        g = reset_ai_game()
                if g["state"] in ("win", "gameover"):
                    if ev.key == pygame.K_r:
                        if g.get("mode") == "ai":
                            g = reset_ai_game()
                        else:
                            g = reset_game()
                if g["state"] == "playing" and g["penalty"] <= 0:
                    ch = KEY_TO_CHAR.get(ev.key)
                    if ch is None:
                        ch = SCAN_TO_CHAR.get(ev.scancode)
                    if ch is not None:
                        now = pygame.time.get_ticks()
                        if now - last_input < DEBOUNCE_MS:
                            continue
                        last_input = now
                        if ch == g["seq"][g["idx"]]:
                            handle_correct(g, ch)
                        else:
                            handle_wrong(g, ch)

        if g["state"] == "playing":
            g["elapsed"] += dt
            if g.get("mode") == "ai":
                update_ai(g, dt)
                if g["dist"] >= GOAL_DIST or g["ai_dist"] >= GOAL_DIST:
                    g["state"] = "win"
                elif g["elapsed"] >= GAME_TIME:
                    g["state"] = "gameover"
            else:
                if g["elapsed"] >= GAME_TIME:
                    g["state"] = "gameover"
                if g["dist"] >= GOAL_DIST:
                    g["state"] = "win"

        if g["state"] == "win" and not g["sound_played"]:
            assets.snd_win.play()
            g["sound_played"] = True
        if g["state"] == "gameover" and not g["sound_played"]:
            assets.snd_lose.play()
            g["sound_played"] = True

        if g["penalty"] > 0:
            g["penalty"] -= dt

        if g["row_timer"] > 0:
            g["row_timer"] -= dt
            g["frame_timer"] -= dt
            if g["frame_timer"] <= 0:
                g["frame"] = 1 - g["frame"]
                g["frame_timer"] = FRAME_INTERVAL
            if g["row_timer"] <= 0:
                g["frame"] = 0
        else:
            g["frame"] = 0

        if g.get("mode") == "ai":
            if g["ai_row_timer"] > 0:
                g["ai_row_timer"] -= dt
                g["ai_frame_timer"] -= dt
                if g["ai_frame_timer"] <= 0:
                    g["ai_frame"] = 1 - g["ai_frame"]
                    g["ai_frame_timer"] = FRAME_INTERVAL
                if g["ai_row_timer"] <= 0:
                    g["ai_frame"] = 0
            else:
                g["ai_frame"] = 0

        if g["wrong_flash"] > 0:
            g["wrong_flash"] -= dt

        for p in g["particles"][:]:
            p.update(dt)
            if not p.alive:
                g["particles"].remove(p)

        draw(g)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    assets.init()
    main()
