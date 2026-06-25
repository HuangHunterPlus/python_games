---
title: 从零实现 AI 桌面宠物：Q-Learning + Char-RNN + 矢量精灵完整架构解析
date: 2026-06-25
tags: [Python, AI, Q-Learning, RNN, 桌面应用, PyQt5]
---

## 前言

桌面宠物这个概念并不新鲜——从早年的《电子宠物机》到《桌面宠物》Flash 游戏，陪伴了一代人的童年。但如果你的宠物**能自主学习你的习惯、拥有独立的性格和记忆、甚至能用微型神经网络和你对话**呢？

本文从一个完全离线、零 API 调用、纯 Python 实现的 AI 桌面宠物项目出发，逐层拆解它的技术架构：行为决策、性格建模、记忆系统、对话引擎、矢量渲染，以及桌面集成方案。代码总计约 2200 行，全部开源可用。

---

## 一、整体架构

整个宠物被设计为 **AI 大脑 + 渲染层 + 桌面窗口** 三层结构，数据流如下：

```
用户互动 → 性格系统 → 行为引擎 → 动作输出
                  ↘ 记忆系统 ↗
对话 ← 混合引擎（模板 + Char-RNN）
```

| 模块 | 文件 | 职责 | 技术选型 |
|------|------|------|----------|
| 大脑主控 | `pet/brain.py` | 协调所有子系统、属性衰减、交互分发 | - |
| 行为引擎 | `pet/behavior.py` | 自主决策（吃/睡/玩/探索…） | Q-Learning |
| 性格系统 | `pet/personality.py` | 5 维性格建模 | 向量 + 日限变化 |
| 记忆系统 | `pet/memory.py` | 时间衰减记忆 | 指数半衰期 |
| 对话引擎 | `pet/dialogue.py` | 宠物说话 | 模板 80% + RNN 20% |
| Char-RNN | `brain_models/char_rnn.py` | 对话生成 | 单层 RNN ~28K 参数 |
| 训练脚本 | `brain_models/train.py` | RNN 离线训练 | BPTT, NumPy 手写 |
| 矢量渲染 | `renderer/sprites.py` | 像素风宠物绘制 | Pygame 图元 |
| 帧动画 | `renderer/renderer.py` | 动画 + 特效叠加 | Pygame + SRCALPHA |
| 桌面窗口 | `desktop/pet_window.py` | 透明穿透窗口 | PyQt5 |
| 系统托盘 | `desktop/tray.py` | 托盘菜单 | PyQt5 |

### 属性系统

宠物有四个核心属性，每秒随 δt 衰减：

| 属性 | 范围 | 衰减速率/秒 | 说明 |
|------|------|-------------|------|
| 饥饿 | 0-100 | +0.02/60 | 越高越饿 |
| 精力 | 0-100 | -0.015/60 | 越低越累 |
| 心情 | 0-100 | -0.01/60 | 影响行为权重 |
| 健康 | 0-100 | -0.005/60 | 饥饿>80 或精力<20 时翻倍 |

属性在 tick（~1 秒/次）中自动更新，使用 `dt` 确保帧率稳定，不会因为掉帧而加速衰减。

---

## 二、行为引擎：Q-Learning

行为引擎是宠物的"决策大脑"，用来决定**无人互动时宠物应该自主做什么**。

### 状态空间

状态用 5 个维度表示，每个维度离散化为 3 级：

```python
(饥饿等级, 精力等级, 心情等级, 健康等级, 时间段)
```

时间段分为：凌晨（0-7）、白天（8-17）、夜晚（18-23）。

总计 `3^5 = 243` 个状态，每个状态对应 7 个可选动作。

### 动作空间

| 动作 | 触发条件偏好 | 效果 |
|------|-------------|------|
| `sleep` | 精力 < 40 | 精力 +10 |
| `eat` | 饥饿 > 50 | 饥饿 -15 |
| `explore` | 精力 > 50 | 心情 +5 |
| `play` | 精力 > 40 | 精力 -10, 心情 +8 |
| `cuddle` | 心情 < 60 | 心情 +5 |
| `wander` | 通用 | 心情 +3 |
| `groom` | 健康 < 50 | 健康 +3 |

### Reward 设计

Reward 不是简单的是非判断，而是**属性状态 + 性格权重**的组合：

```python
if action == "play":
    reward += 1.0 if energy > 40 else -1.0
    reward += 0.5 if mood < 50 else 0.2
    reward += personality.get("energetic") * 0.5
    reward += personality.get("curious") * 0.3
```

