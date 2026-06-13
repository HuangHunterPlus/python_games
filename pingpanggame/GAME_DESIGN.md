# 🏓 俯视乒乓双人对战 — 游戏设计方案

## 1. 概述

### 1.1 游戏简介
一款**双人本地对战**的乒乓球游戏。  
采用**正上方向下俯视**的视角，AI 生成的乒乓球桌高清图作为游戏背景。  
双方在同一屏幕上对战：玩家1 在屏幕下方（近端），玩家2 在屏幕上方（远端），球在桌面上前后左右运动。

### 1.2 核心特色
| 特色 | 说明 |
|------|------|
| **俯视视角** | 正上方向下俯瞰整张球桌，一目了然 |
| **AI 实景背景** | 用 AI 生成的球桌图片作为背景，视觉沉浸感强 |
| **纵深玩法** | 球在桌面上下（Y轴纵深）前后运动 |
| **本地双人** | 同一键盘，两位玩家对战 |
| **单屏同框** | 不分屏，双方在同一画面中竞技 |

---

## 2. 游戏规则

### 2.1 基本规则
- 双方各在球桌一端：**玩家1 在下方（近端）**，**玩家2 在上方（远端）**
- 球在桌面上方运动，先到达对方底线者得分
- 玩家需用球拍拦截并击回球
- **先得 11 分者获胜**（需领先 2 分）

### 2.2 得分规则
| 情况 | 结果 |
|------|------|
| 球越过对方底线（出屏幕上方/下方） | 靠近该底线的玩家 +1 分 |
| 球拍击球出桌面左右边界 | 对方 +1 分 |
| 球拍未击中球（让球从身边溜过到底线） | 对方 +1 分 |
| 球在桌面弹地超过一次 | 对方 +1 分 |

> **简化版**：球碰到屏幕顶端 → 玩家1 得分；球碰到屏幕底端 → 玩家2 得分

### 2.3 发球规则
- 每 2 分交换一次发球权
- 发球方球从己方半场发出，飞向对方半场
- 首局玩家1 先发球

---

## 3. 坐标系与空间设计

### 3.1 二维坐标系
游戏采用**2D 坐标**，直接在屏幕像素空间中进行：

```
(0, 0) ────────────────→ X (左右)
  │
  │     ┌───────────────┐
  │     │   玩家2 (远端) │
  │     │               │      屏幕/桌面
  │     │    ● 球       │
  │     │               │
  │     │   玩家1 (近端) │
  │     └───────────────┘
  ↓
  Y (前后/纵深)
```

| 轴 | 含义 | 说明 |
|----|------|------|
| **X** | 桌面宽度方向（左右） | 左边界 ~ 右边界 |
| **Y** | 纵深方向（前后） | 上端=玩家2，下端=玩家1 |

### 3.2 坐标映射（基于背景图）

游戏窗口尺寸固定为 `WINDOW_WIDTH × WINDOW_HEIGHT`（例如 900×600）。

背景图覆盖整个窗口，所有游戏物体坐标与背景图像素对齐：

| 参数 | 默认值（900×600窗口） | 说明 |
|------|----------------------|------|
| 桌面区域 | (100, 50) ~ (800, 550) | 背景图中球桌的有效区域 |
| 桌面中心 X | 450 | 左右居中 |
| 桌面顶部 Y（玩家2底线） | 80 | 远端底线 |
| 桌面底部 Y（玩家1底线） | 520 | 近端底线 |
| 球网位置 Y | 300 | 正中央 |
| 球拍移动范围 X | 150 ~ 750 | 左右边界 |
| 球拍移动范围 Y（玩家1） | 400 ~ 520 | 近端半场 |
| 球拍移动范围 Y（玩家2） | 80 ~ 200 | 远端半场 |

> 💡 这些参数在首次运行时根据背景图实际尺寸微调，写入 `config.py`。

### 3.3 伪3D 氛围（在俯视图上）

虽然是俯视视角，但通过以下手法保留"伪3D"感：

