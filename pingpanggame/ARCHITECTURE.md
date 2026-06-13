# 🏗️ 游戏代码架构设计

## 1. 整体架构概览

### 1.1 架构模式：分层游戏循环

```
┌─────────────────────────────────────────────┐
│                  main.py                     │
│        游戏主循环 (Game Loop)                 │
│                                              │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│   │  输入处理  │→│  逻辑更新  │→│  渲染绘制  │  │
│   │ input/    │ │ objects/  │ │ rendering/│  │
│   └──────────┘  └──────────┘  └──────────┘  │
│         ↑              ↑              ↑       │
│   ┌─────────────────────────────────────┐    │
│   │           config.py                 │    │
│   │        所有配置常量                  │    │
│   └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

### 1.2 模块依赖关系（只允许单向依赖）

```
main.py
  ├── config.py            (无依赖)
  ├── game_state.py        (依赖 config)
  ├── input/controller.py  (依赖 config)
  ├── objects/
  │   ├── ball.py          (依赖 config)
  │   └── paddle.py        (依赖 config)
  ├── rendering/
  │   ├── renderer.py      (依赖 config, objects/ball, objects/paddle)
  │   ├── hud.py           (依赖 config)
  │   └── effects.py       (依赖 config)
  └── audio/
      └── sound_manager.py (依赖 config)
```

> **规则**：低层模块（objects/）不依赖高层模块（rendering/）。数据从低层流向高层。

---

## 2. 核心类设计

### 2.1 Ball（球）

```python
# objects/ball.py

class Ball:
    """球：位置、速度、物理碰撞、伪3D弹跳动画"""
    
    def __init__(self):
        self.x: float = 0          # 当前 X 坐标（像素）
        self.y: float = 0          # 当前 Y 坐标（像素）
        self.vx: float = 0         # X 方向速度
        self.vy: float = 0         # Y 方向速度
        self.radius: float = 10    # 球半径
        self.bounce_phase: float = 0.0  # 弹跳动画相位
        self.alive: bool = True    # 是否在游戏中
        self.trail: list = []      # 轨迹点 [(x,y), ...]
    
    def reset(self, direction: str = "up"):
        """发球重置：将球放到发球方半场，赋予初始速度"""
        pass
    
    def update(self, dt: float):
        """更新位置、速度、弹跳动画、轨迹"""
        # 1. 位置更新: x += vx * dt_factor
        # 2. 边界碰撞
        # 3. 弹跳相位更新
        # 4. 轨迹记录
        pass
    
    def get_bounce_y(self, time: float) -> float:
        """获取弹跳高度偏移量（伪3D效果）"""
        pass
    
    def get_scaled_radius(self) -> float:
        """根据 Y 位置返回视觉缩放后的半径（近大远小）"""
        pass

    def get_rect(self) -> pygame.Rect:
        """获取碰撞矩形"""
        pass
```

**数据流**：
```
Ball.update(dt)
  → 读取 self.vx, self.vy
  → 写入 self.x, self.y
  → 边界碰撞 → 修改 self.vx
  → 更新 self.bounce_phase

外部调用：
  Ball.update(dt)               # 每帧更新物理
  collision(ball, paddle)       # 碰撞检测（外部函数）
  → 修改 ball.vx, ball.vy      # 碰撞后改变速度
```

### 2.2 Paddle（球拍）

```python
# objects/paddle.py

class Paddle:
    """球拍：位置、移动、边界限制、绘制辅助"""
    
    def __init__(self, player_id: int):
        self.player_id: int = player_id   # 1 或 2
        self.x: float = 0                 # 中心 X 坐标
        self.y: float = 0                 # 中心 Y 坐标
        self.width: int = 60              # 宽度（像素）
        self.height: int = 20             # 高度（像素）
        self.speed: float = 7.0           # 移动速度
        self.color: tuple = (0, 0, 0)     # 颜色
        self.bounds: dict = {}            # 移动边界 {min_x, max_x, min_y, max_y}
        self.hit_cooldown: float = 0      # 击球冷却
        self._init_from_config()          # 从 config 读取参数
    
    def _init_from_config(self):
        """根据 player_id 从 config 加载位置、颜色、边界"""
        pass
    
    def update(self, dt: float, dx: float, dy: float):
        """移动球拍，应用边界限制"""
        # self.x += dx * self.speed * dt_factor
        # self.y += dy * self.speed * dt_factor
        # clamp(self.x, bounds)
        # clamp(self.y, bounds)
        # self.hit_cooldown = max(0, self.hit_cooldown - dt)
        pass
    
    def get_rect(self) -> pygame.Rect:
        """返回用于碰撞检测的矩形"""
        pass
    
    def can_hit(self) -> bool:
        """是否可击球（冷却中返回 False）"""
        pass
