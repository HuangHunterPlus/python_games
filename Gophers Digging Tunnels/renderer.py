import math
import pygame
import config as cfg
import items as itm


class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.font_small = pygame.font.Font(None, 18)
        self.font = pygame.font.Font(None, 24)
        self.font_med = pygame.font.Font(None, 32)
        self.font_large = pygame.font.Font(None, 48)
        self.font_title = pygame.font.Font(None, 56)
        self.font_huge = pygame.font.Font(None, 72)
        self.shake_offset = (0, 0)
        self.shake_timer = 0.0
        self.combo_text = ""
        self.combo_timer = 0.0
        self.floating_texts = []

    def add_shake(self, intensity=5, duration=0.2):
        self.shake_timer = duration
        self.shake_intensity = intensity

    def add_floating_text(self, text, x, y, color=(255, 255, 255), duration=1.0):
        self.floating_texts.append({
            "text": text, "x": x, "y": y, "color": color,
            "duration": duration, "timer": duration,
        })

    def update(self, dt):
        if self.shake_timer > 0:
            self.shake_timer -= dt
            import random
            self.shake_offset = (
                random.randint(-self.shake_intensity, self.shake_intensity),
                random.randint(-self.shake_intensity, self.shake_intensity),
            )
        else:
            self.shake_offset = (0, 0)

        for ft in self.floating_texts[:]:
            ft["timer"] -= dt
            ft["y"] -= 30 * dt
            if ft["timer"] <= 0:
                self.floating_texts.remove(ft)

        if self.combo_timer > 0:
            self.combo_timer -= dt

    def draw_grid(self, grid):
        sx, sy = self.shake_offset
        for row in range(grid.rows):
            for col in range(grid.cols):
                cell = grid.cells[row][col]
                x = cfg.GRID_OFFSET_X + col * cfg.CELL_SIZE + sx
                y = cfg.GRID_OFFSET_Y + row * cfg.CELL_SIZE + sy
                soil_color = cell.get_soil_color()
                rect = pygame.Rect(x, y, cfg.CELL_SIZE, cfg.CELL_SIZE)
                pygame.draw.rect(self.screen, soil_color, rect)
                pygame.draw.rect(self.screen, (30, 20, 10), rect, 1)

                if cell.dug:
                    if cell.content == itm.ItemType.ROCK:
                        pygame.draw.rect(self.screen, (130, 120, 110),
                                         (x + 4, y + 4, cfg.CELL_SIZE - 8, cfg.CELL_SIZE - 8))
                        pygame.draw.rect(self.screen, (100, 90, 80),
                                         (x + 4, y + 4, cfg.CELL_SIZE - 8, cfg.CELL_SIZE - 8), 2)
                    elif cell.content == itm.ItemType.NEST:
                        cx, cy = x + cfg.CELL_SIZE // 2, y + cfg.CELL_SIZE // 2
                        pygame.draw.circle(self.screen, (120, 60, 60), (cx, cy), 10)
                        pygame.draw.circle(self.screen, (80, 30, 30), (cx, cy), 5)
                    elif cell.content == itm.ItemType.BOSS_LAIR:
                        cx, cy = x + cfg.CELL_SIZE // 2, y + cfg.CELL_SIZE // 2
                        pygame.draw.circle(self.screen, (180, 30, 30), (cx, cy), 12)
                        pygame.draw.circle(self.screen, (120, 10, 10), (cx, cy), 7)
                        pygame.draw.line(self.screen, (255, 200, 50), (cx - 5, cy - 3), (cx - 5, cy - 8), 2)
                        pygame.draw.line(self.screen, (255, 200, 50), (cx + 5, cy - 3), (cx + 5, cy - 8), 2)

                if cell.revealed or cell.dug:
                    content = cell.content
                    if content != itm.ItemType.EMPTY and content in itm.ITEM_INFO:
                        info = itm.ITEM_INFO[content]
                        cx, cy = x + cfg.CELL_SIZE // 2, y + cfg.CELL_SIZE // 2
                        color = info.get("color", (255, 255, 255))
                        icon = info.get("icon", "?")
                        if cell.dug:
                            self._draw_item_icon(cx, cy, content, color, icon)
                        else:
                            s = pygame.Surface((cfg.CELL_SIZE, cfg.CELL_SIZE), pygame.SRCALPHA)
                            s.fill((255, 255, 255, 30))
                            self.screen.blit(s, (x, y))

    def _draw_item_icon(self, cx, cy, content, color, icon):
        if content in [itm.ItemType.COPPER, itm.ItemType.SILVER, itm.ItemType.GOLD,
                        itm.ItemType.DIAMOND, itm.ItemType.FOSSIL]:
            r = 6 if content == itm.ItemType.DIAMOND else 5
            if content == itm.ItemType.DIAMOND:
                points = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
                pygame.draw.polygon(self.screen, color, points)
            else:
                pygame.draw.circle(self.screen, color, (cx, cy), r)
                if content == itm.ItemType.GOLD:
                    pygame.draw.circle(self.screen, (255, 255, 200), (cx - 1, cy - 1), 2)
        elif content == itm.ItemType.SPIKE:
            points = [(cx, cy - 6), (cx + 4, cy + 4), (cx - 4, cy + 4)]
            pygame.draw.polygon(self.screen, color, points)
        elif content == itm.ItemType.MUSHROOM:
            pygame.draw.ellipse(self.screen, color, (cx - 5, cy - 6, 10, 6))
            pygame.draw.rect(self.screen, (200, 180, 160), (cx - 2, cy, 4, 6))
        elif content == itm.ItemType.WATER:
            for i in range(3):
                wave_y = cy - 3 + i * 3
                pygame.draw.arc(self.screen, color, (cx - 6, wave_y - 2, 12, 6), 0, math.pi, 2)
        elif content == itm.ItemType.TRAP:
            pygame.draw.rect(self.screen, (160, 120, 80), (cx - 6, cy - 2, 12, 8))
            pygame.draw.arc(self.screen, (180, 140, 100), (cx - 4, cy - 5, 8, 8), math.pi, 2 * math.pi, 2)
        elif content == itm.ItemType.CHEST:
            pygame.draw.rect(self.screen, color, (cx - 7, cy - 3, 14, 10))
            pygame.draw.rect(self.screen, (120, 100, 40), (cx - 7, cy - 3, 14, 10), 1)
            pygame.draw.circle(self.screen, (255, 220, 80), (cx, cy + 1), 2)
        elif content == itm.ItemType.PORTAL:
            pygame.draw.circle(self.screen, color, (cx, cy), 8)
            pygame.draw.circle(self.screen, (200, 150, 255), (cx, cy), 5)
            pygame.draw.circle(self.screen, (255, 255, 255), (cx, cy), 2)
        elif content == itm.ItemType.SECRET_ROOM:
            pygame.draw.circle(self.screen, color, (cx, cy), 8)
            text = self.font_small.render("!", True, (0, 0, 0))
            self.screen.blit(text, (cx - 3, cy - 7))
        elif content == itm.ItemType.CARROT:
            pygame.draw.polygon(self.screen, color, [(cx, cy - 7), (cx + 3, cy - 2),
                                                      (cx + 4, cy + 3), (cx - 4, cy + 3),
                                                      (cx - 3, cy - 2)])
        elif content == itm.ItemType.SHIELD:
            pygame.draw.arc(self.screen, color, (cx - 6, cy - 6, 12, 12), 0, math.pi, 3)
            pygame.draw.rect(self.screen, color, (cx - 1, cy - 3, 2, 8))
        elif content == itm.ItemType.DRILL:
            pygame.draw.polygon(self.screen, color, [(cx, cy - 7), (cx + 3, cy + 2),
                                                      (cx - 3, cy + 2)])
            pygame.draw.rect(self.screen, (100, 100, 100), (cx - 1, cy + 2, 2, 5))
        elif content == itm.ItemType.MAP:
            pygame.draw.rect(self.screen, color, (cx - 6, cy - 5, 12, 10))
            pygame.draw.line(self.screen, (100, 80, 40), (cx - 3, cy), (cx + 3, cy), 1)
            pygame.draw.line(self.screen, (100, 80, 40), (cx, cy - 3), (cx, cy + 3), 1)
        elif content == itm.ItemType.KEY:
            pygame.draw.circle(self.screen, color, (cx - 2, cy - 4), 3)
            pygame.draw.rect(self.screen, color, (cx - 2, cy - 1, 2, 7))
        elif content == itm.ItemType.BOMB:
            pygame.draw.circle(self.screen, color, (cx, cy), 6)
            pygame.draw.rect(self.screen, (100, 100, 100), (cx - 1, cy - 9, 2, 4))
        elif content == itm.ItemType.FREEZE:
            pygame.draw.circle(self.screen, color, (cx, cy), 5)
            pygame.draw.circle(self.screen, (200, 240, 255), (cx - 1, cy - 2), 2)
        elif content == itm.ItemType.FIRE_BREATH:
            points = [(cx, cy - 6), (cx + 4, cy + 2), (cx + 2, cy + 5),
                      (cx - 2, cy + 5), (cx - 4, cy + 2)]
            pygame.draw.polygon(self.screen, color, points)
        elif content == itm.ItemType.STONE_TOOTH:
            pygame.draw.polygon(self.screen, color, [(cx, cy - 6), (cx + 3, cy + 4), (cx - 3, cy + 4)])
        elif content == itm.ItemType.IRON_CLAW:
            for i in range(3):
                lx = cx - 4 + i * 4
                pygame.draw.line(self.screen, color, (lx, cy - 5), (lx, cy + 5), 2)

    def draw_player(self, player):
        if player.invincible > 0 and int(player.invincible * 10) % 2 == 0:
            return
        sx, sy = self.shake_offset
        x = cfg.GRID_OFFSET_X + player.col * cfg.CELL_SIZE + cfg.CELL_SIZE // 2 + sx
        y = cfg.GRID_OFFSET_Y + player.row * cfg.CELL_SIZE + cfg.CELL_SIZE // 2 + sy

        body_color = (240, 200, 60) if player.shield > 0 else (255, 210, 50)
        pygame.draw.circle(self.screen, body_color, (x, y), 12)
        pygame.draw.circle(self.screen, (220, 180, 40), (x, y), 12, 2)

        ex, ey = -3, -4
        if player.facing == "right":
            ex, ey = 4, -3
        elif player.facing == "left":
            ex, ey = -4, -3
        elif player.facing == "up":
            ex, ey = 0, -5
        elif player.facing == "down":
            ex, ey = 0, -2

        pygame.draw.circle(self.screen, (255, 255, 255), (x + ex - 4, y + ey - 1), 5)
        pygame.draw.circle(self.screen, (255, 255, 255), (x + ex + 4, y + ey - 1), 5)
        pygame.draw.circle(self.screen, (20, 20, 20), (x + ex - 4, y + ey - 1), 2)
        pygame.draw.circle(self.screen, (20, 20, 20), (x + ex + 4, y + ey - 1), 2)

        nose_x = x + ex
        pygame.draw.circle(self.screen, (20, 20, 20), (nose_x, y + ey + 3), 2)

        mouth_y = y + ey + 6
        if player.flash_timer > 0:
            pygame.draw.ellipse(self.screen, (20, 20, 20), (x + ex - 3, mouth_y, 6, 3))
        else:
            pygame.draw.arc(self.screen, (20, 20, 20), (x + ex - 4, mouth_y, 8, 5), 0, math.pi, 1)

        if player.shield > 0:
            pygame.draw.circle(self.screen, (100, 180, 255, 120), (x, y), 15, 3)

        if player.drill_boost > 0:
            for i in range(3):
                angle = pygame.time.get_ticks() / 100 + i * 2
                dx = math.cos(angle) * 10
                dy = math.sin(angle) * 10
                pygame.draw.line(self.screen, (200, 180, 100), (x, y), (x + dx, y + dy), 2)

    def draw_enemies(self, grid, player):
        sx, sy = self.shake_offset
        for enemy in grid.enemies:
            if enemy.hp <= 0:
                continue
            self._draw_enemy(enemy, sx, sy, player)
        if grid.boss and grid.boss_active and grid.boss.hp > 0:
            self._draw_enemy(grid.boss, sx, sy, player, is_boss=True)

    def _draw_enemy(self, enemy, sx, sy, player, is_boss=False):
        x = cfg.GRID_OFFSET_X + enemy.col * cfg.CELL_SIZE + cfg.CELL_SIZE // 2 + sx
        y = cfg.GRID_OFFSET_Y + enemy.row * cfg.CELL_SIZE + cfg.CELL_SIZE // 2 + sy

        stats = itm.ENEMY_STATS.get(enemy.type, {})
        color = stats.get("color", (200, 50, 50))
        shape = stats.get("shape", "circle")
        radius = stats.get("radius", 10)

        if enemy.frozen_timer > 0:
            s = pygame.Surface((radius * 3, radius * 3), pygame.SRCALPHA)
            pygame.draw.circle(s, (100, 180, 255, 150), (radius * 3 // 2, radius * 3 // 2), radius + 2)
            self.screen.blit(s, (x - radius * 3 // 2, y - radius * 3 // 2))

        if is_boss:
            shadow_color = (0, 0, 0, 80)
            s = pygame.Surface((radius * 3, radius * 3), pygame.SRCALPHA)
            pygame.draw.circle(s, shadow_color, (radius * 3 // 2 + 3, radius * 3 // 2 + 3), radius)
            self.screen.blit(s, (x - radius * 3 // 2, y - radius * 3 // 2))
            pygame.draw.circle(self.screen, (40, 10, 10), (x, y), radius + 3, 3)

        if shape == "ellipse":
            pygame.draw.ellipse(self.screen, color, (x - radius, y - radius // 2, radius * 2, radius))
        elif shape == "hexagon":
            pts = []
            for i in range(6):
                angle = math.pi / 3 * i - math.pi / 6
                pts.append((x + math.cos(angle) * radius, y + math.sin(angle) * radius))
            pygame.draw.polygon(self.screen, color, pts)
        elif shape == "star":
            pts = []
            for i in range(10):
                angle = math.pi / 5 * i - math.pi / 2
                r = radius if i % 2 == 0 else radius // 2
                pts.append((x + math.cos(angle) * r, y + math.sin(angle) * r))
            pygame.draw.polygon(self.screen, color, pts)
        elif shape == "triangle":
            pts = [(x, y - radius), (x + radius, y + radius), (x - radius, y + radius)]
            pygame.draw.polygon(self.screen, color, pts)
        elif shape == "diamond":
            pts = [(x, y - radius), (x + radius, y), (x, y + radius), (x - radius, y)]
            pygame.draw.polygon(self.screen, color, pts)
        elif shape == "crown":
            pygame.draw.circle(self.screen, color, (x, y), radius)
            pts = [(x - radius, y - 5), (x - radius // 2, y - radius - 3),
                   (x, y - 7), (x + radius // 2, y - radius - 3), (x + radius, y - 5)]
            pygame.draw.polygon(self.screen, (255, 200, 50), pts)
            for px, py in pts:
                pygame.draw.circle(self.screen, (255, 255, 100), (px, py), 2)
        else:
            pygame.draw.circle(self.screen, color, (x, y), radius)

        eye_offset = 3
        pygame.draw.circle(self.screen, (255, 255, 255), (x - eye_offset, y - 1), 3)
        pygame.draw.circle(self.screen, (255, 255, 255), (x + eye_offset, y - 1), 3)
        pygame.draw.circle(self.screen, (0, 0, 0), (x - eye_offset, y - 1), 1)
        pygame.draw.circle(self.screen, (0, 0, 0), (x + eye_offset, y - 1), 1)

        if enemy.hp < enemy.max_hp:
            bar_width = radius * 2
            bar_h = 3
            bar_y = y - radius - 6
            ratio = enemy.hp / enemy.max_hp
            pygame.draw.rect(self.screen, (60, 60, 60), (x - bar_width // 2, bar_y, bar_width, bar_h))
            bar_color = (50, 200, 50) if ratio > 0.5 else (200, 200, 50) if ratio > 0.25 else (200, 50, 50)
            pygame.draw.rect(self.screen, bar_color,
                             (x - bar_width // 2, bar_y, int(bar_width * ratio), bar_h))

    def draw_hud(self, player, level_num):
        pygame.draw.rect(self.screen, (30, 25, 20), (0, 0, cfg.SCREEN_WIDTH, cfg.HUD_HEIGHT))
        pygame.draw.line(self.screen, (60, 50, 40), (0, cfg.HUD_HEIGHT - 1), (cfg.SCREEN_WIDTH, cfg.HUD_HEIGHT - 1), 2)

        heart_x = 15
        for i in range(player.max_hp):
            hx = heart_x + i * 28
            if i < int(player.hp):
                pygame.draw.circle(self.screen, (220, 50, 50), (hx + 10, 18), 9)
                pygame.draw.circle(self.screen, (255, 80, 80), (hx + 10, 18), 6)
            elif i < player.hp:
                pygame.draw.circle(self.screen, (220, 50, 50), (hx + 10, 18), 9)
                pygame.draw.circle(self.screen, (255, 80, 80), (hx + 6, 18), 4)
                pygame.draw.circle(self.screen, (220, 50, 50), (hx + 14, 18), 4)
            else:
                pygame.draw.circle(self.screen, (80, 50, 50), (hx + 10, 18), 9)
                pygame.draw.circle(self.screen, (60, 40, 40), (hx + 10, 18), 6)

        score_text = self.font.render(f"Score: {player.score}", True, (255, 230, 150))
        self.screen.blit(score_text, (cfg.SCREEN_WIDTH // 2 - score_text.get_width() // 2, 8))

        depth = player.row
        total_depth = cfg.GRID_ROWS - 1
        depth_text = self.font_small.render(f"Depth: {depth}/{total_depth}", True, (200, 200, 200))
        self.screen.blit(depth_text, (cfg.SCREEN_WIDTH // 2 - depth_text.get_width() // 2, 32))

        level_text = self.font_small.render(f"Lv.{level_num}", True, (200, 180, 100))
        self.screen.blit(level_text, (cfg.SCREEN_WIDTH - 60, 10))

        combo_display = ""
        for threshold, mult in sorted(cfg.COMBO_BONUS.items(), reverse=True):
            if player.combo >= threshold:
                combo_display = f"x{mult}"
                break
        if combo_display and player.combo >= 2:
            combo_surf = self.font_med.render(combo_display, True, (255, 220, 50))
            self.screen.blit(combo_surf, (cfg.SCREEN_WIDTH - 100, 30))

        inv_x = 180
        for i in range(cfg.INVENTORY_SIZE):
            rect = pygame.Rect(inv_x + i * 40, 8, 34, 34)
            pygame.draw.rect(self.screen, (50, 40, 30), rect)
            pygame.draw.rect(self.screen, (80, 65, 50), rect, 2)

            item = player.inventory[i]
            if item and item in itm.ITEM_INFO:
                info = itm.ITEM_INFO[item]
                cx, cy = inv_x + i * 40 + 17, 25
                icon = info.get("icon", "?")
                color = info.get("color", (200, 200, 200))
                if item in [itm.ItemType.BOMB, itm.ItemType.FREEZE, itm.ItemType.FIRE_BREATH]:
                    pygame.draw.circle(self.screen, color, (cx, cy), 10)
                elif item in [itm.ItemType.STONE_TOOTH, itm.ItemType.IRON_CLAW]:
                    pygame.draw.polygon(self.screen, color, [(cx, cy - 8), (cx + 6, cy + 6), (cx - 6, cy + 6)])
                text = self.font_small.render(icon, True, (255, 255, 255))
                self.screen.blit(text, (cx - 4, cy - 7))
            else:
                text = self.font_small.render(str(i + 1), True, (100, 90, 80))
                self.screen.blit(text, (inv_x + i * 40 + 13, 15))

        effect_x = 280
        if player.shield > 0:
            shield_text = self.font_small.render(f"Shield:{player.shield}", True, (100, 180, 255))
            self.screen.blit(shield_text, (effect_x, 8))
            effect_x += shield_text.get_width() + 10
        if player.drill_boost > 0:
            drill_text = self.font_small.render(f"Drill:{player.drill_boost}", True, (200, 180, 100))
            self.screen.blit(drill_text, (effect_x, 8))
            effect_x += drill_text.get_width() + 10
        if player.poison > 0:
            poison_text = self.font_small.render(f"Poison:{int(player.poison)}", True, (200, 50, 200))
            self.screen.blit(poison_text, (effect_x, 28))
        if player.frozen > 0:
            freeze_text = self.font_small.render(f"Stun:{player.frozen:.1f}", True, (100, 200, 255))
            self.screen.blit(freeze_text, (effect_x + 80, 28))
        if player.attack > cfg.PLAYER_START_ATTACK:
            atk_text = self.font_small.render(f"ATK:{player.attack}", True, (255, 150, 50))
            self.screen.blit(atk_text, (effect_x + 160, 8))

    def draw_menu(self, selected_level=1):
        self.screen.fill((40, 30, 20))

        title = self.font_title.render("Gophers Digging Tunnels", True, (255, 220, 80))
        self.screen.blit(title, (cfg.SCREEN_WIDTH // 2 - title.get_width() // 2, 80))

        subtitle = self.font_med.render("Dig deep, find treasures, fight enemies!", True, (200, 180, 140))
        self.screen.blit(subtitle, (cfg.SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 140))

        gx = cfg.SCREEN_WIDTH // 2
        gy = 240
        pygame.draw.circle(self.screen, (255, 210, 50), (gx, gy), 25)
        pygame.draw.circle(self.screen, (255, 255, 255), (gx - 8, gy - 5), 8)
        pygame.draw.circle(self.screen, (255, 255, 255), (gx + 8, gy - 5), 8)
        pygame.draw.circle(self.screen, (20, 20, 20), (gx - 8, gy - 5), 3)
        pygame.draw.circle(self.screen, (20, 20, 20), (gx + 8, gy - 5), 3)
        pygame.draw.circle(self.screen, (20, 20, 20), (gx, gy + 3), 3)
        pygame.draw.arc(self.screen, (20, 20, 20), (gx - 5, gy + 5, 10, 6), 0, math.pi, 1)
        anim = math.sin(pygame.time.get_ticks() / 300) * 3
        pygame.draw.rect(self.screen, (180, 140, 60), (gx - 8, gy + 25 + anim, 5, 12))
        pygame.draw.rect(self.screen, (180, 140, 60), (gx + 3, gy + 25 - anim, 5, 12))

        level_text = self.font_med.render(f"Level {selected_level}", True, (255, 255, 255))
        self.screen.blit(level_text, (cfg.SCREEN_WIDTH // 2 - level_text.get_width() // 2, 310))

        hint = self.font.render("LEFT/RIGHT: Select Level    SPACE: Start    ESC: Quit", True, (180, 180, 180))
        self.screen.blit(hint, (cfg.SCREEN_WIDTH // 2 - hint.get_width() // 2, 360))

        controls1 = self.font_small.render("Arrow Keys / WASD: Dig & Move", True, (150, 150, 150))
        self.screen.blit(controls1, (cfg.SCREEN_WIDTH // 2 - controls1.get_width() // 2, 400))
        controls2 = self.font_small.render("SPACE: Use Item    1/2: Select Item Slot", True, (150, 150, 150))
        self.screen.blit(controls2, (cfg.SCREEN_WIDTH // 2 - controls2.get_width() // 2, 420))

        level_info = {
            1: "Sunny Meadow - Beginner friendly",
            2: "Dark Forest - Spiders & beetles appear",
            3: "Desert Ant Hill - Bandits & first Boss",
            4: "Frozen Cave - Scorpions & twin Boss",
            5: "Lava Depths - All enemies, Fire Boss",
            6: "Mole Kingdom - Ultimate challenge!",
        }
        desc = level_info.get(selected_level, "")
        desc_text = self.font_small.render(desc, True, (200, 200, 100))
        self.screen.blit(desc_text, (cfg.SCREEN_WIDTH // 2 - desc_text.get_width() // 2, 460))

        credit = self.font_small.render("v1.0 | pygame", True, (100, 100, 100))
        self.screen.blit(credit, (cfg.SCREEN_WIDTH // 2 - credit.get_width() // 2, 620))

    def draw_game_over(self, player, final_score, boss_defeated=False):
        overlay = pygame.Surface((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        if boss_defeated:
            title = self.font_huge.render("VICTORY!", True, (255, 220, 50))
            sub = self.font_large.render(f"Mole King Defeated!", True, (255, 180, 50))
        else:
            title = self.font_huge.render("GAME OVER", True, (220, 60, 60))
            sub = self.font_med.render("The gopher fainted...", True, (200, 150, 150))

        self.screen.blit(title, (cfg.SCREEN_WIDTH // 2 - title.get_width() // 2, 150))
        self.screen.blit(sub, (cfg.SCREEN_WIDTH // 2 - sub.get_width() // 2, 220))

        score_text = self.font_large.render(f"Score: {final_score}", True, (255, 255, 255))
        self.screen.blit(score_text, (cfg.SCREEN_WIDTH // 2 - score_text.get_width() // 2, 300))

        restart = self.font_med.render("Press R to Restart   |   M for Menu", True, (200, 200, 200))
        self.screen.blit(restart, (cfg.SCREEN_WIDTH // 2 - restart.get_width() // 2, 380))

    def draw_level_complete(self, player, level_num):
        overlay = pygame.Surface((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        title = self.font_huge.render("LEVEL COMPLETE!", True, (100, 255, 100))
        self.screen.blit(title, (cfg.SCREEN_WIDTH // 2 - title.get_width() // 2, 150))

        lvl_text = self.font_large.render(f"Level {level_num} Cleared!", True, (255, 255, 255))
        self.screen.blit(lvl_text, (cfg.SCREEN_WIDTH // 2 - lvl_text.get_width() // 2, 220))

        score_text = self.font_med.render(f"Score: {player.score}   HP: {int(player.hp)}/{player.max_hp}", True, (255, 230, 150))
        self.screen.blit(score_text, (cfg.SCREEN_WIDTH // 2 - score_text.get_width() // 2, 280))

        if player.fossils >= 3:
            bonus = self.font_med.render(f"Fossil Bonus! +200", True, (200, 180, 100))
            self.screen.blit(bonus, (cfg.SCREEN_WIDTH // 2 - bonus.get_width() // 2, 310))

        hint = self.font_med.render("Press SPACE for Next Level", True, (200, 200, 200))
        self.screen.blit(hint, (cfg.SCREEN_WIDTH // 2 - hint.get_width() // 2, 380))

    def draw_boss_intro(self, boss_name):
        overlay = pygame.Surface((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((30, 10, 10))
        self.screen.blit(overlay, (0, 0))

        warning = self.font_huge.render("WARNING!", True, (255, 50, 50))
        self.screen.blit(warning, (cfg.SCREEN_WIDTH // 2 - warning.get_width() // 2, 200))

        boss_text = self.font_large.render(boss_name, True, (255, 200, 50))
        self.screen.blit(boss_text, (cfg.SCREEN_WIDTH // 2 - boss_text.get_width() // 2, 280))

        hint = self.font_med.render("Get ready...", True, (200, 200, 200))
        self.screen.blit(hint, (cfg.SCREEN_WIDTH // 2 - hint.get_width() // 2, 360))

    def draw_floating_texts(self):
        for ft in self.floating_texts:
            alpha = max(0, int(255 * ft["timer"] / ft["duration"]))
            color = ft["color"]
            surf = self.font_med.render(ft["text"], True, color)
            s = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            s.blit(surf, (0, 0))
            s.set_alpha(alpha)
            self.screen.blit(s, (ft["x"] - s.get_width() // 2, ft["y"]))
