import random
import math
import config as cfg
import items as itm
from grid import Enemy


class Player:
    def __init__(self):
        self.col = cfg.PLAYER_START_COL
        self.row = cfg.PLAYER_START_ROW
        self.hp = cfg.PLAYER_START_HP
        self.max_hp = cfg.PLAYER_MAX_HP
        self.score = 0
        self.attack = cfg.PLAYER_START_ATTACK
        self.inventory = [None] * cfg.INVENTORY_SIZE
        self.shield = 0
        self.drill_boost = 0
        self.invincible = 0.0
        self.combo = 0
        self.frozen = 0.0
        self.poison = 0
        self.fossils = 0
        self.has_key = False
        self.alive = True
        self.facing = "down"
        self.anim_timer = 0.0
        self.flash_timer = 0.0

    def move(self, direction, grid):
        dc, dr = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}[direction]
        self.facing = direction
        new_col = self.col + dc
        new_row = self.row + dr

        result = {"moved": False, "combat": False, "item": None, "blocked": False,
                  "dug": False, "damage": 0, "score": 0, "enemy_killed": None,
                  "bomb_triggered": False, "push": 0, "stun": 0,
                  "teleport": False, "chest": False, "secret_room": False,
                  "collectible": None, "inventory_item": None, "nest_destroyed": False}

        if not (0 <= new_col < grid.cols and 0 <= new_row < grid.rows):
            return result

        cell = grid.cells[new_row][new_col]

        if cell.content == itm.ItemType.ROCK and not cell.dug:
            if self.drill_boost <= 0:
                result["blocked"] = True
                return result

        enemy = None
        for e in grid.enemies:
            if e.col == new_col and e.row == new_row and e.hp > 0:
                enemy = e
                break
        if grid.boss and grid.boss.col == new_col and grid.boss.row == new_row and grid.boss.hp > 0:
            enemy = grid.boss

        if enemy:
            return self._attack_enemy(enemy, grid, result)
        else:
            return self._move_to_cell(new_col, new_row, cell, grid, result, direction)

    def _attack_enemy(self, enemy, grid, result):
        result["combat"] = True
        stats = itm.ENEMY_STATS.get(enemy.type, {})
        armor = stats.get("armor", 0)
        effective_damage = max(1, int(self.attack * (1 - armor)))

        enemy.hp -= effective_damage
        result["moved"] = True

        if enemy.hp <= 0:
            result["enemy_killed"] = enemy
            result["score"] = stats.get("score", 0)
            if enemy == grid.boss:
                grid.boss_active = False
                grid.boss_defeated = True
                grid.boss = None
            else:
                grid.enemies.remove(enemy)
        else:
            enemy_damage = stats.get("damage", 0.5)
            if self._take_damage(enemy_damage):
                result["damage"] = enemy_damage
            if stats.get("poison"):
                self.poison = stats["poison"]
            if stats.get("web"):
                self.frozen = 1.0

        return result

    def _move_to_cell(self, new_col, new_row, cell, grid, result, direction):
        self.col = new_col
        self.row = new_row
        result["moved"] = True

        if not cell.dug:
            result["dug"] = True
            cell.dug = True
            content = cell.content
            cell.content = itm.ItemType.EMPTY

            if content == itm.ItemType.EMPTY:
                self.combo = 0
            elif content in itm.ITEM_INFO:
                info = itm.ITEM_INFO[content]
                result["item"] = content

                if info.get("instant", True):
                    self._apply_instant(content, info, result, grid)
                else:
                    self._add_to_inventory(content, result)
            elif itm.is_enemy_type(content):
                enemy = Enemy(content, new_col, new_row)
                grid.enemies.append(enemy)
                result["item"] = content
                self.combo = 0
        elif self.drill_boost > 0:
            self.drill_boost -= 1

        return result

    def _apply_instant(self, content, info, result, grid):
        if info.get("heal"):
            self.hp = min(self.max_hp, self.hp + info["heal"])
            self.combo = 0
        elif info.get("damage"):
            if self._take_damage(info["damage"]):
                result["damage"] = info["damage"]
            self.combo = 0
        elif info.get("score"):
            multiplier = 1
            self.combo += 1
            for threshold, mult in sorted(cfg.COMBO_BONUS.items()):
                if self.combo >= threshold:
                    multiplier = max(multiplier, mult)
            result["score"] = info["score"] * multiplier
            self.score += result["score"]
        elif info.get("shield_turns"):
            self.shield = info["shield_turns"]
        elif info.get("drill_turns"):
            self.drill_boost = info["drill_turns"]
        elif info.get("reveal_radius"):
            r = info["reveal_radius"]
            for dc in range(-r, r + 1):
                for dr in range(-r, r + 1):
                    nc, nr = self.col + dc, self.row + dr
                    if 0 <= nc < grid.cols and 0 <= nr < grid.rows:
                        grid.cells[nr][nc].revealed = True
        elif info.get("has_key"):
            self.has_key = True
        elif info.get("blocked"):
            pass
        elif info.get("random"):
            effects = [
                ("heal", {"heal": 1}),
                ("damage", {"damage": 1}),
                ("score", {"score": 50}),
                ("teleport", {"teleport": True}),
                ("stun", {"stun": 2.0}),
            ]
            effect_name, effect_data = random.choice(effects)
            if effect_name == "teleport":
                result["teleport"] = True
            elif effect_name == "stun":
                result["stun"] = effect_data["stun"]
            elif effect_name == "heal":
                self.hp = min(self.max_hp, self.hp + effect_data["heal"])
            elif effect_name == "damage":
                if self._take_damage(effect_data["damage"]):
                    result["damage"] = effect_data["damage"]
            elif effect_name == "score":
                result["score"] = effect_data["score"]
                self.score += result["score"]
            self.combo = 0
        elif info.get("push"):
            result["push"] = info["push"]
            self.combo = 0
        elif info.get("stun"):
            result["stun"] = info["stun"]
            self.combo = 0
        elif info.get("teleport"):
            result["teleport"] = True
            self.combo = 0
        elif info.get("chest"):
            self._open_chest(result, grid)
        elif info.get("secret_room"):
            result["secret_room"] = True
            self._create_secret_room(grid)
        elif info.get("nest"):
            result["nest_destroyed"] = True
            result["score"] = 150
            self.score += 150
            self.combo = 0
        elif info.get("boss"):
            result["item"] = itm.ItemType.BOSS_LAIR

    def _take_damage(self, amount):
        if self.invincible > 0:
            return False
        if self.shield > 0:
            self.shield -= 1
            return False
        self.hp -= amount
        self.invincible = cfg.PLAYER_INVINCIBLE_TIME
        self.combo = 0
        self.flash_timer = 0.3
        if self.hp <= 0:
            self.alive = False
        return True

    def _add_to_inventory(self, content, result):
        for i in range(cfg.INVENTORY_SIZE):
            if self.inventory[i] is None:
                self.inventory[i] = content
                result["inventory_item"] = content
                return
        result["inventory_full"] = True

    def use_item(self, slot, grid):
        if slot < 0 or slot >= cfg.INVENTORY_SIZE:
            return None
        item = self.inventory[slot]
        if item is None:
            return None
        self.inventory[slot] = None
        info = itm.ITEM_INFO.get(item, {})
        effect = info.get("use_effect")
        if effect:
            return {"type": effect}
        elif info.get("attack_bonus"):
            self.attack += info["attack_bonus"]
            return {"type": "attack_up", "amount": info["attack_bonus"]}
        return None

    def _open_chest(self, result, grid):
        possible = [itm.ItemType.GOLD, itm.ItemType.DIAMOND, itm.ItemType.BOMB,
                    itm.ItemType.FREEZE, itm.ItemType.FIRE_BREATH, itm.ItemType.IRON_CLAW,
                    itm.ItemType.SHIELD, itm.ItemType.CARROT]
        count = random.randint(1, 3)
        rewards = random.sample(possible, min(count, len(possible)))
        result["chest"] = True
        result["chest_items"] = []
        for content in rewards:
            info = itm.ITEM_INFO[content]
            if info.get("instant", True):
                self._apply_instant(content, info, result, grid)
            else:
                self._add_to_inventory(content, result)
            result["chest_items"].append(content)

    def _create_secret_room(self, grid):
        room_col = max(0, min(grid.cols - 4, self.col - 2))
        room_row = max(0, min(grid.rows - 3, self.row - 1))
        for dc in range(4):
            for dr in range(3):
                nc, nr = room_col + dc, room_row + dr
                if 0 <= nc < grid.cols and 0 <= nr < grid.rows:
                    cell = grid.cells[nr][nc]
                    cell.dug = True
                    cell.content = itm.ItemType.EMPTY
        for _ in range(6):
            rx = room_col + random.randint(0, 3)
            ry = room_row + random.randint(0, 2)
            if 0 <= rx < grid.cols and 0 <= ry < grid.rows:
                grid.cells[ry][rx].content = random.choice([
                    itm.ItemType.GOLD, itm.ItemType.GOLD, itm.ItemType.SILVER,
                    itm.ItemType.DIAMOND, itm.ItemType.CARROT,
                ])

    def update(self, dt):
        if self.invincible > 0:
            self.invincible -= dt
        if self.frozen > 0:
            self.frozen -= dt
        if self.flash_timer > 0:
            self.flash_timer -= dt
        if self.shield > 0:
            pass
        if self.drill_boost > 0:
            pass
        if self.poison > 0:
            self.poison -= dt
            if self.poison > 0 and int(self.poison * 10) % 20 == 0:
                self.hp -= 0.5
                if self.hp <= 0:
                    self.alive = False

    def get_x(self):
        return cfg.GRID_OFFSET_X + self.col * cfg.CELL_SIZE + cfg.CELL_SIZE // 2

    def get_y(self):
        return cfg.GRID_OFFSET_Y + self.row * cfg.CELL_SIZE + cfg.CELL_SIZE // 2
