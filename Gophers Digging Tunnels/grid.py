import random
from collections import deque
import config as cfg
import items as itm


class Cell:
    def __init__(self):
        self.dug = False
        self.content = itm.ItemType.EMPTY
        self.soil_type = "topsoil"
        self.revealed = False

    def get_soil_color(self):
        colors = cfg.SOIL_COLORS.get(self.soil_type, cfg.SOIL_COLORS["topsoil"])
        return colors["dug"] if self.dug else colors["undug"]


class Enemy:
    def __init__(self, enemy_type, col, row):
        self.type = enemy_type
        self.col = col
        self.row = row
        stats = itm.ENEMY_STATS.get(enemy_type, {})
        self.hp = stats.get("hp", 1)
        self.max_hp = self.hp
        self.state = "patrol"
        self.move_timer = 0.0
        self.move_interval = stats.get("speed", 1.0)
        self.patrol_dir = random.choice([-1, 1])
        self.frozen_timer = 0.0
        self.attack_timer = 0.0
        self.patrol_axis = "horizontal"


class Boss(Enemy):
    def __init__(self, enemy_type, col, row):
        super().__init__(enemy_type, col, row)
        self.phase = 1
        self.phase_hp_thresholds = [self.max_hp * 0.66, self.max_hp * 0.33]
        self.special_timer = 0.0

    def update_phase(self):
        if self.phase < 3 and self.hp <= self.phase_hp_thresholds[self.phase - 1]:
            self.phase += 1
            self.special_timer = 2.0
            return True
        return False


