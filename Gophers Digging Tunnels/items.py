class ItemType:
    EMPTY = "empty"
    COPPER = "copper"
    SILVER = "silver"
    GOLD = "gold"
    DIAMOND = "diamond"
    FOSSIL = "fossil"
    STONE_TOOTH = "stone_tooth"
    IRON_CLAW = "iron_claw"
    BOMB = "bomb"
    FREEZE = "freeze"
    FIRE_BREATH = "fire_breath"
    CARROT = "carrot"
    SHIELD = "shield"
    DRILL = "drill"
    MAP = "map"
    KEY = "key"
    SPIKE = "spike"
    ROCK = "rock"
    MUSHROOM = "mushroom"
    WATER = "water"
    TRAP = "trap"
    PORTAL = "portal"
    CHEST = "chest"
    SECRET_ROOM = "secret_room"
    NEST = "nest"
    BOSS_LAIR = "boss_lair"


class EnemyType:
    ANT = "ant"
    BEETLE = "beetle"
    SPIDER = "spider"
    MOLE_BANDIT = "mole_bandit"
    SCORPION = "scorpion"
    GIANT_WORM = "giant_worm"
    MOLE_KING = "mole_king"


ITEM_INFO = {
    ItemType.COPPER: {"name": "Copper", "score": 10, "color": (205, 155, 50),
                      "icon": "C", "instant": True, "rarity": "common"},
    ItemType.SILVER: {"name": "Silver", "score": 30, "color": (192, 192, 210),
                      "icon": "S", "instant": True, "rarity": "uncommon"},
    ItemType.GOLD: {"name": "Gold", "score": 100, "color": (255, 200, 50),
                    "icon": "G", "instant": True, "rarity": "rare"},
    ItemType.DIAMOND: {"name": "Diamond", "score": 300, "color": (180, 220, 255),
                       "icon": "D", "instant": True, "rarity": "epic"},
    ItemType.FOSSIL: {"name": "Fossil", "score": 50, "color": (220, 200, 170),
                      "icon": "F", "instant": True, "rarity": "rare"},

    ItemType.STONE_TOOTH: {"name": "Stone Tooth", "score": 0, "color": (180, 180, 180),
                           "icon": "T", "instant": False, "rarity": "uncommon", "attack_bonus": 1},
    ItemType.IRON_CLAW: {"name": "Iron Claw", "score": 0, "color": (100, 100, 120),
                         "icon": "C", "instant": False, "rarity": "rare", "attack_bonus": 2},
    ItemType.BOMB: {"name": "Bomb", "score": 0, "color": (255, 80, 50),
                    "icon": "B", "instant": False, "rarity": "rare", "use_effect": "bomb"},
    ItemType.FREEZE: {"name": "Freeze Potion", "score": 0, "color": (100, 200, 255),
                      "icon": "F", "instant": False, "rarity": "rare", "use_effect": "freeze"},
    ItemType.FIRE_BREATH: {"name": "Fire Breath", "score": 0, "color": (255, 120, 30),
                           "icon": "F", "instant": False, "rarity": "epic", "use_effect": "fire"},

    ItemType.CARROT: {"name": "Carrot", "score": 0, "color": (255, 150, 50),
                      "icon": "H", "instant": True, "rarity": "uncommon", "heal": 1},
    ItemType.SHIELD: {"name": "Shield", "score": 0, "color": (100, 150, 255),
                      "icon": "S", "instant": True, "rarity": "uncommon", "shield_turns": 5},
    ItemType.DRILL: {"name": "Drill Boost", "score": 0, "color": (200, 180, 100),
                     "icon": "D", "instant": True, "rarity": "uncommon", "drill_turns": 5},
    ItemType.MAP: {"name": "Map", "score": 0, "color": (200, 180, 140),
                   "icon": "M", "instant": True, "rarity": "rare", "reveal_radius": 2},
    ItemType.KEY: {"name": "Key", "score": 0, "color": (255, 220, 80),
                   "icon": "K", "instant": True, "rarity": "uncommon", "has_key": True},

    ItemType.SPIKE: {"name": "Spike Trap", "score": 0, "color": (200, 50, 50),
                     "icon": "X", "instant": True, "rarity": "trap", "damage": 1},
    ItemType.ROCK: {"name": "Rock", "score": 0, "color": (150, 140, 130),
                    "icon": "R", "instant": True, "rarity": "obstacle", "blocked": True},
    ItemType.MUSHROOM: {"name": "Mushroom", "score": 0, "color": (200, 50, 200),
                        "icon": "?", "instant": True, "rarity": "trap", "random": True},
    ItemType.WATER: {"name": "Underground Water", "score": 0, "color": (50, 150, 220),
                     "icon": "~", "instant": True, "rarity": "trap", "push": 2},
    ItemType.TRAP: {"name": "Mouse Trap", "score": 0, "color": (180, 130, 90),
                    "icon": "T", "instant": True, "rarity": "trap", "stun": 2.0},

    ItemType.PORTAL: {"name": "Portal", "score": 0, "color": (150, 50, 220),
                      "icon": "@", "instant": True, "rarity": "special", "teleport": True},
    ItemType.CHEST: {"name": "Treasure Chest", "score": 0, "color": (180, 140, 60),
                     "icon": "C", "instant": True, "rarity": "special", "chest": True},
    ItemType.SECRET_ROOM: {"name": "Secret Room", "score": 0, "color": (255, 230, 100),
                           "icon": "!", "instant": True, "rarity": "special", "secret_room": True},
    ItemType.NEST: {"name": "Enemy Nest", "score": 0, "color": (120, 60, 60),
                    "icon": "N", "instant": True, "rarity": "special", "nest": True},
    ItemType.BOSS_LAIR: {"name": "Boss Lair", "score": 0, "color": (180, 30, 30),
                         "icon": "B", "instant": True, "rarity": "special", "boss": True},
}

