"""
Top-down ping pong — main entry point.
Paddles auto-track the ball; Player 1 hits with Space, Player 2 with 1.
"""

import sys
import pygame


def main():
    from src import config as cfg

    # ── 1. Load background ──
    try:
        surf = pygame.image.load(cfg.BACKGROUND_PATH)
        img_w, img_h = surf.get_size()
    except FileNotFoundError:
        print(f"[Error] Background not found: {cfg.BACKGROUND_PATH}")
        img_w, img_h = 1054, 1492

    # ── 2. Init config ──
    cfg.init(img_w, img_h)

    # ── 3. Init pygame ──
    pygame.init()
    screen = pygame.display.set_mode((cfg.WINDOW_WIDTH, cfg.WINDOW_HEIGHT))
    pygame.display.set_caption(cfg.TITLE)
    clock = pygame.time.Clock()

    print(f"[Info] Window: {cfg.WINDOW_WIDTH}x{cfg.WINDOW_HEIGHT}")

    # ── 4. Import game modules (after config is ready) ──
    from src.game_state import GameState, State
    from src.objects import Ball, Paddle
    from src.objects.collision import is_ball_in_hit_zone, hit_ball, check_ball_wall
    from src.input import Controller
    from src.rendering import Renderer

    # ── 5. Create objects ──
    state = GameState()
    ball = Ball()
    paddles = [Paddle(1), Paddle(2)]
    renderer = Renderer(screen)

    def reset_for_serve():
        """Place the ball at the server's position and wait for serve."""
        ball.stop()
        server = state.server
        if server == 1:
            ball.x = cfg.TABLE_CENTER_X
            ball.y = cfg.PADDLE1_INIT_Y - 40
        else:
            ball.x = cfg.TABLE_CENTER_X
            ball.y = cfg.PADDLE2_INIT_Y + 40
        paddles[0].reset_position()
        paddles[1].reset_position()

    def do_serve(player: int) -> None:
        """Execute a serve."""
        direction = "up" if player == 1 else "down"
        ball.reset(direction=direction, server=player)
        renderer.effects.emit_hit(ball.x, ball.y)

    # ── 6. Main loop ──
    running = True
    state_changed = True

    while running:
        dt = clock.tick(cfg.FPS) / 1000.0
        time_ms = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        prev_state = state.current

        # ── Events ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                if state.current == State.TITLE and event.key == pygame.K_SPACE:
                    state.__init__()
                    state.transition(State.COUNTDOWN)
                    reset_for_serve()

                if state.current == State.GAME_OVER and event.key == pygame.K_r:
                    state.__init__()
                    state.transition(State.COUNTDOWN)
                    reset_for_serve()

        # ── State update ──
        state.update(dt)

        current = state.current
        if current != prev_state:
            state_changed = True
            if current == State.COUNTDOWN:
                reset_for_serve()
            elif current == State.SCORED:
                ball.stop()
        else:
            state_changed = False

        # ── PLAYING logic ──
        if current == State.PLAYING:
            for paddle in paddles:
                paddle.auto_track(ball.x, dt)
                paddle.update_cooldown(dt)

            if ball.is_moving:
                ball.update(dt, time_ms)

                for paddle in paddles:
                    if paddle.can_hit() and is_ball_in_hit_zone(ball, paddle):
                        paddle.can_hit_flag = True
                        if Controller.is_player_hit(keys, paddle.player_id):
                            hit_ball(ball, paddle)
                            renderer.effects.emit_hit(ball.x, ball.y)
                            state.total_hits += 1
                            paddle.can_hit_flag = False
                    else:
                        paddle.can_hit_flag = False

                bounds = (cfg.TABLE_TOP, cfg.TABLE_BOTTOM,
                          cfg.TABLE_LEFT, cfg.TABLE_RIGHT)
                result = check_ball_wall(ball, bounds)

                if result == 'top':
                    renderer.effects.emit_score(ball.x, cfg.TABLE_TOP)
                    ball.stop()
                    state.add_score(1)
                elif result == 'bottom':
                    renderer.effects.emit_score(ball.x, cfg.TABLE_BOTTOM)
                    ball.stop()
                    state.add_score(2)

            else:
                player = state.server
                if Controller.is_player_hit(keys, player):
                    do_serve(player)

        renderer.effects.update(dt)

        show_serve_hint = (current == State.PLAYING and not ball.is_moving)
        renderer.render(
            ball=ball, paddles=paddles,
            state=state, time_ms=time_ms,
            show_serve_hint=show_serve_hint,
            server=state.server,
        )
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