| 手法 | 实现方式 |
|------|---------|
| **球阴影** | 在球正下方绘制半透明椭圆阴影，球弹起时阴影与球分离 |
| **球拍厚度** | 球拍绘制时加一个小倾斜阴影，显得有立体感 |
| **球缩放** | 球在靠近玩家1（屏幕下方）时略微放大，靠近玩家2（屏幕上方）时略微缩小，模拟透视 |
| **小球弹跳** | 球沿 Y 轴运动时叠加一个小的正弦波垂直弹跳动画 |
| **粒子效果** | 击球时产生小光点粒子 |

---

## 4. 屏幕布局

### 4.1 整体布局

```
┌──────────────────────────────────────────┐
│  玩家2得分: 3                    P2: ↑↓←→ │  ← HUD 顶部
│──────────────────────────────────────────│
│                                          │
│      ┌────────────────────────┐          │
│      │                        │          │
│  ┌── │       玩家2 半场        │ ──┐      │
│  │   │                        │   │      │
│  │   │──────── 球网 ──────────│   │      │
│  │   │                        │   │      │
│  │   │       玩家1 半场        │   │      │
│  └── │                        │ ──┘      │
│      │      ● 球              │          │
│      └────────────────────────┘          │
│                                          │
│──────────────────────────────────────────│
│  玩家1得分: 5                    P1: WASD  │  ← HUD 底部
└──────────────────────────────────────────┘
```

### 4.2 图层顺序（从下到上）

```
Layer 0: 背景色/星空
Layer 1: AI 生成球桌背景图（全屏）
Layer 2: 球网（绘制在背景图上）
Layer 3: 球阴影
Layer 4: 球
Layer 5: 玩家1 球拍
Layer 6: 玩家2 球拍
Layer 7: 粒子特效
Layer 8: HUD / UI（得分、按键提示）
Layer 9: 消息弹窗（得分提示、倒计时、胜利）
```

### 4.3 HUD 信息

| 区域 | 内容 |
|------|------|
| 屏幕顶部 | 玩家2 得分 + 操作提示（↑↓←→） |
| 屏幕底部 | 玩家1 得分 + 操作提示（WASD） |
| 屏幕中央（弹窗） | 倒计时、得分提示、"GAME OVER" 等 |

---

## 5. 游戏对象设计

### 5.1 球 (Ball)

```python
class Ball:
    x: float           # X 坐标（像素）
    y: float           # Y 坐标（像素）
    vx: float          # X 方向速度
    vy: float          # Y 方向速度
    radius: int        # 球半径（像素）
    bounce_y: float    # 弹跳高度偏移（伪3D效果）
    shadow_offset: int # 阴影偏移
    trail: list        # 轨迹点列表
```

**参数：**
| 属性 | 值 |
|------|-----|
| 球半径 | 10 ~ 14 像素（随Y位置缩放） |
| 基础速度 | 6 像素/帧 (360 像素/秒 @60fps) |
| 最大速度 | 15 像素/帧 |
| 加速比 | 每回合递增 5% |

**行为：**
- 每帧：`x += vx * dt`，`y += vy * dt`
- 触边反弹：`|x - 桌面中心| > 桌面半宽` → `vx = -vx`
- 触拍反弹：碰撞到球拍时反转 `vy` 方向，并根据击球位置偏移调整 `vx`
- 出底线：`y < 桌面顶部` 或 `y > 桌面底部` → 得分，重置
- 弹跳动画：叠加 `sin(time * freq) * amplitude` 到球的绘制 Y 坐标
- 阴影：在球正下方（根据弹跳高度偏移）绘制半透明椭圆

### 5.2 球拍 (Paddle)

```python
class Paddle:
    player: 1 | 2       # 玩家编号
    x: float            # X 坐标
    y: float            # Y 坐标
    width: int          # 宽度（像素）
    height: int         # 长度（像素）
    color: tuple        # 颜色
    hit_cooldown: int   # 击球冷却帧数
```

