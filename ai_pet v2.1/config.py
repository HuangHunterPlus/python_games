import os
import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
    MEIPASS = Path(getattr(sys, '_MEIPASS', BASE_DIR))
else:
    BASE_DIR = Path(__file__).parent
    MEIPASS = BASE_DIR

SRC_DIR = Path(__file__).parent
MEIPASS_DIR = MEIPASS / "brain_models" / "data"
DATA_DIR = BASE_DIR / "brain_models" / "data"


def bundled_path(filename: str) -> Path:
    p = DATA_DIR / filename
    if p.exists():
        return p
    return MEIPASS_DIR / filename

os.makedirs(DATA_DIR, exist_ok=True)

# Pet identity
PET_NAME = "小咪"
PET_SPECIES = "cat"

# Status attributes (0-100)
INITIAL_HUNGER = 30
INITIAL_ENERGY = 70
INITIAL_MOOD = 60
INITIAL_HEALTH = 80

# Decay rates per second
HUNGER_DECAY = 0.02 / 60
ENERGY_DECAY = 0.015 / 60
MOOD_DECAY = 0.01 / 60
HEALTH_DECAY = 0.005 / 60

# Interaction effects
PET_FEED_HUNGER = -20
PET_PET_MOOD = 15
PET_PET_AFFECTION = 0.02
PET_PET_CLINGY = 0.01
PET_PLAY_ENERGY = -15
PET_PLAY_MOOD = 20
PET_PLAY_ACTIVE = 0.02
PET_PLAY_CURIOUS = 0.01
PET_HEAL_HEALTH = 25
PET_SCOLD_MOOD = -10
PET_SCOLD_AFFECTION = -0.03
PET_SCOLD_STUBBORN = 0.02

# New interaction effects
PET_BATHE_MOOD = 10
PET_BATHE_HEALTH = 5
PET_GIFT_MOOD = 15
PET_GIFT_AFFECTION = 0.02
PET_PRAISE_MOOD = 12
PET_PRAISE_AFFECTION = 0.02
PET_STORY_MOOD = 10
PET_STORY_ENERGY = -5
PET_TEACH_MOOD = 8
PET_TEACH_ENERGY = -10
PET_TEACH_CURIOUS = 0.02
PET_DANCE_ENERGY = -5
PET_DANCE_MOOD = 15

# Q-Learning
STATES_DIM = [3, 3, 3, 3, 3]
ACTIONS = ["sleep", "play", "explore", "cuddle", "eat", "wander", "groom"]
LEARNING_RATE = 0.1
DISCOUNT_FACTOR = 0.9
EXPLORATION_RATE = 0.2
EXPLORATION_DECAY = 0.9995
MIN_EXPLORATION = 0.05

# Personality
PERSONALITY_DIMS = ["affectionate", "energetic", "curious", "stubborn", "clingy"]
INITIAL_PERSONALITY = [0.6, 0.5, 0.7, 0.3, 0.4]
PERSONALITY_CHANGE_RATE = 0.001
PERSONALITY_MAX_DAILY = 0.1

# Memory
MEMORY_HALF_LIFE_DAYS = 7
MEMORY_CLEAN_THRESHOLD = 0.05
MEMORY_MIN_COUNT = 3

# Char-RNN
VOCAB = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ .,!?-'\":;()0123456789\n"
VOCAB_SIZE = len(VOCAB)
EMBED_DIM = 16
HIDDEN_DIM = 64
RNN_TEMPERATURE = 0.8
RNN_TRAIN_EPOCHS = 60
RNN_LEARNING_RATE = 0.01

# Dialogue
EMOTIONS = ["happy", "sad", "hungry", "sleepy", "playful", "curious", "grateful", "loving", "excited", "cuddly"]
TEMPLATE_PROB = 0.8

# Rendering
PET_SIZE = 128
WINDOW_WIDTH = 200
WINDOW_HEIGHT = 280
FPS = 30
SCALE = 1.2

# Animation
ANIMATION_FRAMES = {
    "idle": 2,
    "happy": 3,
    "sad": 2,
    "playful": 3,
    "hungry": 2,
    "sleepy": 2,
    "sick": 2,
    "curious": 2,
    "excited": 3,
    "cuddly": 2,
    "dance": 3,
}

# Animal shop
ANIMAL_CONFIGS = {
    "cat": {"name": "橘猫", "body": (255, 159, 67), "ear": (255, 138, 128),
            "belly": (255, 243, 224), "nose": (255, 107, 107), "whisker": (99, 110, 114)},
    "dog": {"name": "柴犬", "body": (220, 180, 140), "ear": (200, 160, 120),
            "belly": (250, 235, 210), "nose": (60, 60, 60), "whisker": (140, 130, 120)},
    "rabbit": {"name": "白兔", "body": (245, 240, 235), "ear": (255, 200, 210),
               "belly": (255, 250, 248), "nose": (255, 150, 180), "whisker": (180, 170, 170)},
    "hamster": {"name": "仓鼠", "body": (235, 195, 140), "ear": (245, 200, 170),
                "belly": (255, 235, 210), "nose": (255, 150, 150), "whisker": (160, 150, 140)},
    "fox": {"name": "赤狐", "body": (255, 130, 50), "ear": (255, 200, 150),
            "belly": (255, 245, 235), "nose": (50, 50, 50), "whisker": (140, 130, 120)},
}

SHOP_ITEMS = [
    ("cat", "橘猫", 0, "默认宠物，友好的橘色小猫"),
    ("dog", "柴犬", 100, "活泼忠诚的柴犬"),
    ("rabbit", "白兔", 150, "温顺可爱的白兔"),
    ("hamster", "仓鼠", 200, "圆滚滚的黄金仓鼠"),
    ("fox", "赤狐", 300, "机灵优雅的赤狐"),
]

COIN_REWARDS = {
    "greet": 1, "pet": 2, "feed": 3, "play": 3, "heal": 2,
    "bathe": 3, "praise": 2, "story": 2, "teach": 3, "dance": 3,
    "scold": 0, "status": 0, "gift": 0,
}
GIFT_COST = 5

# Window
WINDOW_FLAGS = {
    "frameless": True,
    "topmost": True,
    "transparent": True,
    "skip_taskbar": True,
    "show_without_activating": True,
}