```

### 2.3 碰撞检测（独立函数）

```python
# objects/collision.py  (或放在 objects/__init__.py)

def check_ball_paddle(ball: Ball, paddle: Paddle) -> bool:
    """检测球和球拍碰撞，若碰撞则改变球的速度"""
    # 1. 矩形与圆形碰撞检测
    # 2. 碰撞则反转 vy，根据偏移调整 vx
    # 3. 限制最大速度
    # 4. 设置球拍冷却
    pass

def check_ball_wall(ball: Ball, table_bounds: tuple) -> str | None:
    """检测球是否出界，返回 'left'/'right'/'top'/'bottom' 或 None"""
    pass

def check_ball_net(ball: Ball, net_y: float) -> bool:
    """检测球是否碰网"""
    pass
```

### 2.4 GameState（状态机）

```python
# game_state.py

from enum import Enum, auto

class State(Enum):
    TITLE = auto()
    COUNTDOWN = auto()
    PLAYING = auto()
    SCORED = auto()
    GAME_OVER = auto()

class GameState:
    """管理游戏状态流转、计时、过渡"""
    
    def __init__(self):
        self.current: State = State.TITLE
        self.timer: float = 0.0         # 当前状态计时器
        self.countdown_num: int = 3     # 倒计时数字
        self.scores: list = [0, 0]      # [玩家1得分, 玩家2得分]
        self.server: int = 1            # 当前发球方
        self.winner: int | None = None  # 胜者
    
    def transition(self, new_state: State):
        """切换到新状态，重置计时器"""
        pass
    
    def update(self, dt: float):
        """更新当前状态计时，处理自动过渡"""
        pass
    
    def add_score(self, player: int):
        """给指定玩家加分，检查是否达到胜利条件"""
        pass
    
    def get_winner(self) -> int | None:
        """检查是否有人获胜，返回玩家编号或 None"""
        pass
```

### 2.5 Controller（输入控制）

```python
# input/controller.py

class Controller:
    """统一输入接口，将按键映射为方向向量"""
    
    # 按键映射表
    KEY_MAP = {
        1: {'up': pygame.K_w, 'down': pygame.K_s, 
            'left': pygame.K_a, 'right': pygame.K_d,
            'action': pygame.K_SPACE},
        2: {'up': pygame.K_UP, 'down': pygame.K_DOWN,
            'left': pygame.K_LEFT, 'right': pygame.K_RIGHT,
            'action': pygame.K_RETURN}
    }
    
    @staticmethod
    def get_paddle_input(keys: pygame.key.ScancodeWrapper, 
                         player: int) -> tuple[float, float]:
        """返回 (dx, dy)，范围 -1~1，对角线归一化"""
        pass
    
    @staticmethod
    def get_action_down(events: list, player: int) -> bool:
        """检测是否按下动作键（用于菜单选择）"""
        pass
```

### 2.6 Renderer（渲染主控）

```python
# rendering/renderer.py