**参数：**
| 属性 | 玩家1 | 玩家2 |
|------|-------|-------|
| 初始 X | 窗口中心 | 窗口中心 |
| 初始 Y | 460 | 140 |
| 宽度 | 60 像素 | 60 像素 |
| 高度 | 20 像素 | 20 像素 |
| 颜色 | `#4ecdc4` 青蓝 | `#ff6b6b` 珊瑚红 |
| 移动速度 | 7 像素/帧 | 7 像素/帧 |
| 移动范围 X | 150 ~ 750 | 150 ~ 750 |
| 移动范围 Y | 380 ~ 520 | 80 ~ 220 |

**移动：**
- 玩家1：W（上/前）A（左）S（下/后）D（右）
- 玩家2：↑（上/前）←（左）↓（下/后）→（右）
- 可在 X（左右）和 Y（前后）两个维度自由移动

### 5.3 球网 (Net)
```
位置：y = 300（桌面中央）
绘制：在背景图的球网位置叠加一条半透明白线或发光线条
宽度：与桌面同宽
```

### 5.4 背景图
```
文件：assets/background.png
格式：PNG / JPG
尺寸：自适应窗口大小（保持宽高比缩放并裁剪居中）
作用：整个游戏的视觉基础，替代所有手动绘制的桌面和场景
```

---

## 6. 碰撞检测

### 6.1 球拍 ↔ 球（核心碰撞）

```python
def check_paddle_hit(ball, paddle):
    """检测球是否击中球拍"""
    # 碰撞盒检测（矩形 vs 圆形）
    closest_x = clamp(ball.x, paddle.x - paddle.width/2, paddle.x + paddle.width/2)
    closest_y = clamp(ball.y, paddle.y - paddle.height/2, paddle.y + paddle.height/2)
    
    dx = ball.x - closest_x
    dy = ball.y - closest_y
    distance = math.sqrt(dx*dx + dy*dy)
    
    if distance < ball.radius:
        # 击中！反弹
        ball.vy = -ball.vy * 1.05  # 略加速
        
        # 根据击球位置偏移调整水平角度
        offset = (ball.x - paddle.x) / (paddle.width / 2)  # -1 ~ 1
        ball.vx += offset * 2
        
        # 限制最大速度
        speed = math.sqrt(ball.vx**2 + ball.vy**2)
        if speed > MAX_SPEED:
            ball.vx *= MAX_SPEED / speed
            ball.vy *= MAX_SPEED / speed
        
        return True
    return False
```

### 6.2 球 ↔ 桌面边界（左右）

```python
if ball.x - ball.radius < TABLE_LEFT:
    ball.x = TABLE_LEFT + ball.radius
    ball.vx = abs(ball.vx)  # 向右反弹

if ball.x + ball.radius > TABLE_RIGHT:
    ball.x = TABLE_RIGHT - ball.radius
    ball.vx = -abs(ball.vx)  # 向左反弹
```

### 6.3 球 ↔ 底线（得分判定）

```python
if ball.y < TABLE_TOP:        # 球到达屏幕顶部（玩家2底线）
    player1_score += 1
    reset_ball(direction='down')  # 向玩家2方向发球

if ball.y > TABLE_BOTTOM:     # 球到达屏幕底部（玩家1底线）
    player2_score += 1
    reset_ball(direction='up')    # 向玩家1方向发球
```

### 6.4 球 ↔ 球网

```python
if abs(ball.y - NET_Y) < 5 and abs(ball.x - TABLE_CENTER_X) < TABLE_HALF_WIDTH:
    # 球碰到球网，轻微反弹并减速
    ball.vy *= -0.5
    ball.vx += random.uniform(-1, 1)  # 随机偏移
```

---

## 7. 玩家控制

### 7.1 键盘绑定

| 操作 | 玩家1（下方） | 玩家2（上方） |
|------|-------------|--------------|
| **上移（前压）** | **W** | **↑** |
| **下移（后退）** | **S** | **↓** |
| **左移** | **A** | **←** |
| **右移** | **D** | **→** |
| **蓄力击球**（可选） | **空格** | **Enter** |

### 7.2 手柄支持（可选扩展）
- 玩家1：左摇杆
- 玩家2：右摇杆 或 第二手柄

### 7.3 移动逻辑