这种设计的精妙之处在于：活泼型（energetic 高）的宠物玩耍会获得更高 reward，从而强化"爱玩"的行为模式，形成性格与行为的正反馈循环。

### Q-Learning 更新公式

标准的 **时序差分学习（TD Learning）**：

```python
new_q = current_q + lr * (reward + gamma * max_next_q - current_q)
```

- 学习率 `lr = 0.1`
- 折扣因子 `gamma = 0.9`
- 探索率从 `0.2` 开始，每步乘以 `0.9995`，最小 `0.05`

### 性格影响行为

性格不仅影响 reward，还影响"每日人格变化上限"（`PERSONALITY_MAX_DAILY = 0.1`）：

| 互动 | 性格变化 |
|------|---------|
| 抚摸 | 亲昵↑ +0.02, 粘人↑ +0.01 |
| 玩耍 | 活跃↑ +0.02, 好奇↑ +0.01 |
| 喂食 | 亲昵↑ +0.02 |
| 责骂 | 亲昵↓ -0.03, 固执↑ +0.02 |

每天每个维度的变化量不超过 ±0.1，防止一次极端操作彻底改变宠物性格。

---

## 三、记忆系统：指数衰减

记忆系统使用**二指数半衰期**模型，半衰期 7 天：

```python
def _weight(self, timestamp):
    days = (time.time() - timestamp) / 86400
    return 2.0 ** (-days / MEMORY_HALF_LIFE_DAYS)
```

- **1 天后**：权重 0.91
- **7 天后**：权重 0.50
- **14 天后**：权重 0.25
- **30 天后**：权重 0.05

当权重低于 0.05 且互动次数 < 3 时，记忆自动清理。这模拟了"不常提起的事就会慢慢忘记"的机制。

记忆还会影响对话内容——如果宠物记得"你上次喂我鸡肉"，对话中就可能提到它。

---

## 四、混合对话引擎

对话采用 **80% 模板 + 20% RNN** 的混合策略：

### 模板系统

覆盖 10 种情绪：`happy / sad / hungry / sleepy / playful / curious / grateful / loving / excited / cuddly`

每种情绪 8 条中文模板，支持 `{name}` 变量替换：

```python
"happy": [
    "我好开心！{name}你真好~",
    "今天真是美好的一天！",
    "嘿嘿，我好快乐！",
    # ...
]
```

### Char-RNN 自由生成

当 RNN 权重已加载且随机数落在 20% 概率内时，会调用 RNN 生成对话：

```python
seed = f"<{emotion}>"
generated = rnn.sample(seed, length=25)
```

这保证了宠物的话**大部分时候通顺合理**，偶尔又有**意想不到的惊喜**。

---

## 五、微型 Char-RNN：28K 参数的纯 NumPy 实现

这是整个项目最硬核的部分——**完全不依赖 PyTorch/TensorFlow**，只用 NumPy 手写 RNN 的前向、反向传播和训练。

### 模型架构

```
Embedding(70→16) → RNN(16→64) → Linear(64→70)
```

| 参数 | 值 | 说明 |
|------|-----|------|
| 词表大小 | 70 | 大小写字母 + 数字 + 标点 |
| Embedding 维度 | 16 | 字符向量化 |
| 隐藏层维度 | 64 | RNN 记忆容量 |
| 参数量 | ~28K | 极小，适合纯 CPU 推理 |
| 权重文件 | ~112KB | `weights.npz` |

### 手写 BPTT

反向传播通过时间（BPTT）完全手动实现，核心代码只有 30 行：

```python
for t in reversed(range(T)):
    dy = probs[t:t+1].copy()
    dy[0, targets[t]] -= 1
    ht_2d = hs[t+1:t+2]
    h_2d = hs[t:t+1]
    dW_hy += ht_2d.T @ dy
    db_y += dy
    dh = dy @ self.W_hy.T + dh_next
    dh_raw = (1 - ht_2d ** 2) * dh
    # ... 梯度累积
```

梯度裁剪到 [-5, 5] 防止爆炸，学习率线性衰减。

### 训练方式

语料库使用 `<happy>`, `<sad>` 等情绪标签包裹的短句：

```
<start> 我好开心呀！<end>
<start> 今天天气真好，我们去玩吧！<end>
<happy> 心情真好！<end>
```

首次启动自动训练 200 个 epoch（约 30 秒），loss 从 ~3.1 降至 ~0.59。

训练完成后生成示例：