class Renderer:
    """统筹所有绘制操作"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen: pygame.Surface = screen
        self.background: pygame.Surface = None  # AI 背景图
        self.fonts: dict = {}                    # 预加载字体
        self.hud: HUD = HUD()
        self.effects: ParticleSystem = ParticleSystem()
        self._load_assets()
    
    def _load_assets(self):
        """加载背景图、字体"""
        pass
    
    def render(self, ball: Ball, paddles: list[Paddle], 
               state: GameState):
        """一帧的完整渲染管线"""
        # 1. 绘制背景
        # 2. 绘制球网
        # 3. 绘制粒子（底层部分）
        # 4. 绘制球的阴影
        # 5. 绘制球
        # 6. 绘制球拍
        # 7. 绘制粒子（上层部分）
        # 8. 绘制 HUD
        # 9. 根据状态绘制覆盖层
        pass
```

### 2.7 HUD（界面）

```python
# rendering/hud.py

class HUD:
    """计分板、按键提示、消息弹窗"""
    
    def draw_scores(self, screen, scores: list[int]):
        """绘制双方得分"""
        pass
    
    def draw_controls(self, screen):
        """绘制按键提示"""
        pass
    
    def draw_center_message(self, screen, text: str, 
                            size: int = 48, color: tuple = WHITE):
        """屏幕中央消息（倒计时、GO!、胜利等）"""
        pass
    
    def draw_score_popup(self, screen, player: int, timer: float):
        """得分弹出动画"""
        pass
```

### 2.8 粒子系统

```python
# rendering/effects.py

class Particle:
    def __init__(self, x, y, vx, vy, lifetime, color, size):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.color = color
        self.size = size

class ParticleSystem:
    """粒子特效系统（击球火花、得分光效）"""
    
    def __init__(self):
        self.particles: list[Particle] = []
    
    def emit_hit(self, x: float, y: float):
        """击球火花效果"""
        pass
    
    def emit_score(self, x: float, y: float):
        """得分光效"""
        pass
    
    def update(self, dt: float):
        """更新所有粒子生命和位置"""
        pass
    
    def draw(self, screen: pygame.Surface):
        """绘制所有存活粒子"""
        pass
```

---

## 3. 主循环与数据流

### 3.1 主循环（main.py）

```python
# main.py — 伪代码结构

def main():
    # ── 初始化 ──
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    
    # ── 游戏对象 ──
    state = GameState()
    ball = Ball()
    paddles = [Paddle(1), Paddle(2)]
    controller = Controller()
    renderer = Renderer(screen)
    
    # ── 主循环 ──
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        
        # 1. 事件处理
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                handle_menu_input(event, state)
        
        # 2. 按键状态
        keys = pygame.key.get_pressed()
        
        # 3. 更新逻辑
        update(dt, keys, events, state, ball, paddles, renderer.effects)
        
        # 4. 渲染
        renderer.render(ball, paddles, state)
        pygame.display.flip()
    
    pygame.quit()


def update(dt, keys, events, state, ball, paddles, effects):
    """核心更新逻辑"""
    if state.current == State.TITLE:
        # 只是等待按键进入
        pass
    
    elif state.current == State.COUNTDOWN:
        state.update(dt)
        # 倒计时结束自动进入 PLAYING
    
    elif state.current == State.PLAYING:
        # 玩家输入 → 移动球拍
        for i, paddle in enumerate(paddles):
            dx, dy = Controller.get_paddle_input(keys, i + 1)
            paddle.update(dt, dx, dy)
        
        # 更新球
        ball.update(dt)
        
        # 碰撞检测
        for paddle in paddles:
            if check_ball_paddle(ball, paddle):
                effects.emit_hit(ball.x, ball.y)
        
        # 得分检测
        result = check_ball_wall(ball, TABLE_BOUNDS)
        if result == 'top':    # 球出顶端 → 玩家1得分
            state.add_score(1)
            effects.emit_score(ball.x, TABLE_TOP)
        elif result == 'bottom':  # 球出底端 → 玩家2得分
            state.add_score(2)
            effects.emit_score(ball.x, TABLE_BOTTOM)
        
        # 碰网检测
        if check_ball_net(ball, NET_Y):
            effects.emit_hit(ball.x, NET_Y)
        
        # 粒子更新
        effects.update(dt)
    
    elif state.current == State.SCORED:
        state.update(dt)
        effects.update(dt)
        # 计时结束自动回到 COUNTDOWN
    
    elif state.current == State.GAME_OVER:
        state.update(dt)
        effects.update(dt)
```

### 3.2 数据流图（每帧）

```
                    ┌───────────────┐
                    │  pygame事件    │
                    │  (QUIT, KEYUP) │
                    └───────┬───────┘
                            ↓
               ┌────────────────────┐
               │  handle_menu_input │  ← TITLE/GAMEOVER 状态的按键处理
               │  (start, restart)  │
               └────────────────────┘
                           
                    ┌───────────────┐
                    │  pygame按键    │
                    │  get_pressed() │
                    └───────┬───────┘
                            ↓
               ┌────────────────────┐
               │ Controller.        │
               │ get_paddle_input() │ → 返回 (dx, dy)
               └───────┬────────────┘
                       │ dx, dy
                       ↓
               ┌────────────────────┐
               │ Paddle.update()    │ → 修改 self.x, self.y
               └───────┬────────────┘
                       │
               ┌───────┴────────────┐
               │ Ball.update()      │ → 修改 self.x, self.y, self.vx, self.vy
               └───────┬────────────┘
                       │
               ┌───────┴────────────┐
               │ 碰撞检测函数         │ → 修改 ball.vx, ball.vy
               │ check_ball_paddle()│ → 修改 paddle.hit_cooldown
               │ check_ball_wall()  │ → 触发 add_score()
               │ check_ball_net()   │ → 修改 ball.vy
               └───────┬────────────┘
                       │
               ┌───────┴────────────┐
               │ GameState.update() │ → 自动状态切换
               │ GameState.add_     │
               │   score()          │
               └───────┬────────────┘
                       │
               ┌───────┴────────────┐
               │ Effects.update()   │ → 粒子位置/生命
               └───────┬────────────┘
                       │
                       ↓
               ┌────────────────────┐
               │ Renderer.render()  │ → 绘制所有内容到 screen
               └────────────────────┘
                       ↓
               ┌────────────────────┐
               │ pygame.display.    │
               │   flip()          │ → 交换缓冲区
               └────────────────────┘
```

---

## 4. 配置系统

### 4.1 config.py 设计

```python
# config.py — 所有可调参数集中管理

import pygame

# ── 窗口 ──
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600
FPS = 60
TITLE = "🏓 俯视乒乓双人对战"

# ── 桌面区域（在背景图上的像素坐标）──
TABLE_LEFT = 100
TABLE_RIGHT = 800
TABLE_TOP = 80
TABLE_BOTTOM = 520
TABLE_CENTER_X = (TABLE_LEFT + TABLE_RIGHT) // 2
TABLE_WIDTH = TABLE_RIGHT - TABLE_LEFT

# ── 球网 ──
NET_Y = 300
NET_COLOR = (200, 200, 200, 128)  # RGBA

# ── 球 ──
BALL_RADIUS = 10
BALL_BASE_SPEED = 360        # 像素/秒
BALL_MAX_SPEED = 900
BALL_ACCEL = 1.05            # 每次击球加速 5%
BALL_COLOR = (255, 107, 53)  # 橙色
BOUNCE_HEIGHT = 15           # 弹跳最大高度（像素）
BOUNCE_FREQ = 0.01           # 弹跳频率

# ── 球拍 ──
PADDLE_WIDTH = 60
PADDLE_HEIGHT = 20
PADDLE_SPEED = 420           # 像素/秒
HIT_COOLDOWN = 0.15          # 击球冷却（秒）

PADDLE1_COLOR = (78, 205, 196)   # 青蓝
PADDLE1_INIT_X = TABLE_CENTER_X
PADDLE1_INIT_Y = 460
PADDLE1_BOUNDS = {
    'min_x': 150, 'max_x': 750,
    'min_y': 380, 'max_y': 520
}

PADDLE2_COLOR = (255, 107, 107)  # 珊瑚红
PADDLE2_INIT_X = TABLE_CENTER_X
PADDLE2_INIT_Y = 140
PADDLE2_BOUNDS = {
    'min_x': 150, 'max_x': 750,
    'min_y': 80, 'max_y': 220
}

# ── 游戏规则 ──
WIN_SCORE = 11
SERVER_CHANGE = 2       # 每几分交换发球权
COUNTDOWN_SECONDS = 2   # 倒计时秒数
SCORE_PAUSE = 1.5       # 得分后暂停秒数

# ── 背景图 ──
BACKGROUND_PATH = "assets/background.png"

# ── 颜色 ──
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
SHADOW_COLOR = (0, 0, 0)

# ── 字体 ──
FONT_NAME = None         # None = 默认字体
FONT_SMALL = 24
FONT_LARGE = 72
```

### 4.2 使用方法

```python
# 任何模块中
from config import *

# 使用常量
ball_speed = BALL_BASE_SPEED
```

---

## 5. 初始化流程

### 5.1 游戏启动时序

```
main() 调用
  │
  ├── pygame.init()
  ├── screen = set_mode(900, 600)
  │
  ├── Renderer(screen)
  │   ├── 加载 assets/background.png
  │   ├── 自适应缩放 + 居中裁剪
  │   ├── 预创建字体对象
  │   └── 初始化粒子系统
  │
  ├── GameState()
  │   ├── 初始状态 = TITLE
  │   └── 分数 = [0, 0]
  │
  ├── Ball()
  │   ├── 半径 = config.BALL_RADIUS
  │   └── 位置 / 速度 = 0
  │
  ├── Paddle(1)
  │   ├── 从 config 读取玩家1 参数
  │   └── 移动到初始位置
  │
  ├── Paddle(2)
  │   ├── 从 config 读取玩家2 参数
  │   └── 移动到初始位置
  │
  └── 进入主循环 while running:
        ├── clock.tick(60)
        ├── 事件处理
        ├── update(dt, ...)
        └── render()
```

---

## 6. 渲染管线详解

### 6.1 每帧渲染顺序

```python
def render(self, ball, paddles, state):
    # Layer 0: 背景
    self.screen.blit(self.background, (0, 0))
    
    # Layer 1: 球网（如果背景图不含球网，手动补绘）
    if not self.background_has_net:
        self._draw_net()
    
    # Layer 2: 球阴影（在球正下方）
    shadow_y = ball.y  # 阴影在桌面高度，不随弹跳上移
    self._draw_shadow(ball.x, shadow_y, ball.get_scaled_radius())
    
    # Layer 3: 球
    bounce_y = ball.get_bounce_y(pygame.time.get_ticks())
    draw_y = ball.y - bounce_y
    scaled_r = ball.get_scaled_radius()
    pygame.draw.circle(self.screen, BALL_COLOR, 
                       (int(ball.x), int(draw_y)), int(scaled_r))
    # 球高光
    self._draw_ball_highlight(ball.x, draw_y, scaled_r)
    
    # Layer 4: 球拍（带3D厚度效果）
    for paddle in paddles:
        self._draw_paddle(paddle)
    
    # Layer 5: 粒子特效（上层）
    self.effects.draw(self.screen)
    
    # Layer 6: HUD
    self.hud.draw_scores(self.screen, state.scores)
    self.hud.draw_controls(self.screen)
    
    # Layer 7: 状态覆盖层
    if state.current == State.TITLE:
        self.hud.draw_center_message(self.screen, "🏓 俯视乒乓")
        self.hud.draw_center_message(self.screen, "按 空格 开始", 
                                     size=36, y_offset=60)
    elif state.current == State.COUNTDOWN:
        self.hud.draw_countdown(self.screen, state.countdown_num)
    elif state.current == State.SCORED:
        self.hud.draw_score_popup(self.screen, state.last_scorer, 
                                  state.timer)
    elif state.current == State.GAME_OVER:
        self.hud.draw_center_message(self.screen, 
            f"🏆 玩家{state.winner} 获胜！")
        self.hud.draw_center_message(self.screen, "按 R 重新开始",
                                     size=36, y_offset=60)
```

---

## 7. 关键算法细节

### 7.1 球拍-球 碰撞检测

```python
def check_ball_paddle(ball: Ball, paddle: Paddle) -> bool:
    """矩形球拍 vs 圆形球，碰撞后反弹"""
    if paddle.hit_cooldown > 0:
        return False
    
    # 找矩形上离圆最近的点
    closest_x = max(paddle.x - paddle.width/2, 
                    min(ball.x, paddle.x + paddle.width/2))
    closest_y = max(paddle.y - paddle.height/2, 
                    min(ball.y, paddle.y + paddle.height/2))
    
    dx = ball.x - closest_x
    dy = ball.y - closest_y
    dist = math.sqrt(dx*dx + dy*dy)
    
    if dist < ball.radius:
        # 碰撞方向：球从哪边来就在哪边反弹
        # 主要反转 Y 方向（前后）
        ball.vy = -ball.vy * BALL_ACCEL
        
        # 根据击球点偏移调整水平角度
        offset = (ball.x - paddle.x) / (paddle.width / 2)  # -1 ~ 1
        ball.vx += offset * 100  # 加一点水平速度
        
        # 限速
        speed = math.hypot(ball.vx, ball.vy)
        if speed > BALL_MAX_SPEED:
            ball.vx *= BALL_MAX_SPEED / speed
            ball.vy *= BALL_MAX_SPEED / speed
        
        # 防止球卡在拍内
        overlap = ball.radius - dist
        if dy != 0:
            ball.y += overlap * (dy / abs(dy))
        
        paddle.hit_cooldown = HIT_COOLDOWN
        return True
    
    return False
```

### 7.2 球弹跳动画

```python
def get_bounce_y(self, time_ms: int) -> float:
    """伪3D弹跳偏移：球在飞行时上下浮动"""
    if abs(self.vy) < 10:  # 球几乎不动时停止弹跳
        return 0
    phase = (time_ms * BOUNCE_FREQ) % (2 * math.pi)
    return abs(math.sin(phase)) * BOUNCE_HEIGHT
```

### 7.3 近大远小缩放

```python
def get_scaled_radius(self) -> float:
    """根据 Y 位置做近大远小缩放"""
    progress = (self.y - TABLE_TOP) / (TABLE_BOTTOM - TABLE_TOP)
    progress = max(0.0, min(1.0, progress))  # 夹紧
    scale = 0.85 + progress * 0.3  # 范围 0.85 ~ 1.15
    return self.radius * scale
```

---

## 8. 模块接口汇总

### 8.1 对象模块接口

```python
# objects/__init__.py
from .ball import Ball
from .paddle import Paddle

def check_ball_paddle(ball, paddle) -> bool: ...
def check_ball_wall(ball, bounds) -> str | None: ...
def check_ball_net(ball, net_y) -> bool: ...
```

### 8.2 输入模块接口

```python
# input/__init__.py
from .controller import Controller
# Controller.get_paddle_input(keys, player) -> (dx, dy)
# Controller.get_action_down(events, player) -> bool
```

### 8.3 渲染模块接口

```python
# rendering/__init__.py
from .renderer import Renderer
from .hud import HUD
from .effects import ParticleSystem, Particle
```

---

## 9. 文件依赖与创建顺序

建议按以下顺序创建文件，每步可运行验证：

```
Step 1:  config.py          ← 独立，无依赖
Step 2:  main.py            ← 骨架（窗口 + 主循环）
Step 3:  game_state.py      ← 独立，依赖 config
Step 4:  objects/ball.py    ← 依赖 config
Step 5:  objects/paddle.py  ← 依赖 config
Step 6:  objects/collision.py  ← 依赖 ball, paddle
Step 7:  input/controller.py   ← 依赖 config
Step 8:  rendering/hud.py      ← 依赖 config
Step 9:  rendering/effects.py  ← 依赖 config
Step 10: rendering/renderer.py ← 依赖 config + 以上所有
         → 完整可运行！
```

> 💡 **建议**：每完成一步就跑一下确认无报错，不要一口气写完再调试。

---

## 10. 架构核心原则

| 原则 | 说明 |
|------|------|
| **单一职责** | 每个类只做一件事（Ball 管物理，Renderer 管绘制） |
| **单向依赖** | objects → rendering （绝不反向） |
| **配置集中** | 所有魔法数字在 config.py，不要散落在各文件 |
| **接口清晰** | 模块通过 `__init__.py` 暴露统一接口 |
| **状态驱动** | 游戏行为由 GameState.current 控制，避免散乱的 flag |
| **数据向下** | 输入→逻辑→渲染，数据单向流动 |