```python
def update_paddle(paddle, keys, up, down, left, right, dt):
    dx, dy = 0, 0
    if keys[up]:    dy -= 1
    if keys[down]:  dy += 1
    if keys[left]:  dx -= 1
    if keys[right]: dx += 1
    
    # 归一化对角线移动
    if dx != 0 and dy != 0:
        dx *= 0.707  # 1/√2
        dy *= 0.707
    
    paddle.x += dx * paddle.speed * dt * 60
    paddle.y += dy * paddle.speed * dt * 60
    
    # 边界限制
    paddle.x = clamp(paddle.x, paddle.min_x, paddle.max_x)
    paddle.y = clamp(paddle.y, paddle.min_y, paddle.max_y)
```

---

## 8. 游戏流程

### 8.1 状态机

```
TITLE → COUNTDOWN → PLAYING → SCORED → (回到 COUNTDOWN) → GAME_OVER
```

| 状态 | 行为 |
|------|------|
| **TITLE** | 显示标题画面，背景图半透明暗化处理，按空格开始 |
| **COUNTDOWN** | 3-2-1 中央倒计时，球就位 |
| **PLAYING** | 正常对战 |
| **SCORED** | 得分后暂停 1.5 秒，显示 "+1" 特效 |
| **GAME_OVER** | 一方达 11 分，显示胜者，按 R 重新开始 |

### 8.2 单局流程

```
TITLE → 按空格
  → COUNTDOWN (3, 2, 1, GO!)
    → PLAYING（球从发球方发出）
      → 球拍击球 → 继续对打
      → 球出界/出底线 → SCORED（加分）
      → 检查是否 ≥11 分且领先 ≥2 分
        → 是 → GAME_OVER
        → 否 → 交换发球权 → COUNTDOWN
```

### 8.3 发球
- 发球方球从己方半场中后部发出
- 球以随机角度（±30°）飞向对方半场
- 发球前有短暂停顿和提示

---

## 9. 视觉与渲染设计

### 9.1 颜色主题

| 元素 | 颜色 | 备注 |
|------|------|------|
| 背景 | 使用 AI 生成的球桌图片 | 全屏作为底层 |
| 暗化遮罩 | `rgba(0,0,0,0.3)` | TITLE/GAMEOVER 时覆盖 |
| 球 | `#ff6b35` 橙色 | 亮眼，易追踪 |
| 玩家1 球拍 | `#4ecdc4` 青蓝 | 与背景对比明显 |
| 玩家2 球拍 | `#ff6b6b` 珊瑚红 | 与背景对比明显 |
| 球网 | `rgba(255,255,255,0.5)` | 半透明发光线条 |
| HUD 文字 | `#ffffff` 白色 | 带黑色描边 |
| 得分特效 | `#ffd700` 金色 | 得分时闪烁 |

### 9.2 渲染管线（每帧）

```
每一帧：

1. 绘制 AI 背景图（覆盖全屏）
2. 在背景图上方绘制球网（线条发光效果）
3. 绘制球的阴影（半透明椭圆）
4. 绘制球（带弹跳高度偏移）
5. 绘制玩家1 球拍（带3D阴影厚度）
6. 绘制玩家2 球拍（带3D阴影厚度）
7. 绘制粒子特效（击球火花、得分光效）
8. 绘制 HUD（得分、按键提示、分隔线）
9. 根据状态覆盖 TITLE / COUNTDOWN / GAME_OVER 画面
```

### 9.3 球的伪3D 弹跳效果

```python
def draw_ball(screen, ball, time):
    """绘制球，包含伪3D弹跳效果"""
    # 弹跳高度 = 正弦波
    bounce = abs(math.sin(time * 0.01)) * 15  # 0~15 像素弹跳高度
    draw_y = ball.y - bounce  # 球往上移
    
    # 根据 Y 坐标缩放球的大小（近大远小）
    y_ratio = (ball.y - TABLE_TOP) / (TABLE_BOTTOM - TABLE_TOP)  # 0~1
    scale = 0.85 + y_ratio * 0.3  # 0.85 ~ 1.15
    draw_radius = ball.radius * scale
    
    # 阴影（在桌面位置，不随弹跳上移）
    shadow_radius = draw_radius * 0.7
    shadow_surface = pygame.Surface((shadow_radius*2, shadow_radius*2), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_surface, (*SHADOW_COLOR, 80), 
                        (0, 0, shadow_radius*2, shadow_radius*2))
    screen.blit(shadow_surface, (ball.x - shadow_radius, ball.y - shadow_radius//2))
    
    # 球体
    pygame.draw.circle(screen, BALL_COLOR, (int(ball.x), int(draw_y)), int(draw_radius))
    # 高光
    highlight_radius = draw_radius * 0.3
    pygame.draw.circle(screen, (255, 255, 255, 180),
                      (int(ball.x - draw_radius*0.2), int(draw_y - draw_radius*0.2)), 
                      int(highlight_radius))
```