ENEMY_STATS = {
    EnemyType.ANT: {"name": "Ant Soldier", "hp": 1, "damage": 0.5, "color": (50, 50, 50),
                    "radius": 10, "speed": 0.6, "score": 20, "shape": "ellipse"},
    EnemyType.BEETLE: {"name": "Beetle Warrior", "hp": 3, "damage": 1, "color": (139, 90, 43),
                       "radius": 12, "speed": 1.2, "score": 50, "armor": 0.5, "shape": "hexagon"},
    EnemyType.SPIDER: {"name": "Cave Spider", "hp": 2, "damage": 1, "color": (80, 20, 80),
                       "radius": 11, "speed": 0.9, "score": 40, "web": True, "shape": "star"},
    EnemyType.MOLE_BANDIT: {"name": "Mole Bandit", "hp": 2, "damage": 0.5, "color": (160, 120, 70),
                            "radius": 10, "speed": 0.5, "score": 60, "steals": 20, "shape": "triangle"},
    EnemyType.SCORPION: {"name": "Scorpion", "hp": 3, "damage": 1.5, "color": (200, 100, 50),
                         "radius": 11, "speed": 1.0, "score": 70, "poison": 3, "shape": "diamond"},
    EnemyType.GIANT_WORM: {"name": "Giant Worm", "hp": 8, "damage": 2, "color": (180, 140, 160),
                           "radius": 14, "speed": 1.5, "score": 200, "shape": "big_circle"},
    EnemyType.MOLE_KING: {"name": "Mole King", "hp": 20, "damage": 3, "color": (180, 50, 50),
                          "radius": 15, "speed": 0.8, "score": 1000, "boss": True, "shape": "crown"},
}

LAYER_DISTRIBUTIONS = {
    "surface": {
        "empty": 80,
        ItemType.COPPER: 10,
        ItemType.CARROT: 10,
    },
    "topsoil": {
        "empty": 50,
        ItemType.COPPER: 15,
        ItemType.SILVER: 8,
        ItemType.CARROT: 5,
        ItemType.SPIKE: 5,
        ItemType.SHIELD: 3,
        ItemType.STONE_TOOTH: 3,
        EnemyType.ANT: 4,
        ItemType.KEY: 3,
        ItemType.MUSHROOM: 2,
        ItemType.TRAP: 2,
    },
    "deep_soil": {
        "empty": 35,
        ItemType.COPPER: 10,
        ItemType.SILVER: 8,
        ItemType.GOLD: 5,
        ItemType.CARROT: 4,
        ItemType.SPIKE: 5,
        ItemType.SHIELD: 3,
        ItemType.STONE_TOOTH: 3,
        ItemType.IRON_CLAW: 3,
        EnemyType.ANT: 3,
        EnemyType.BEETLE: 3,
        EnemyType.SPIDER: 3,
        ItemType.BOMB: 2,
        ItemType.FOSSIL: 2,
        ItemType.MUSHROOM: 2,
        ItemType.DRILL: 2,
        ItemType.MAP: 2,
        ItemType.WATER: 1,
        EnemyType.MOLE_BANDIT: 1,
    },
    "stone": {
        "empty": 25,
        ItemType.SILVER: 5,
        ItemType.GOLD: 6,
        ItemType.DIAMOND: 3,
        ItemType.SPIKE: 5,
        ItemType.ROCK: 8,
        ItemType.CARROT: 3,
        ItemType.SHIELD: 3,
        ItemType.IRON_CLAW: 4,
        ItemType.BOMB: 3,
        ItemType.FREEZE: 3,
        ItemType.FIRE_BREATH: 2,
        EnemyType.BEETLE: 4,
        EnemyType.SPIDER: 4,
        EnemyType.SCORPION: 3,
        EnemyType.MOLE_BANDIT: 3,
        ItemType.FOSSIL: 3,
        ItemType.WATER: 2,
        ItemType.TRAP: 2,
        ItemType.MUSHROOM: 1,
        ItemType.PORTAL: 2,
        ItemType.CHEST: 2,
        ItemType.NEST: 2,
        ItemType.DRILL: 1,
        ItemType.MAP: 1,
    },
    "bedrock": {
        "empty": 15,
        ItemType.GOLD: 6,
        ItemType.DIAMOND: 5,
        ItemType.SPIKE: 3,
        ItemType.ROCK: 8,
        ItemType.IRON_CLAW: 5,
        ItemType.BOMB: 5,
        ItemType.FREEZE: 4,
        ItemType.FIRE_BREATH: 3,
        EnemyType.SCORPION: 6,
        EnemyType.GIANT_WORM: 6,
        EnemyType.MOLE_BANDIT: 4,
        ItemType.NEST: 5,
        ItemType.CHEST: 5,
        ItemType.FOSSIL: 4,
        ItemType.PORTAL: 3,
        ItemType.CARROT: 3,
        ItemType.SHIELD: 3,
        ItemType.SECRET_ROOM: 2,
    },
}


def get_layer_for_row(row):
    if row <= 1:
        return "surface"
    elif row <= 6:
        return "topsoil"
    elif row <= 12:
        return "deep_soil"
    elif row <= 17:
        return "stone"
    else:
        return "bedrock"


def is_enemy_type(content):
    return content in [
        EnemyType.ANT, EnemyType.BEETLE, EnemyType.SPIDER,
        EnemyType.MOLE_BANDIT, EnemyType.SCORPION,
        EnemyType.GIANT_WORM, EnemyType.MOLE_KING,
    ]


def is_item_type(content):
    return content in ITEM_INFO and not is_enemy_type(content)
