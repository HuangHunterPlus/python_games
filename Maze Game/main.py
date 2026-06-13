import pygame
import sys
import random

# 初始化pygame
pygame.init()

# 游戏设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CELL_SIZE = 40
FPS = 30

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# 创建屏幕
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Maze Adventure")

# 时钟
clock = pygame.time.Clock()

# 字体
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)

# 关卡数据
class Level:
    def __init__(self, level_num):
        self.level_num = level_num
        # 随着关卡增加，迷宫变大且更复杂
        self.width = 15 + (level_num // 3) * 5  # 增加宽度增长速度
        self.height = 10 + (level_num // 3) * 4  # 增加高度增长速度
        # 随机选择出口位置，可以在中间或角落
        if random.random() < 0.7:  # 70%概率在中间
            self.exit_pos = (random.randint(3, self.width - 4), random.randint(3, self.height - 4))
        else:  # 30%概率在角落
            self.exit_pos = (self.width - 2, self.height - 2)
        self.grid = self.generate_maze()
        self.player_pos = (1, 1)
        
    def generate_maze(self):
        # 使用改进的Prim算法生成连通的迷宫
        grid = [[1 for _ in range(self.width)] for _ in range(self.height)]
        stack = []
        
        # 起点
        start_x, start_y = 1, 1
        grid[start_y][start_x] = 0
        stack.append((start_x, start_y))
        
        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
        
        while stack:
            x, y = stack[-1]
            random.shuffle(directions)
            found = False
            
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 1 <= nx < self.width - 1 and 1 <= ny < self.height - 1 and grid[ny][nx] == 1:
                    grid[ny][nx] = 0
                    grid[y + dy//2][x + dx//2] = 0
                    stack.append((nx, ny))
                    found = True
                    break
            
            if not found:
                stack.pop()
        
        # 移除长直线路径，增加转弯
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if grid[y][x] == 0:
                    # 检查是否是长直线路径的一部分
                    horizontal = 0
                    vertical = 0
                    # 检查水平方向
                    for dx in range(-3, 4):
                        if 0 <= x + dx < self.width and grid[y][x + dx] == 0:
                            horizontal += 1
                        else:
                            break
                    # 检查垂直方向
                    for dy in range(-3, 4):
                        if 0 <= y + dy < self.height and grid[y + dy][x] == 0:
                            vertical += 1
                        else:
                            break
                    # 如果是长直线路径，随机添加墙壁
                    if horizontal >= 6 or vertical >= 6:
                        if random.random() < 0.3:  # 30%概率添加墙壁
                            # 检查周围是否有足够的通路
                            neighbors = 0
                            if grid[y-1][x] == 0:
                                neighbors += 1
                            if grid[y+1][x] == 0:
                                neighbors += 1
                            if grid[y][x-1] == 0:
                                neighbors += 1
                            if grid[y][x+1] == 0:
                                neighbors += 1
                            if neighbors >= 2:
                                grid[y][x] = 1
        
        # 确保出口是通路
        grid[self.height - 2][self.width - 2] = 0
        
        # 添加额外的墙壁增加难度，但不破坏连通性
        extra_walls = self.width * self.height // 15  # 增加墙壁数量
        for _ in range(extra_walls):
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            if (x, y) != (1, 1) and (x, y) != (self.width - 2, self.height - 2):
                # 检查周围至少有两个通路，避免孤立
                neighbors = 0
                if grid[y-1][x] == 0:
                    neighbors += 1
                if grid[y+1][x] == 0:
                    neighbors += 1
                if grid[y][x-1] == 0:
                    neighbors += 1
                if grid[y][x+1] == 0:
                    neighbors += 1
                if neighbors >= 2:
                    grid[y][x] = 1
        
        # 添加更多分支和死胡同
        dead_ends = self.width * self.height // 20
        for _ in range(dead_ends):
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            if grid[y][x] == 0:
                # 检查是否是通路且不是关键节点
                neighbors = 0
                if grid[y-1][x] == 0:
                    neighbors += 1
                if grid[y+1][x] == 0:
                    neighbors += 1
                if grid[y][x-1] == 0:
                    neighbors += 1
                if grid[y][x+1] == 0:
                    neighbors += 1
                if neighbors == 1:
                    # 扩展死胡同
                    nx, ny = x, y
                    for _ in range(random.randint(2, 5)):
                        # 随机方向
                        dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
                        random.shuffle(dirs)
                        for dx, dy in dirs:
                            new_x, new_y = nx + dx, ny + dy
                            if 1 <= new_x < self.width - 1 and 1 <= new_y < self.height - 1 and grid[new_y][new_x] == 1:
                                grid[new_y][new_x] = 0
                                nx, ny = new_x, new_y
                                break
                        else:
                            break
        
        # 确保出口是通路
        grid[self.exit_pos[1]][self.exit_pos[0]] = 0
        
        # 修复最外圈的通路问题
        # 确保最外圈只有起点是通路
        for x in range(self.width):
            grid[0][x] = 1
            grid[self.height - 1][x] = 1
        for y in range(self.height):
            grid[y][0] = 1
            grid[y][self.width - 1] = 1
        # 保留起点
        grid[start_y][start_x] = 0
        # 确保出口位置是通路
        grid[self.exit_pos[1]][self.exit_pos[0]] = 0
        
        # 验证并修复连通性
        max_attempts = 3
        attempt = 0
        while attempt < max_attempts and not self.is_connected(grid, (start_x, start_y), self.exit_pos):
            attempt += 1
            # 使用DFS找到一条从起点到终点的路径
            path = []
            visited = set()
            
            def dfs(x, y):
                if (x, y) == self.exit_pos:
                    path.append((x, y))
                    return True
                if (x, y) in visited:
                    return False
                visited.add((x, y))
                
                directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
                random.shuffle(directions)
                
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    if 1 <= nx < self.width - 1 and 1 <= ny < self.height - 1:  # 限制在内部区域
                        if grid[ny][nx] == 0 and dfs(nx, ny):
                            path.append((x, y))
                            return True
                return False
            
            if dfs(start_x, start_y):
                # 如果找到路径，确保路径畅通
                for x, y in path:
                    grid[y][x] = 0
            else:
                # 如果找不到路径，创建一条内部的折线通路
                x, y = start_x, start_y
                # 先随机移动一段距离
                for _ in range(random.randint(5, 10)):
                    dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
                    random.shuffle(dirs)
                    for dx, dy in dirs:
                        nx, ny = x + dx, y + dy
                        if 1 <= nx < self.width - 1 and 1 <= ny < self.height - 1:
                            grid[ny][nx] = 0
                            x, y = nx, ny
                            break
                # 然后向终点移动
                while abs(x - self.exit_pos[0]) > 0 or abs(y - self.exit_pos[1]) > 0:
                    if abs(x - self.exit_pos[0]) > 0:
                        x += 1 if self.exit_pos[0] > x else -1
                        grid[y][x] = 0
                    else:
                        y += 1 if self.exit_pos[1] > y else -1
                        grid[y][x] = 0
        
        # 添加多条备用路径
        if self.level_num >= 5:  # 从第5关开始添加多条路径
            for _ in range(random.randint(1, 3)):
                # 随机选择两个通路点
                path_points = []
                # 找到随机的通路点
                while len(path_points) < 2:
                    x = random.randint(1, self.width - 2)
                    y = random.randint(1, self.height - 2)
                    if grid[y][x] == 0:
                        path_points.append((x, y))
                
                # 打通这两个点之间的路径
                x1, y1 = path_points[0]
                x2, y2 = path_points[1]
                
                # 使用Bresenham算法画一条线
                dx = abs(x2 - x1)
                dy = abs(y2 - y1)
                sx = 1 if x1 < x2 else -1
                sy = 1 if y1 < y2 else -1
                err = dx - dy
                
                x, y = x1, y1
                while True:
                    grid[y][x] = 0
                    if x == x2 and y == y2:
                        break
                    e2 = 2 * err
                    if e2 > -dy:
                        err -= dy
                        x += sx
                    if e2 < dx:
                        err += dx
                        y += sy
        
        return grid
    
    def is_connected(self, grid, start, end):
        # 使用BFS检查连通性，改用deque提升性能
        from collections import deque
        visited = set()
        queue = deque([start])
        visited.add(start)
        
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        while queue:
            x, y = queue.popleft()
            
            if (x, y) == end:
                return True
            
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 1 <= nx < self.width -1 and 1 <= ny < self.height -1:
                    if grid[ny][nx] == 0 and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append((nx, ny))
        
        return False

# 玩家类
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = CELL_SIZE
        
    def draw(self, screen):
        # 绘制可爱的卡通角色
        # 身体
        pygame.draw.circle(screen, YELLOW, (self.x + CELL_SIZE//2, self.y + CELL_SIZE//2), CELL_SIZE//2 - 5)
        # 眼睛
        pygame.draw.circle(screen, BLACK, (self.x + CELL_SIZE//4, self.y + CELL_SIZE//3), 5)
        pygame.draw.circle(screen, BLACK, (self.x + 3*CELL_SIZE//4, self.y + CELL_SIZE//3), 5)
        # 嘴巴
        pygame.draw.arc(screen, BLACK, 
                       (self.x + CELL_SIZE//4, self.y + CELL_SIZE//3, 
                        CELL_SIZE//2, CELL_SIZE//3), 0, 3.14, 2)
        # 腮红
        pygame.draw.circle(screen, (255, 192, 203), (self.x + CELL_SIZE//5, self.y + CELL_SIZE//2), 4)
        pygame.draw.circle(screen, (255, 192, 203), (self.x + 4*CELL_SIZE//5, self.y + CELL_SIZE//2), 4)

# 游戏状态
class GameState:
    MENU = 0
    PLAYING = 1
    WIN = 2
    LOSE = 3
    
    def __init__(self):
        self.state = GameState.MENU
        self.current_level = 1
        self.levels = [Level(i) for i in range(1, 21)]
        self.timer = 60
        self.start_time = None
        self.button_clicked = None
        # 地图滚动偏移
        self.scroll_x = 0
        self.scroll_y = 0
        # 长按连续移动
        self.key_states = {}
        self.last_move_time = 0
        self.move_delay = 150

# 初始化游戏状态
game_state = GameState()

# 主菜单
def draw_menu():
    screen.fill(BLUE)
    
    # 标题
    title_text = large_font.render("Maze Adventure", True, YELLOW)
    screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 100))
    
    # 关卡选择 - 滚动版本
    scroll_area = pygame.Rect(150, 250, 520, 200)
    pygame.draw.rect(screen, WHITE, scroll_area, 2)
    
    # 计算可见关卡
    visible_levels = 5
    start_level = max(0, game_state.current_level - visible_levels // 2)
    end_level = min(20, start_level + visible_levels)
    
    # 绘制可见关卡
    for i in range(start_level, end_level):
        level_num = i + 1
        x = 160
        y = 260 + (i - start_level) * 35
        
        rect = pygame.Rect(x, y, 500, 30)
        color = GREEN if level_num == game_state.current_level else WHITE
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)
        
        level_text = font.render(f"Level {level_num}", True, BLACK)
        screen.blit(level_text, (x + 10, y + 5))
    
    # 滚动提示
    scroll_text = font.render("Use mouse wheel to scroll levels", True, WHITE)
    screen.blit(scroll_text, (SCREEN_WIDTH//2 - scroll_text.get_width()//2, 470))
    
    # 开始按钮
    start_rect = pygame.Rect(SCREEN_WIDTH//2 - 80, 500, 160, 50)
    pygame.draw.rect(screen, GREEN, start_rect)
    pygame.draw.rect(screen, BLACK, start_rect, 2)
    start_text = font.render("Start Game", True, BLACK)
    screen.blit(start_text, (SCREEN_WIDTH//2 - start_text.get_width()//2, 510))

# 绘制迷宫
def draw_maze(level):
    screen.fill(BLACK)
    
    # 绘制网格
    for y in range(level.height):
        for x in range(level.width):
            if level.grid[y][x] == 1:
                rect = pygame.Rect(x * CELL_SIZE - game_state.scroll_x, y * CELL_SIZE - game_state.scroll_y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, BLUE, rect)
    
    # 绘制出口
    exit_rect = pygame.Rect(level.exit_pos[0] * CELL_SIZE - game_state.scroll_x, level.exit_pos[1] * CELL_SIZE - game_state.scroll_y, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, GREEN, exit_rect)
    
    # 绘制玩家
    player = Player(level.player_pos[0], level.player_pos[1])
    # 调整玩家绘制位置以适应滚动
    original_x = player.x
    original_y = player.y
    player.x = original_x * CELL_SIZE - game_state.scroll_x
    player.y = original_y * CELL_SIZE - game_state.scroll_y
    player.draw(screen)
    
    # 计算地图滚动偏移，使角色保持在屏幕中央
    player_x = level.player_pos[0] * CELL_SIZE
    player_y = level.player_pos[1] * CELL_SIZE
    
    # 计算理想偏移，让角色居中
    ideal_scroll_x = player_x - SCREEN_WIDTH // 2
    ideal_scroll_y = player_y - SCREEN_HEIGHT // 2
    
    # 限制偏移范围，避免显示空白
    max_scroll_x = max(0, level.width * CELL_SIZE - SCREEN_WIDTH)
    max_scroll_y = max(0, level.height * CELL_SIZE - SCREEN_HEIGHT)
    
    game_state.scroll_x = max(0, min(ideal_scroll_x, max_scroll_x))
    game_state.scroll_y = max(0, min(ideal_scroll_y, max_scroll_y))
    
    # 绘制计时器
    timer_text = font.render(f"Time: {int(game_state.timer)}s", True, WHITE)
    screen.blit(timer_text, (10, 10))
    
    # 绘制关卡
    level_text = font.render(f"Level: {game_state.current_level}", True, WHITE)
    screen.blit(level_text, (SCREEN_WIDTH - 150, 10))
    
    # 绘制返回主界面按钮
    menu_button_rect = pygame.Rect(SCREEN_WIDTH - 150, 50, 140, 30)
    pygame.draw.rect(screen, YELLOW, menu_button_rect)
    pygame.draw.rect(screen, BLACK, menu_button_rect, 2)
    menu_button_text = font.render("Back to Menu", True, BLACK)
    screen.blit(menu_button_text, (SCREEN_WIDTH - 150 + 10, 55))

# 结算弹窗
def draw_result(is_win):
    # 半透明背景
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    if is_win:
        result_text = large_font.render("You Win!", True, GREEN)
    else:
        result_text = large_font.render("Time's Up!", True, RED)
    
    screen.blit(result_text, (SCREEN_WIDTH//2 - result_text.get_width()//2, 200))
    
    # 按钮 - 带点击效果
    restart_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 350, 140, 50)
    restart_color = (200, 200, 0) if game_state.button_clicked == 'restart' else YELLOW
    pygame.draw.rect(screen, restart_color, restart_rect)
    pygame.draw.rect(screen, BLACK, restart_rect, 2)
    restart_text = font.render("Restart", True, BLACK)
    screen.blit(restart_text, (SCREEN_WIDTH//2 - 150 + 30, 360))
    
    # 下一关按钮（仅胜利界面显示）
    if is_win:
        next_rect = pygame.Rect(SCREEN_WIDTH//2 + 10, 350, 140, 50)
        next_color = (200, 200, 0) if game_state.button_clicked == 'next' else GREEN
        pygame.draw.rect(screen, next_color, next_rect)
        pygame.draw.rect(screen, BLACK, next_rect, 2)
        next_text = font.render("Next Level", True, BLACK)
        screen.blit(next_text, (SCREEN_WIDTH//2 + 10 + 20, 360))
        
        # 返回主界面按钮
        menu_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 430, 200, 50)
        menu_color = (200, 200, 0) if game_state.button_clicked == 'menu' else YELLOW
        pygame.draw.rect(screen, menu_color, menu_rect)
        pygame.draw.rect(screen, BLACK, menu_rect, 2)
        menu_text = font.render("Back to Menu", True, BLACK)
        screen.blit(menu_text, (SCREEN_WIDTH//2 - menu_text.get_width()//2, 440))
    else:
        menu_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 430, 200, 50)
        menu_color = (200, 200, 0) if game_state.button_clicked == 'menu' else YELLOW
        pygame.draw.rect(screen, menu_color, menu_rect)
        pygame.draw.rect(screen, BLACK, menu_rect, 2)
        menu_text = font.render("Back to Menu", True, BLACK)
        screen.blit(menu_text, (SCREEN_WIDTH//2 - menu_text.get_width()//2, 440))

# 主游戏循环
running = True
while running:
    clock.tick(FPS)
    
    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state.state == GameState.MENU:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                # 检测关卡选择
                scroll_area = pygame.Rect(150, 250, 520, 200)
                if scroll_area.collidepoint(mouse_x, mouse_y):
                    # 计算点击的关卡
                    visible_levels = 5
                    start_level = max(0, game_state.current_level - visible_levels // 2)
                    for i in range(start_level, min(20, start_level + visible_levels)):
                        level_num = i + 1
                        x = 160
                        y = 260 + (i - start_level) * 35
                        rect = pygame.Rect(x, y, 500, 30)
                        if rect.collidepoint(mouse_x, mouse_y):
                            game_state.current_level = level_num
                            break
                
                # 检测开始按钮
                start_rect = pygame.Rect(SCREEN_WIDTH//2 - 80, 500, 160, 50)
                if start_rect.collidepoint(mouse_x, mouse_y):
                    game_state.state = GameState.PLAYING
                    game_state.start_time = pygame.time.get_ticks()
                    game_state.timer = 60
                    # 重置按键状态，防止长按连续移动在游戏开始后继续
                    game_state.key_states.clear()
            elif game_state.state in [GameState.WIN, GameState.LOSE]:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                # 重新开始
                restart_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 350, 140, 50)
                if restart_rect.collidepoint(mouse_x, mouse_y):
                    game_state.button_clicked = 'restart'
                    # 重新生成当前关卡的迷宫
                    game_state.levels[game_state.current_level - 1] = Level(game_state.current_level)
                    game_state.state = GameState.PLAYING
                    game_state.start_time = pygame.time.get_ticks()
                    game_state.timer = 60
                    # 重置按键状态，防止长按连续移动在重启后继续
                    game_state.key_states.clear()
                
                # 下一关（仅胜利界面）
                if game_state.state == GameState.WIN:
                    next_rect = pygame.Rect(SCREEN_WIDTH//2 + 10, 350, 140, 50)
                    if next_rect.collidepoint(mouse_x, mouse_y):
                        game_state.button_clicked = 'next'
                        # 进入下一关
                    if game_state.current_level < 20:
                        game_state.current_level += 1
                        game_state.state = GameState.PLAYING
                        game_state.start_time = pygame.time.get_ticks()
                        game_state.timer = 60
                        # 重置按键状态，防止长按连续移动在关卡切换后继续
                        game_state.key_states.clear()
                    else:
                        # 所有关卡通关
                        game_state.state = GameState.MENU
                    
                    # 返回主界面按钮（胜利界面）
                    menu_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 430, 200, 50)
                    if menu_rect.collidepoint(mouse_x, mouse_y):
                        game_state.button_clicked = 'menu'
                        game_state.state = GameState.MENU
                        # 重置按键状态，防止长按连续移动在返回菜单后继续
                        game_state.key_states.clear()
                else:
                    # 返回菜单（失败界面）
                    menu_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 430, 200, 50)
                    if menu_rect.collidepoint(mouse_x, mouse_y):
                        game_state.button_clicked = 'menu'
                        game_state.state = GameState.MENU
                        # 重置按键状态，防止长按连续移动在返回菜单后继续
                        game_state.key_states.clear()
            
        # 鼠标滚轮滚动关卡
        if event.type == pygame.MOUSEWHEEL:
            if game_state.state == GameState.MENU:
                if event.y > 0:
                    game_state.current_level = max(1, game_state.current_level - 1)
                else:
                    game_state.current_level = min(20, game_state.current_level + 1)
        
        # 重置按钮点击状态
        if event.type == pygame.MOUSEBUTTONUP:
            game_state.button_clicked = None
        
        if event.type == pygame.KEYDOWN:
            if game_state.state == GameState.PLAYING:
                game_state.key_states[event.key] = True
                current_level = game_state.levels[game_state.current_level - 1]
                x, y = current_level.player_pos
                
                if event.key == pygame.K_UP:
                    if y > 0 and current_level.grid[y - 1][x] == 0:
                        current_level.player_pos = (x, y - 1)
                        game_state.last_move_time = pygame.time.get_ticks()
                elif event.key == pygame.K_DOWN:
                    if y < current_level.height - 1 and current_level.grid[y + 1][x] == 0:
                        current_level.player_pos = (x, y + 1)
                        game_state.last_move_time = pygame.time.get_ticks()
                elif event.key == pygame.K_LEFT:
                    if x > 0 and current_level.grid[y][x - 1] == 0:
                        current_level.player_pos = (x - 1, y)
                        game_state.last_move_time = pygame.time.get_ticks()
                elif event.key == pygame.K_RIGHT:
                    if x < current_level.width - 1 and current_level.grid[y][x + 1] == 0:
                        current_level.player_pos = (x + 1, y)
                        game_state.last_move_time = pygame.time.get_ticks()
        
        if event.type == pygame.KEYUP:
            if game_state.state == GameState.PLAYING:
                game_state.key_states[event.key] = False
        
        # 游戏中返回主界面按钮点击
        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state.state == GameState.PLAYING:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                menu_button_rect = pygame.Rect(SCREEN_WIDTH - 150, 50, 140, 30)
                if menu_button_rect.collidepoint(mouse_x, mouse_y):
                    game_state.state = GameState.MENU
                    # 重置按键状态，防止长按连续移动在返回菜单后继续
                    game_state.key_states.clear()
    
    # 更新计时器 - 难度递增，关卡越高时间越短
    if game_state.state == GameState.PLAYING:
        elapsed_time = (pygame.time.get_ticks() - game_state.start_time) / 1000
        base_time = 60
        time_reduction = min(30, game_state.current_level * 2)
        game_state.timer = (base_time - time_reduction) - elapsed_time
        
        if game_state.timer <= 0:
            game_state.state = GameState.LOSE
        
        # 检查是否到达出口
        current_level = game_state.levels[game_state.current_level - 1]
        if current_level.player_pos == current_level.exit_pos:
            game_state.state = GameState.WIN
        
        # 长按连续移动
        current_time = pygame.time.get_ticks()
        if current_time - game_state.last_move_time > game_state.move_delay:
            for key in game_state.key_states:
                if game_state.key_states[key]:
                    x, y = current_level.player_pos
                    moved = False
                    
                    if key == pygame.K_UP:
                        if y > 0 and current_level.grid[y - 1][x] == 0:
                            current_level.player_pos = (x, y - 1)
                            moved = True
                    elif key == pygame.K_DOWN:
                        if y < current_level.height - 1 and current_level.grid[y + 1][x] == 0:
                            current_level.player_pos = (x, y + 1)
                            moved = True
                    elif key == pygame.K_LEFT:
                        if x > 0 and current_level.grid[y][x - 1] == 0:
                            current_level.player_pos = (x - 1, y)
                            moved = True
                    elif key == pygame.K_RIGHT:
                        if x < current_level.width - 1 and current_level.grid[y][x + 1] == 0:
                            current_level.player_pos = (x + 1, y)
                            moved = True
                    
                    if moved:
                        game_state.last_move_time = current_time
    
    # 绘制
    if game_state.state == GameState.MENU:
        draw_menu()
    elif game_state.state == GameState.PLAYING:
        draw_maze(game_state.levels[game_state.current_level - 1])
    elif game_state.state == GameState.WIN:
        draw_maze(game_state.levels[game_state.current_level - 1])
        draw_result(True)
    elif game_state.state == GameState.LOSE:
        draw_maze(game_state.levels[game_state.current_level - 1])
        draw_result(False)
    
    # 更新显示
    pygame.display.flip()

# 退出游戏
pygame.quit()
sys.exit()