```
[train] 1/60 loss=3.10   cdefghijklmnopq
[train] 20/60 loss=1.24  <happy>我好开心
[train] 40/60 loss=0.84  <happy>我好想和你
[train] 60/60 loss=0.59  <happy>我好想和你一起玩！
```

---

## 六、矢量精灵渲染（零图片资源）

所有宠物形象完全由代码绘制——用 Pygame 的椭圆、圆、多边形、弧线、抗锯齿线组合而成。**不需要任何外部图片或精灵表。**

### 绘制分解

以猫为例，一个角色的绘制分 10 个层次：

```python
# 1. 尾巴       — 抗锯齿曲线 + 圆形尾尖
# 2. 身体       — 椭圆 + 肚子（浅色椭圆）
# 3. 后腿       — 两个椭圆（可交替抬起实现踢腿）
# 4. 前腿       — 椭圆（可抬起挥手/伸长）
# 5. 头部       — 大圆（Q 版大头）
# 6. 耳朵       — 两个多边形（内外两层）
# 7. 眼睛       — 椭圆的白色眼白 + 金色虹膜 + 黑色瞳孔 + 高光
# 8. 腮红       — 半透明椭圆（SRCALPHA）
# 9. 鼻子/嘴巴  — 小三角形 + 圆弧（微笑/难过/张嘴）
# 10. 胡须      — 抗锯齿直线
```

### 11 种情绪动画

每个情绪由一组 **modifier 参数**控制，本质上是一个参数化 IK（反向运动学）系统：

```python
# sleepy 状态
modifiers = {
    "eye_open": 0.1,        # 半闭眼
    "head_tilt": 0,         # 不歪头
    "bounce_y": 0,          # 不弹跳
    "smile": 0.3,           # 微小微笑
    "breathe": breath_val,  # 缓慢呼吸
}
```

| 情绪 | 帧数 | 关键动画 | 参数变化 |
|------|------|----------|---------|
| idle | 2 | 呼吸起伏 | sin 波驱动 body 垂直微动 |
| happy | 3 | 上下弹跳 | `bounce_y = abs(sin(frame*0.5))*6` |
| sad | 2 | 垂头丧气 | `head_tilt` 负值 + 半闭眼 |
| playful | 3 | 活泼好动 | 高弹跳 + 尾巴竖起 + 踢腿 |
| hungry | 2 | 左右张望 | `head_tilt` 正弦摆动 + 张嘴 |
| sleepy | 2 | 打瞌睡 | `eye_open=0.1` + 缓慢点头 |
| sick | 2 | 生病萎靡 | `body_color` 换为灰白色 |
| curious | 2 | 好奇歪头 | `head_tilt` 摆动 + 睁大眼 |
| excited | 3 | 兴奋蹦跳 | 高弹跳 + 举双爪 + 快速踢腿 |
| cuddly | 2 | 撒娇求抱 | 倾斜歪头 + 伸爪 + 腮红 |
| dance | 3 | 左右摇摆 | 交替抬爪 + 左右 sway |

### 9 种视觉特效

每个互动操作触发对应的叠加特效，使用粒子和动画系统：

```python
def _set_overlay(self, overlay_type: str, duration: int = None):
    # "heart", "food", "gift", "toy", "star", "bubble", "book", "anger", "sparkle"
    # 持续约 2-3 秒 (FPS * 2)
```

特效绘制在单独的支持 alpha 的 surface 上，与宠物 surface 叠加合成，再用 `blit` 输出到窗口。

### 多宠物支持

通过配置字典，5 种动物共享同一套绘制逻辑，仅颜色参数不同：

```python
ANIMAL_CONFIGS = {
    "cat":     {"name": "橘猫", "body": (255,159,67), "ear": (255,138,128), ...},
    "dog":     {"name": "柴犬", "body": (220,180,140), "ear": (200,160,120), ...},
    "rabbit":  {"name": "白兔", "body": (245,240,235), "ear": (255,200,210), ...},
    "hamster": {"name": "仓鼠", "body": (235,195,140), "ear": (245,200,170), ...},
    "fox":     {"name": "赤狐", "body": (255,130,50),  "ear": (255,200,150), ...},
}
```

---

## 七、桌面集成：PyQt5 透明窗口

### 窗口技术

桌面窗口使用 PyQt5 实现，核心配置：

```python
WINDOW_FLAGS = {
    "frameless": True,
    "topmost": True,
    "transparent": True,
    "skip_taskbar": True,
    "show_without_activating": True,
}
```

