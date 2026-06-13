"""
Configuration — all tunable parameters in one place.
Pixel values are computed from background image size in init().
"""


# ── Asset paths ──
BACKGROUND_PATH = "image/bg.png"
PADDLE_IMAGE_PATH = "image/pat.png"

# ── Reference resolution (used to scale pixel values) ──
REF_WIDTH = 1054
REF_HEIGHT = 1492

# ── Window (set by init()) ──
WINDOW_WIDTH: int = 0
WINDOW_HEIGHT: int = 0
FPS = 60
TITLE = "🏓 Top-Down Ping Pong"

# ── Window scale (1.0 = full image size, 0.5 = half size) ──
SCREEN_SCALE = 0.5

# ── Table area (computed from ratios in init()) ──
TABLE_LEFT: int = 0
TABLE_RIGHT: int = 0
TABLE_TOP: int = 0
TABLE_BOTTOM: int = 0
TABLE_CENTER_X: int = 0
TABLE_WIDTH: int = 0
NET_Y: int = 0
NET_COLOR = (200, 200, 200, 180)

# ── Table ratios (fraction of window width/height, 0.0–1.0) ──
_TABLE_LEFT_RATIO = 0.12
_TABLE_RIGHT_RATIO = 0.88
_TABLE_TOP_RATIO = 0.06
_TABLE_BOTTOM_RATIO = 0.94
_NET_Y_RATIO = 0.50

# ── Ball ──
BALL_RADIUS: int = 0
BALL_BASE_SPEED: float = 0
BALL_MAX_SPEED: float = 0
BALL_ACCEL = 1.03
BALL_COLOR = (255, 230, 50)
BOUNCE_HEIGHT: int = 0
BOUNCE_CYCLE_DISTANCE: int = 0
LANDING_DIST: int = 0
OWN_BOUNCE_DIST: int = 0
LANDING_BOUNCE_DURATION = 0.45
LANDING_BOUNCE_MULTIPLIER = 3.2

# ── Particles ──
PARTICLE_HIT_COUNT = 12
PARTICLE_SCORE_COUNT = 30
PARTICLE_LIFETIME = 0.6

# ── Paddle (auto-tracks ball; no manual movement) ──
PADDLE_WIDTH: int = 0
PADDLE_HEIGHT: int = 0
PADDLE_TRACK_SPEED = 0.15
HIT_COOLDOWN = 0.2
HIT_ZONE_HEIGHT: int = 0

PADDLE1_COLOR = (78, 205, 196)
PADDLE2_COLOR = (255, 107, 107)
PADDLE1_INIT_X: int = 0
PADDLE1_INIT_Y: int = 0
PADDLE2_INIT_X: int = 0
PADDLE2_INIT_Y: int = 0
# Paddle movement bounds (also used during auto-track)
PADDLE1_BOUNDS: dict = {}
PADDLE2_BOUNDS: dict = {}

# ── Game rules ──
WIN_SCORE = 11
SERVER_CHANGE = 2
COUNTDOWN_SECONDS = 2
SCORE_PAUSE_SECONDS = 1.5

# ── Colors ──
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
SHADOW_COLOR = (0, 0, 0)
HUD_BG = (0, 0, 0, 100)

# ── Fonts ──
FONT_NAME = None
FONT_SMALL = 20
FONT_MEDIUM = 28
FONT_LARGE = 56


def init(img_width: int, img_height: int) -> None:
    """
    Compute pixel values from the background image size.
    Must be called before importing objects/rendering modules.
    """
    global WINDOW_WIDTH, WINDOW_HEIGHT
    global TABLE_LEFT, TABLE_RIGHT, TABLE_TOP, TABLE_BOTTOM
    global TABLE_CENTER_X, TABLE_WIDTH, NET_Y
    global BALL_RADIUS, BALL_BASE_SPEED, BALL_MAX_SPEED, BOUNCE_HEIGHT
    global BOUNCE_CYCLE_DISTANCE, LANDING_DIST, OWN_BOUNCE_DIST
    global PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_TRACK_SPEED, HIT_ZONE_HEIGHT
    global PADDLE1_INIT_X, PADDLE1_INIT_Y, PADDLE1_BOUNDS
    global PADDLE2_INIT_X, PADDLE2_INIT_Y, PADDLE2_BOUNDS

    WINDOW_WIDTH = int(img_width * SCREEN_SCALE)
    WINDOW_HEIGHT = int(img_height * SCREEN_SCALE)

    sx = (img_width * SCREEN_SCALE) / REF_WIDTH
    sy = (img_height * SCREEN_SCALE) / REF_HEIGHT
    scale = min(sx, sy)

    # ── Table ──
    TABLE_LEFT = int(img_width * _TABLE_LEFT_RATIO * SCREEN_SCALE)
    TABLE_RIGHT = int(img_width * _TABLE_RIGHT_RATIO * SCREEN_SCALE)
    TABLE_TOP = int(img_height * _TABLE_TOP_RATIO * SCREEN_SCALE)
    TABLE_BOTTOM = int(img_height * _TABLE_BOTTOM_RATIO * SCREEN_SCALE)
    TABLE_CENTER_X = (TABLE_LEFT + TABLE_RIGHT) // 2
    TABLE_WIDTH = TABLE_RIGHT - TABLE_LEFT
    NET_Y = int(img_height * _NET_Y_RATIO * SCREEN_SCALE)

    table_h = TABLE_BOTTOM - TABLE_TOP

    # ── Ball (speed in px/frame; dt_factor keeps it frame-rate independent) ──
    BALL_RADIUS = max(8, int(18 * scale))
    BALL_BASE_SPEED = max(5, int(table_h / 80))
    BALL_MAX_SPEED = max(10, int(table_h / 30))
    BOUNCE_HEIGHT = max(4, int(14 * scale))
    BOUNCE_CYCLE_DISTANCE = max(30, int(table_h / 5))
    LANDING_DIST = max(40, int(table_h * 0.07))
    OWN_BOUNCE_DIST = max(35, int(table_h * 0.06))

    # ── Paddle ──
    PADDLE_WIDTH = max(24, int(60 * scale))
    PADDLE_HEIGHT = max(8, int(20 * scale))
    HIT_ZONE_HEIGHT = max(40, int(100 * scale))

    # Player 1 (bottom of screen)
    PADDLE1_INIT_X = TABLE_CENTER_X
    PADDLE1_INIT_Y = int(img_height * 0.78 * SCREEN_SCALE)
    PADDLE1_BOUNDS = {
        'min_x': int(img_width * 0.18 * SCREEN_SCALE),
        'max_x': int(img_width * 0.82 * SCREEN_SCALE),
        'min_y': int(img_height * 0.68 * SCREEN_SCALE),
        'max_y': int(img_height * 0.88 * SCREEN_SCALE),
    }

    # Player 2 (top of screen)
    PADDLE2_INIT_X = TABLE_CENTER_X
    PADDLE2_INIT_Y = int(img_height * 0.22 * SCREEN_SCALE)
    PADDLE2_BOUNDS = {
        'min_x': int(img_width * 0.18 * SCREEN_SCALE),
        'max_x': int(img_width * 0.82 * SCREEN_SCALE),
        'min_y': int(img_height * 0.12 * SCREEN_SCALE),
        'max_y': int(img_height * 0.32 * SCREEN_SCALE),
    }