class Grid:
    def __init__(self):
        self.cols = cfg.GRID_COLS
        self.rows = cfg.GRID_ROWS
        self.cells = [[Cell() for _ in range(self.cols)] for _ in range(self.rows)]
        self.enemies = []
        self.boss = None
        self.boss_active = False
        self.nest_timers = []
        self.level_num = 1
        self.boss_defeated = False

    def generate(self, level_num):
        self.level_num = level_num
        self.cells = [[Cell() for _ in range(self.cols)] for _ in range(self.rows)]
        self.enemies = []
        self.boss = None
        self.boss_active = False
        self.boss_defeated = False
        self.nest_timers = []

        for row in range(self.rows):
            for col in range(self.cols):
                cell = self.cells[row][col]
                layer = itm.get_layer_for_row(row)
                cell.soil_type = layer
                dist = itm.LAYER_DISTRIBUTIONS.get(layer, itm.LAYER_DISTRIBUTIONS["topsoil"])
                cell.content = self._pick_content(dist)

        self.cells[0][self.cols // 2].content = itm.ItemType.EMPTY
        self.cells[0][self.cols // 2].dug = True

        self.cells[1][self.cols // 2].dug = True
        self.cells[1][self.cols // 2].content = itm.ItemType.EMPTY

        boss_col = self.cols // 2
        boss_row = self.rows - 1
        self.cells[boss_row][boss_col].soil_type = "bedrock"
        if level_num >= 3:
            self.cells[boss_row][boss_col].content = itm.ItemType.BOSS_LAIR
            for dc in [-1, 1]:
                nc = boss_col + dc
                if 0 <= nc < self.cols:
                    self.cells[boss_row][nc].content = itm.ItemType.EMPTY
                    self.cells[boss_row - 1][nc].content = itm.ItemType.EMPTY
        else:
            self.cells[boss_row][boss_col].content = itm.ItemType.DIAMOND
            self.cells[boss_row][boss_col - 1].content = itm.ItemType.GOLD
            self.cells[boss_row][boss_col + 1].content = itm.ItemType.GOLD

        enemy_density = {1: 0.3, 2: 0.5, 3: 0.8, 4: 1.0, 5: 1.5, 6: 2.0}
        density = enemy_density.get(level_num, 1.0)
        for row in range(2, self.rows - 2):
            for col in range(self.cols):
                if self.cells[row][col].content == itm.ItemType.EMPTY:
                    if random.random() < 0.04 * density:
                        enemy_type = self._pick_enemy_for_layer(
                            itm.get_layer_for_row(row), level_num)
                        if enemy_type:
                            self.cells[row][col].content = enemy_type

        for row in range(3, self.rows - 3):
            for col in range(self.cols):
                if self.cells[row][col].content == itm.ItemType.EMPTY:
                    if random.random() < 0.01 * density:
                        self.cells[row][col].content = itm.ItemType.NEST

    def _pick_content(self, dist):
        total = sum(dist.values())
        r = random.randint(1, total)
        cumulative = 0
        for content, weight in dist.items():
            cumulative += weight
            if r <= cumulative:
                if content == "empty":
                    return itm.ItemType.EMPTY
                return content
        return itm.ItemType.EMPTY

    def _pick_enemy_for_layer(self, layer, level):
        if layer == "surface":
            return None
        elif layer == "topsoil":
            pool = [itm.EnemyType.ANT]
            if level >= 2:
                pool.extend([itm.EnemyType.BEETLE])
            if level >= 3:
                pool.extend([itm.EnemyType.MOLE_BANDIT])
            return random.choice(pool)
        elif layer == "deep_soil":
            pool = [itm.EnemyType.ANT, itm.EnemyType.BEETLE, itm.EnemyType.SPIDER]
            if level >= 2:
                pool.extend([itm.EnemyType.MOLE_BANDIT])
            if level >= 4:
                pool.extend([itm.EnemyType.SCORPION])
            return random.choice(pool)
        elif layer == "stone":
            pool = [itm.EnemyType.BEETLE, itm.EnemyType.SPIDER, itm.EnemyType.SCORPION]
            if level >= 5:
                pool.extend([itm.EnemyType.GIANT_WORM])
            return random.choice(pool)
        else:
            pool = [itm.EnemyType.SPIDER, itm.EnemyType.SCORPION, itm.EnemyType.GIANT_WORM]
            return random.choice(pool)

    def activate_boss_lair(self, col, row):
        if self.boss_active:
            return False
        boss_type = itm.EnemyType.MOLE_KING if self.level_num >= 5 else itm.EnemyType.GIANT_WORM
        self.boss = Boss(boss_type, col, row)
        self.boss_active = True
        for dc in [-1, 0, 1]:
            for dr in [-1, 0, 1]:
                nc, nr = col + dc, row + dr
                if 0 <= nc < self.cols and 0 <= nr < self.rows:
                    self.cells[nr][nc].dug = True
        return True

    def update_enemies(self, dt, player_col, player_row, particles):
        for e in self.enemies[:]:
            if e.frozen_timer > 0:
                e.frozen_timer -= dt
                continue
            e.move_timer += dt
            if e.move_timer >= e.move_interval:
                e.move_timer = 0.0
                self._enemy_ai(e, player_col, player_row, particles)

        if self.boss and self.boss_active and self.boss.hp > 0:
            if self.boss.frozen_timer > 0:
                self.boss.frozen_timer -= dt
            else:
                self.boss.move_timer += dt
                interval = self.boss.move_interval * (0.7 if self.boss.phase >= 2 else 1.0)
                if self.boss.move_timer >= interval:
                    self.boss.move_timer = 0.0
                    self._boss_ai(self.boss, player_col, player_row, particles)

    def _enemy_ai(self, enemy, player_col, player_row, particles):
        dist = abs(enemy.col - player_col) + abs(enemy.row - player_row)
        stats = itm.ENEMY_STATS.get(enemy.type, {})

        if dist <= 1:
            enemy.state = "attack"
            return
        elif dist <= cfg.ENEMY_DETECT_RANGE:
            enemy.state = "chase"
        else:
            enemy.state = "patrol"

        if enemy.state == "chase":
            self._move_toward(enemy, player_col, player_row)
        elif enemy.state == "patrol":
            self._patrol_move(enemy)

    def _boss_ai(self, boss, player_col, player_row, particles):
        changed = boss.update_phase()
        if changed:
            bx = cfg.GRID_OFFSET_X + boss.col * cfg.CELL_SIZE + cfg.CELL_SIZE // 2
            by = cfg.GRID_OFFSET_Y + boss.row * cfg.CELL_SIZE + cfg.CELL_SIZE // 2
            particles.emit_boss(bx, by)

        dist = abs(boss.col - player_col) + abs(boss.row - player_row)

        if boss.phase == 1:
            if dist <= 1:
                return
            self._move_toward(boss, player_col, player_row)
        elif boss.phase == 2:
            if dist <= 1:
                return
            if boss.special_timer <= 0 and dist <= 3:
                self._move_toward(boss, player_col, player_row)
            else:
                boss.special_timer -= 0.3
        else:
            if dist <= 1:
                return
            if random.random() < 0.5:
                self._move_toward(boss, player_col, player_row)
            else:
                self._patrol_move(boss)

    def _move_toward(self, enemy, target_col, target_row):
        dc = target_col - enemy.col
        dr = target_row - enemy.row
        if abs(dc) >= abs(dr):
            ndc = 1 if dc > 0 else -1
            if self._can_move_to(enemy.col + ndc, enemy.row):
                enemy.col += ndc
                return
            ndr = 1 if dr > 0 else -1
            if self._can_move_to(enemy.col, enemy.row + ndr):
                enemy.row += ndr
                return
        else:
            ndr = 1 if dr > 0 else -1
            if self._can_move_to(enemy.col, enemy.row + ndr):
                enemy.row += ndr
                return
            ndc = 1 if dc > 0 else -1
            if self._can_move_to(enemy.col + ndc, enemy.row):
                enemy.col += ndc

    def _patrol_move(self, enemy):
        if enemy.patrol_axis == "horizontal":
            nc = enemy.col + enemy.patrol_dir
            if self._can_move_to(nc, enemy.row):
                enemy.col = nc
            else:
                enemy.patrol_dir *= -1
                enemy.patrol_axis = "vertical"
        else:
            nr = enemy.row + enemy.patrol_dir
            if self._can_move_to(enemy.col, nr):
                enemy.row = nr
            else:
                enemy.patrol_dir *= -1
                enemy.patrol_axis = "horizontal"

    def _can_move_to(self, col, row):
        if not (0 <= col < self.cols and 0 <= row < self.rows):
            return False
        cell = self.cells[row][col]
        if not cell.dug:
            return False
        if cell.content == itm.ItemType.ROCK:
            return False
        for e in self.enemies:
            if e.col == col and e.row == row and e.hp > 0:
                return False
        if self.boss and self.boss.col == col and self.boss.row == row:
            return False
        return True

    def update_nests(self, dt):
        for row in range(self.rows):
            for col in range(self.cols):
                cell = self.cells[row][col]
                if cell.content == itm.ItemType.NEST and cell.dug:
                    if not hasattr(cell, 'nest_spawn_timer'):
                        cell.nest_spawn_timer = 0.0
                    cell.nest_spawn_timer += dt
                    if cell.nest_spawn_timer >= cfg.NEST_SPAWN_INTERVAL:
                        cell.nest_spawn_timer = 0.0
                        layer = itm.get_layer_for_row(row)
                        enemy_type = self._pick_enemy_for_layer(layer, self.level_num)
                        if enemy_type:
                            spawn_col, spawn_row = self._find_spawn_pos(col, row)
                            if spawn_col is not None:
                                self.enemies.append(Enemy(enemy_type, spawn_col, spawn_row))

    def _find_spawn_pos(self, nest_col, nest_row):
        positions = []
        for dc in range(-2, 3):
            for dr in range(-2, 3):
                nc, nr = nest_col + dc, nest_row + dr
                if (nc, nr) == (nest_col, nest_row):
                    continue
                if self._can_move_to(nc, nr) and abs(dc) + abs(dr) <= 2:
                    positions.append((nc, nr))
        if positions:
            return random.choice(positions)
        return None, None

    def find_path(self, start_col, start_row, end_col, end_row):
        queue = deque([(start_col, start_row)])
        visited = {(start_col, start_row): None}
        while queue:
            col, row = queue.popleft()
            if (col, row) == (end_col, end_row):
                path = []
                cur = (end_col, end_row)
                while cur != (start_col, start_row):
                    path.append(cur)
                    cur = visited[cur]
                path.reverse()
                return path
            for dc, dr in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nc, nr = col + dc, row + dr
                if (nc, nr) not in visited and self._can_move_to(nc, nr):
                    visited[(nc, nr)] = (col, row)
                    queue.append((nc, nr))
        return None

    def can_reach_bottom(self, start_col, start_row):
        for row in range(self.rows - 1, -1, -1):
            for col in range(self.cols):
                if self.cells[row][col].dug:
                    path = self.find_path(start_col, start_row, col, row)
                    if path is not None:
                        return True, col, row
        return False, None, None

    def get_neighbor_items(self, col, row):
        neighbors = []
        for dc, dr in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nc, nr = col + dc, row + dr
            if 0 <= nc < self.cols and 0 <= nr < self.rows:
                cell = self.cells[nr][nc]
                if not cell.dug:
                    neighbors.append((nc, nr, cell.content))
        return neighbors