关键窗口特性：
- `WA_TranslucentBackground` — 透明背景
- `WindowStaysOnTopHint` — 置顶显示
- `FramelessWindowHint` — 无边框无标题栏
- `WS_EX_TOOLWINDOW`（Windows API）— 隐藏任务栏条目
- `WA_ShowWithoutActivating` — 不窃取焦点

### Pygame 嵌入

Pygame 渲染到 `QWidget` 上，通过 `QWindow.fromWinId()` 嵌入：

```
PyQt5 窗口 (透明) → Pygame Surface (宠物绘制) → 每一帧 blit 到 QWidget
```

窗口尺寸 200×280，宠物 128×128 居中，下方显示对话气泡。

### 交互方式

| 操作 | 效果 |
|------|------|
| **左键单击** 宠物 | 随机互动，宠物切换对应表情 |
| **左键长按拖拽** | 移动宠物位置 |
| **右键单击** 宠物 | 弹出操作菜单（打招呼/摸摸头/喂食/玩耍/改名/退出等 15 项） |

### 系统托盘

托盘图标也由代码绘制（像素猫头），支持左键置顶、双击互动、右键菜单。

---

## 八、商店系统与数据持久化

### 金币经济

每次互动获得金币（1-3 枚），可用于购买新宠物：

```python
COIN_REWARDS = {
    "pet": 2, "feed": 3, "play": 3, "heal": 2,
    "bathe": 3, "praise": 2, "story": 2, "teach": 3, "dance": 3,
}
```

| 宠物 | 价格 | 说明 |
|------|------|------|
| 橘猫 | 0 | 默认 |
| 柴犬 | 100 | 活泼忠诚 |
| 白兔 | 150 | 温顺可爱 |
| 仓鼠 | 200 | 圆滚滚 |
| 赤狐 | 300 | 机灵优雅 |

切换宠物时，当前宠物的**记忆、性格、Q 表、状态**全部保存，新宠物独立加载——每个动物拥有独立的"人格"。

### 数据持久化

所有数据以 JSON / NPZ 格式保存在 `brain_models/data/` 目录：

| 文件 | 内容 |
|------|------|
| `brain_state.json` | 属性状态 + 名字 |
| `q_table.json` | Q-Learning 表格 + 探索率 |
| `memory.json` | 记忆数据 |
| `personality.json` | 性格向量 |
| `weights.npz` | Char-RNN 权重 |
| `corpus.txt` | RNN 训练语料 |
| `shop.json` | 商店数据 |

---

## 九、技术栈总结

| 组件 | 技术 | 用途 |
|------|------|------|
| 游戏循环 / 渲染 | pygame-ce | 帧动画、矢量渲染、叠加特效 |
| 桌面窗口 | PyQt5 | 透明窗口、系统托盘、事件处理 |
| 神经网络 | NumPy | Char-RNN 训练与推理（零深度学习框架依赖） |
| 行为决策 | Q-Learning | 243 状态 × 7 动作的价值学习 |
| 窗口管理 | ctypes (Windows API) | 隐藏任务栏条目 |

### 为什么选择纯 NumPy 实现 RNN？

1. **零依赖部署** — 不需要安装 PyTorch（~800MB）或 TensorFlow（~1GB），仅 NumPy（~20MB）
2. **完全离线** — 不需要下载预训练模型，首次启动 30 秒本地训练
3. **教育意义** — 手动实现 BPTT 让开发者深入理解 RNN 原理
4. **够用** — 28K 参数足以生成合理的短句回复

---

## 十、可能的改进方向

1. **自定义精灵编辑器** — 可视化调整宠物外观
2. **更多互动游戏** — 接球、拼图等小游戏
3. **音效系统** — 互动触发音效
4. **跨平台支持** — 目前依赖 Windows API 隐藏任务栏
5. **对话模型升级** — 用更小的 Transformer（如 NanoGPT）替代 RNN
6. **多宠物同屏** — 同时养多只宠物，它们之间也能互动

---

## 结语

这个项目最有趣的地方在于：**它把所有东西都做得很简单，但组合起来效果却很生动**。Q-Learning 只有 243 个状态，Char-RNN 只有 28K 参数，精灵用 Pygame 椭圆拼接——每一个模块单独看都不复杂，但当属性衰减、性格变化、记忆权重、Q 表更新、对话生成这些系统同时运行时，宠物就真的有了"活着"的感觉。

项目完全开源，代码约 2200 行，适合想做桌面应用 + AI 结合但又不想引入庞大依赖的开发者参考。

---

*项目地址：[GitHub]（暂未公开）*
*技术栈：Python 3.10+ / PyQt5 / pygame-ce / NumPy*