### 9.4 球拍的3D 厚度效果

```python
def draw_paddle(screen, paddle, is_player1):
    """绘制球拍，带伪3D厚度阴影"""
    # 阴影/厚度（偏移几个像素）
    shadow_rect = pygame.Rect(
        paddle.x - paddle.width//2 + 3,
        paddle.y - paddle.height//2 + 3,
        paddle.width, paddle.height
    )
    pygame.draw.rect(screen, (0, 0, 0, 60), shadow_rect, border_radius=5)
    
    # 主体
    main_rect = pygame.Rect(
        paddle.x - paddle.width//2,
        paddle.y - paddle.height//2,
        paddle.width, paddle.height
    )
    pygame.draw.rect(screen, paddle.color, main_rect, border_radius=5)
    
    # 高光条
    highlight_rect = pygame.Rect(
        paddle.x - paddle.width//2 + 4,
        paddle.y - paddle.height//2 + 3,
        paddle.width - 8, paddle.height // 3
    )
    pygame.draw.rect(screen, (255, 255, 255, 40), highlight_rect, border_radius=3)
```

---

## 10. 音效设计（可选扩展）

| 音效 | 触发时机 |
|------|---------|
| `serve.wav` | 发球 |
| `hit.wav` | 球拍击球 |
| `bounce.wav` | 球碰桌面/边界 |
| `score.wav` | 得分 |
| `win.wav` | 比赛结束 |
| `net.wav` | 球碰球网 |

---

## 11. 项目文件结构

```
game1/
├── main.py                # 游戏入口，主循环
├── config.py              # 所有常量/可调参数
├── game_state.py          # 状态机管理
├── objects/
│   ├── __init__.py
│   ├── ball.py            # 球类
│   ├── paddle.py          # 球拍类
│   └── net.py             # 球网类（绘制辅助）
├── rendering/
│   ├── __init__.py
│   ├── renderer.py        # 主渲染管线
│   ├── hud.py             # 计分板/UI
│   └── effects.py         # 粒子/弹跳/阴影特效
├── input/
│   ├── __init__.py
│   └── controller.py      # 按键映射
├── audio/
│   ├── __init__.py
│   └── sound_manager.py   # 音效管理
├── assets/
│   ├── background.png     # ⭐ AI 生成的球桌背景图
│   └── sounds/            # 音效文件（可选）
└── GAME_DESIGN.md         # 本设计文档
```

---

## 12. 开发路线图

### Phase 1 — 项目骨架（~1天）
- [ ] 初始化项目结构及 `main.py`
- [ ] 配置参数 `config.py`
- [ ] 加载并显示 AI 背景图
- [ ] 实现游戏主循环和 `GameState` 状态机
- [ ] 窗口创建与帧率控制

### Phase 2 — 核心玩法（~1天）
- [ ] 实现球的 2D 物理运动
- [ ] 实现两个球拍的控制（WASD + 方向键）
- [ ] 实现球与球拍的碰撞检测
- [ ] 实现球与桌面边界的碰撞

### Phase 3 — 游戏规则（~0.5天）
- [ ] 实现得分系统
- [ ] 实现发球与交换发球权
- [ ] 实现完整游戏流程（得分→重置→继续→结束）
- [ ] 胜利条件判断

### Phase 4 — 视觉打磨（~0.5天）
- [ ] 球的弹跳动画（伪3D效果）
- [ ] 球拍 3D 阴影厚度
- [ ] 球阴影和缩放效果
- [ ] HUD 计分板
- [ ] 得分特效

