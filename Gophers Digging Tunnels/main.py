import sys
import random
import pygame
import config as cfg
import items as itm
from player import Player
from grid import Grid
from particles import ParticleSystem
from renderer import Renderer


class GameState:
    MENU = 0
    PLAYING = 1
    BOSS_INTRO = 2
    LEVEL_COMPLETE = 3
    GAME_OVER = 4
    PAUSED = 5


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
        pygame.display.set_caption("Gophers Digging Tunnels")
        self.clock = pygame.time.Clock()
        self.renderer = Renderer(self.screen)
        self.particles = ParticleSystem()
        self.player = Player()
        self.grid = Grid()
        self.state = GameState.MENU
        self.level_num = 1
        self.selected_level = 1
        self.boss_intro_timer = 0.0
        self.boss_intro_name = ""
        self.game_over_timer = 0.0
        self.total_score = 0
        self.inventory_slot = 1

        self._dir_keys = {
            pygame.K_UP: "up",
            pygame.K_DOWN: "down",
            pygame.K_LEFT: "left",
            pygame.K_RIGHT: "right",
        }

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(cfg.FPS) / 1000.0
            dt = min(dt, 0.1)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == GameState.PLAYING:
                            self.state = GameState.MENU
                        elif self.state == GameState.MENU:
                            running = False
                    elif event.key == pygame.K_1:
                        self.inventory_slot = 1
                    elif event.key == pygame.K_2:
                        self.inventory_slot = 2
                    else:
                        self._on_key(event.key)

            self._update(dt)
            self._render()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def _on_key(self, key):
        if self.state == GameState.MENU:
            if key == pygame.K_SPACE:
                self._start_game()
            elif key == pygame.K_LEFT:
                self.selected_level = max(1, self.selected_level - 1)
            elif key == pygame.K_RIGHT:
                self.selected_level = min(6, self.selected_level + 1)

        elif self.state == GameState.LEVEL_COMPLETE:
            if key == pygame.K_SPACE:
                self.level_num += 1
                if self.level_num > 6:
                    self.state = GameState.GAME_OVER
                    self.total_score = self.player.score
                    self.game_over_timer = 3.0
                else:
                    self._start_level(self.level_num)

        elif self.state == GameState.GAME_OVER:
            if key == pygame.K_r:
                self._start_game()
            elif key == pygame.K_m:
                self.state = GameState.MENU

        elif self.state == GameState.BOSS_INTRO:
            pass

        elif self.state == GameState.PLAYING:
            if key in self._dir_keys:
                self._process_move(self._dir_keys[key])
            elif key == pygame.K_SPACE:
                slot = self.inventory_slot - 1
                result = self.player.use_item(slot, self.grid)
                if result:
                    self._handle_use_effect(result)

    def _process_move(self, direction):
        if self.player.frozen > 0:
            return
        result = self.player.move(direction, self.grid)
        self._handle_move_result(result)

    def _handle_move_result(self, result):
        px = self.player.get_x()
        py = self.player.get_y()

        if result.get("blocked"):
            self.renderer.add_floating_text("Rock!", px, py - 15, (180, 180, 180))
            return

        if not result.get("moved"):
            return

        if result.get("dug"):
            self.particles.emit_dig(px, py)

        if result.get("combat"):
            self.particles.emit_damage(px, py)
            self.renderer.add_shake()

        if result.get("score", 0) > 0:
            combo_mult = 1
            for t, m in sorted(cfg.COMBO_BONUS.items()):
                if self.player.combo >= t:
                    combo_mult = m
            score_text = f"+{result['score']}"
            if combo_mult > 1:
                score_text += f" x{combo_mult}"
            self.particles.emit_coin(px, py, (255, 220, 50))
            self.renderer.add_floating_text(score_text, px, py - 20, (255, 230, 100))

        if result.get("enemy_killed"):
            enemy = result["enemy_killed"]
            stats = itm.ENEMY_STATS.get(enemy.type, {})
            name = stats.get("name", "Enemy")
            self.renderer.add_floating_text(f"Defeated {name}!", px, py - 25, (255, 150, 50))
            self.particles.emit_explosion(px, py)

        if result.get("damage"):
            self.particles.emit_damage(px, py)
            self.renderer.add_shake()
            self.renderer.add_floating_text(f"-{result['damage']} HP", px, py - 15, (255, 50, 50))

        if result.get("item"):
            item = result["item"]
            if item == itm.ItemType.BOSS_LAIR:
                boss_name = itm.ENEMY_STATS.get(
                    itm.EnemyType.MOLE_KING if self.level_num >= 5 else itm.EnemyType.GIANT_WORM, {}
                ).get("name", "Boss")
                self.boss_intro_name = boss_name
                self.state = GameState.BOSS_INTRO
                self.boss_intro_timer = 2.0
                self.grid.activate_boss_lair(self.player.col, self.player.row)
                self.particles.emit_boss(px, py)
            elif item in itm.ITEM_INFO:
                info = itm.ITEM_INFO[item]
                name = info.get("name", "???")
                color = info.get("color", (255, 255, 255))
                if info.get("heal"):
                    self.particles.emit_heal(px, py)
                    self.renderer.add_floating_text(f"{name} +HP", px, py - 20, (100, 255, 100))
                elif info.get("damage"):
                    self.renderer.add_floating_text(f"{name}!", px, py - 20, (255, 50, 50))
                elif info.get("score"):
                    self.renderer.add_floating_text(f"{name}!", px, py - 20, color)
                elif info.get("shield_turns"):
                    self.renderer.add_floating_text("Shield!", px, py - 20, (100, 180, 255))
                elif info.get("drill_turns"):
                    self.renderer.add_floating_text("Drill Boost!", px, py - 20, (200, 180, 100))
                elif info.get("has_key"):
                    self.renderer.add_floating_text("Key! Opens chests", px, py - 20, (255, 220, 80))
                elif info.get("random"):
                    self.renderer.add_floating_text("Mushroom!?", px, py - 20, (200, 50, 200))
                elif info.get("blocked"):
                    pass

        if result.get("inventory_item"):
            item = result["inventory_item"]
            name = itm.ITEM_INFO.get(item, {}).get("name", "Item")
            self.renderer.add_floating_text(f"{name} -> Bag", px, py - 20, (200, 200, 255))

        if result.get("push", 0) > 0:
            push = result["push"]
            direction = self.player.facing
            dc, dr = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}[direction]
            self.renderer.add_floating_text("Swept away!", px, py, (50, 150, 220))
            for _ in range(push):
                nc = self.player.col + dc
                nr = self.player.row + dr
                if 0 <= nc < self.grid.cols and 0 <= nr < self.grid.rows:
                    cell = self.grid.cells[nr][nc]
                    if cell.content == itm.ItemType.ROCK and not cell.dug:
                        break
                    self.player.col = nc
                    self.player.row = nr
                    if not cell.dug:
                        cell.dug = True
                        cell.content = itm.ItemType.EMPTY
                        self.particles.emit_dig(
                            cfg.GRID_OFFSET_X + nc * cfg.CELL_SIZE + cfg.CELL_SIZE // 2,
                            cfg.GRID_OFFSET_Y + nr * cfg.CELL_SIZE + cfg.CELL_SIZE // 2,
                        )

        if result.get("stun", 0) > 0:
            self.player.frozen = result["stun"]
            self.renderer.add_floating_text("Stunned!", px, py - 15, (200, 200, 100))

        if result.get("teleport"):
            for _ in range(20):
                tc = random.randint(0, self.grid.cols - 1)
                tr = random.randint(1, self.grid.rows - 2)
                cell = self.grid.cells[tr][tc]
                if cell.dug and cell.content != itm.ItemType.ROCK:
                    self.player.col = tc
                    self.player.row = tr
                    break
            self.particles.emit_explosion(px, py)
            nx = self.player.get_x()
            ny = self.player.get_y()
            self.particles.emit_explosion(nx, ny)
            self.renderer.add_floating_text("Teleported!", nx, ny, (150, 50, 220))

        if result.get("chest"):
            items_text = ", ".join([
                itm.ITEM_INFO.get(i, {}).get("name", "?") for i in result.get("chest_items", [])
            ])
            self.renderer.add_floating_text(f"Chest: {items_text}", px, py - 25, (255, 220, 80))

        if result.get("secret_room"):
            self.renderer.add_floating_text("Secret Room!", px, py - 20, (255, 230, 100))

        if result.get("nest_destroyed"):
            self.renderer.add_floating_text("Nest destroyed! +150", px, py - 20, (255, 150, 50))
            self.particles.emit_explosion(px, py)

        if not self.player.alive:
            self.state = GameState.GAME_OVER
            self.total_score = self.player.score
            self.game_over_timer = 3.0

        if self.state == GameState.PLAYING and self.player.row >= self.grid.rows - 1:
            if not self.grid.boss_active:
                if self.grid.boss_defeated:
                    if self.player.fossils >= 3:
                        self.player.score += 200
                    self.state = GameState.LEVEL_COMPLETE
                else:
                    self.state = GameState.LEVEL_COMPLETE

    def _handle_use_effect(self, result):
        if result is None:
            return
        px = self.player.get_x()
        py = self.player.get_y()
        effect_type = result.get("type")

        if effect_type == "bomb":
            for dc in range(-1, 2):
                for dr in range(-1, 2):
                    nc = self.player.col + dc
                    nr = self.player.row + dr
                    if 0 <= nc < self.grid.cols and 0 <= nr < self.grid.rows:
                        cell = self.grid.cells[nr][nc]
                        cell.dug = True
                        cell.content = itm.ItemType.EMPTY
                        ex = cfg.GRID_OFFSET_X + nc * cfg.CELL_SIZE + cfg.CELL_SIZE // 2
                        ey = cfg.GRID_OFFSET_Y + nr * cfg.CELL_SIZE + cfg.CELL_SIZE // 2
                        self.particles.emit_explosion(ex, ey)
            self.renderer.add_shake(8, 0.3)
            self.renderer.add_floating_text("BOOM!", px, py, (255, 100, 30))

        elif effect_type == "freeze":
            count = 0
            for e in self.grid.enemies:
                dist = abs(e.col - self.player.col) + abs(e.row - self.player.row)
                if dist <= 4:
                    e.frozen_timer = 3.0
                    count += 1
            if self.grid.boss and self.grid.boss_active:
                dist = abs(self.grid.boss.col - self.player.col) + abs(self.grid.boss.row - self.player.row)
                if dist <= 4:
                    self.grid.boss.frozen_timer = 3.0
                    count += 1
            self.renderer.add_floating_text(f"Frozen {count} enemies!", px, py, (100, 200, 255))

        elif effect_type == "fire":
            count = 0
            for dc, dr in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nc = self.player.col + dc
                nr = self.player.row + dr
                for e in self.grid.enemies[:]:
                    if e.col == nc and e.row == nr:
                        e.hp -= 3
                        if e.hp <= 0:
                            self.player.score += itm.ENEMY_STATS.get(e.type, {}).get("score", 0)
                            self.grid.enemies.remove(e)
                        count += 1
                if self.grid.boss and self.grid.boss_active:
                    if self.grid.boss.col == nc and self.grid.boss.row == nr:
                        self.grid.boss.hp -= 3
                        count += 1
                        if self.grid.boss.hp <= 0:
                            self.grid.boss_active = False
                            self.grid.boss_defeated = True
                            self.player.score += 1000
                            bx = cfg.GRID_OFFSET_X + self.grid.boss.col * cfg.CELL_SIZE + cfg.CELL_SIZE // 2
                            by = cfg.GRID_OFFSET_Y + self.grid.boss.row * cfg.CELL_SIZE + cfg.CELL_SIZE // 2
                            self.particles.emit_boss(bx, by)
                            self.particles.emit_coin(bx, by, (255, 220, 50), 30)
                            self.renderer.add_floating_text("BOSS DEFEATED! +1000", bx, by - 30, (255, 220, 50))
                            self.grid.boss = None
                ex = cfg.GRID_OFFSET_X + nc * cfg.CELL_SIZE + cfg.CELL_SIZE // 2
                ey = cfg.GRID_OFFSET_Y + nr * cfg.CELL_SIZE + cfg.CELL_SIZE // 2
                self.particles.emit_explosion(ex, ey)
            self.renderer.add_floating_text(f"Fire! Hit {count}", px, py, (255, 120, 30))

        elif effect_type == "attack_up":
            self.renderer.add_floating_text(f"ATK +{result['amount']}!", px, py, (255, 150, 50))

    def _update(self, dt):
        self.renderer.update(dt)
        self.particles.update(dt)

        if self.state == GameState.PLAYING:
            self.player.update(dt)

            self.grid.update_enemies(dt, self.player.col, self.player.row, self.particles)
            self.grid.update_nests(dt)

            self._check_enemy_attacks()

            if self.player.hp <= 0:
                self.player.alive = False
                self.state = GameState.GAME_OVER
                self.total_score = self.player.score
                self.game_over_timer = 3.0

            if self.player.row >= self.grid.rows - 1 and not self.grid.boss_active:
                if self.player.fossils >= 3:
                    self.player.score += 200
                self.state = GameState.LEVEL_COMPLETE

        elif self.state == GameState.BOSS_INTRO:
            self.boss_intro_timer -= dt
            if self.boss_intro_timer <= 0:
                self.state = GameState.PLAYING

        elif self.state == GameState.GAME_OVER:
            self.game_over_timer -= dt

    def _check_enemy_attacks(self):
        for enemy in self.grid.enemies[:]:
            if enemy.hp <= 0:
                continue
            if enemy.col == self.player.col and enemy.row == self.player.row:
                continue
            if abs(enemy.col - self.player.col) + abs(enemy.row - self.player.row) == 1:
                stats = itm.ENEMY_STATS.get(enemy.type, {})
                dmg = stats.get("damage", 0.5)
                if self.player.shield > 0:
                    self.player.shield -= 1
                elif self.player.invincible <= 0:
                    px = self.player.get_x()
                    py = self.player.get_y()
                    if stats.get("poison"):
                        self.player.poison = stats["poison"]
                    if stats.get("web"):
                        self.player.frozen = 1.0
                    if stats.get("steals"):
                        stolen = min(stats["steals"], self.player.score // 10 * 10)
                        self.player.score -= stolen
                        self.renderer.add_floating_text(f"-{stolen} stolen!", px, py - 15, (255, 150, 50))
                    self.player.hp -= dmg
                    self.player.invincible = cfg.PLAYER_INVINCIBLE_TIME
                    self.player.combo = 0
                    self.particles.emit_damage(px, py)
                    self.renderer.add_shake()
                    self.renderer.add_floating_text(f"-{dmg} HP", px, py - 20, (255, 50, 50))

        if self.grid.boss and self.grid.boss_active and self.grid.boss.hp > 0:
            boss = self.grid.boss
            if abs(boss.col - self.player.col) + abs(boss.row - self.player.row) == 1:
                stats = itm.ENEMY_STATS.get(boss.type, {})
                dmg = stats.get("damage", 2)
                px = self.player.get_x()
                py = self.player.get_y()
                if self.player.shield > 0:
                    self.player.shield -= 1
                elif self.player.invincible <= 0:
                    self.player.hp -= dmg
                    self.player.invincible = cfg.PLAYER_INVINCIBLE_TIME
                    self.player.combo = 0
                    self.particles.emit_damage(px, py)
                    self.renderer.add_shake(10, 0.3)
                    self.renderer.add_floating_text(f"-{dmg} HP!", px, py - 25, (255, 100, 50))

            if boss.hp <= 0 and self.grid.boss_active:
                self.grid.boss_active = False
                self.grid.boss_defeated = True
                self.grid.boss = None
                self.player.score += 1000
                bx = cfg.GRID_OFFSET_X + boss.col * cfg.CELL_SIZE + cfg.CELL_SIZE // 2
                by = cfg.GRID_OFFSET_Y + boss.row * cfg.CELL_SIZE + cfg.CELL_SIZE // 2
                self.particles.emit_boss(bx, by)
                self.particles.emit_coin(bx, by, (255, 220, 50), 30)
                self.renderer.add_floating_text("BOSS DEFEATED! +1000", bx, by - 30, (255, 220, 50))

    def _render(self):
        if self.state == GameState.MENU:
            self.renderer.draw_menu(self.selected_level)

        elif self.state == GameState.PLAYING:
            self.renderer.draw_grid(self.grid)
            self.renderer.draw_player(self.player)
            self.renderer.draw_enemies(self.grid, self.player)
            self.particles.draw(self.screen)
            self.renderer.draw_hud(self.player, self.level_num)
            self.renderer.draw_floating_texts()

        elif self.state == GameState.BOSS_INTRO:
            self.renderer.draw_grid(self.grid)
            self.renderer.draw_player(self.player)
            self.renderer.draw_enemies(self.grid, self.player)
            self.particles.draw(self.screen)
            self.renderer.draw_hud(self.player, self.level_num)
            self.renderer.draw_boss_intro(self.boss_intro_name)

        elif self.state == GameState.LEVEL_COMPLETE:
            self.renderer.draw_grid(self.grid)
            self.renderer.draw_player(self.player)
            self.renderer.draw_enemies(self.grid, self.player)
            self.particles.draw(self.screen)
            self.renderer.draw_hud(self.player, self.level_num)
            self.renderer.draw_level_complete(self.player, self.level_num)

        elif self.state == GameState.GAME_OVER:
            self.renderer.draw_grid(self.grid)
            self.renderer.draw_player(self.player)
            self.renderer.draw_enemies(self.grid, self.player)
            self.particles.draw(self.screen)
            self.renderer.draw_hud(self.player, self.level_num)
            self.renderer.draw_game_over(self.player, self.total_score,
                                         self.grid.boss_defeated)

    def _start_game(self):
        self.level_num = self.selected_level
        self._start_level(self.level_num)

    def _start_level(self, level_num):
        self.level_num = level_num
        self.player = Player()
        self.grid = Grid()
        self.grid.generate(level_num)
        self.state = GameState.PLAYING
        self.total_score = 0


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