### Phase 5 — 完善（~1天）
- [ ] TITLE / COUNTDOWN / GAME_OVER 画面
- [ ] 音效集成
- [ ] 手感和平衡性调试
- [ ] 粒子特效

---

## 13. 技术参考

### 13.1 关键 Pygame API

```python
import pygame

# 初始化
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("🏓 俯视乒乓双人对战")
clock = pygame.time.Clock()

# 加载背景图
background = pygame.image.load("assets/background.png")
background = pygame.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT))

# 主循环
running = True
while running:
    dt = clock.tick(60) / 1000.0
    
    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # 按键状态
    keys = pygame.key.get_pressed()
    
    # 更新逻辑
    update(dt, keys)
    
    # 渲染
    screen.blit(background, (0, 0))
    render(screen)
    pygame.display.flip()

pygame.quit()
```

### 13.2 数学工具

```python
import math
import random

def clamp(value, min_val, max_val):
    return max(min_val, min(value, max_val))

def lerp(a, b, t):
    return a + (b - a) * t

def distance(x1, y1, x2, y2):
    return math.sqrt((x2-x1)**2 + (y2-y1)**2)

def random_angle(min_deg, max_deg):
    """返回指定角度范围（度）的随机单位向量"""
    angle = math.radians(random.uniform(min_deg, max_deg))
    return math.cos(angle), math.sin(angle)
```

### 13.3 背景图自适应

```python
def load_background(image_path, screen_width, screen_height):
    """加载背景图并自适应窗口尺寸"""
    img = pygame.image.load(image_path)
    img_w, img_h = img.get_size()
    
    # 保持宽高比缩放到覆盖窗口
    scale = max(screen_width / img_w, screen_height / img_h)
    new_w = int(img_w * scale)
    new_h = int(img_h * scale)
    
    img = pygame.transform.scale(img, (new_w, new_h))
    
    # 居中裁剪
    crop_x = (new_w - screen_width) // 2
    crop_y = (new_h - screen_height) // 2
    return img.subsurface((crop_x, crop_y, screen_width, screen_height))
```

---

## 14. 扩展创意

| 扩展 | 描述 | 难度 |
|------|------|------|
| ⚡ **蓄力击球** | 长按空格/Enter 蓄力，松开大力击球 | 简单 |
| 🌀 **球旋转** | 根据球拍移动方向给球加旋转，弧线球 | 中等 |
| 🤖 **AI 对手** | 单人模式 vs 电脑 | 中等 |
| 🏆 **三局两胜** | 多局赛制 | 简单 |
| 🎮 **手柄支持** | 接入双手柄 | 中等 |
| 🌈 **球拍皮肤** | 可选颜色/样式 | 简单 |
| 📊 **赛后统计** | 显示击球数、最快球速等 | 中等 |
| 🔥 **连击奖励** | 连续对打次数越多，球速加成越高 | 简单 |

---

## 15. 总结

这款游戏的魅力在于 **化繁为简**：

```
用一张 AI 生成的高清球桌图 → 省去所有桌面绘制代码
用俯视视角 → 双方同屏竞技，简单直观
用小球拍 2D 移动 → 上手容易，深度足够
```

**对比旧版（分屏伪3D）vs 新版（俯视单屏）：**

| 维度 | 旧版（分屏） | 新版（俯视+背景图） |
|------|------------|------------------|
| 屏幕 | 左右分屏 | 单屏同框 |
| 坐标 | 3D 透视投影 | 2D 像素坐标 |
| 背景绘制 | 代码绘制桌面+网格 | AI 图片直接加载 |
| 复杂度 | 较高（需3D→2D投影） | 低（2D 物理直接渲染） |
| 视觉观感 | 程序化风格 | 写实风格（AI图） |
| 上手难度 | 需适应分屏视角 | 一目了然 |

> **预计代码量**：400 ~ 800 行 Python（比原版少约 30%）  
> **适合人群**：Pygame 初学者 ~ 中级  
> **开发周期**：2 ~ 4 天
