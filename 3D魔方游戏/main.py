import pygame
import math

WIDTH, HEIGHT = 900, 600
CUBE_SIZE = 60
GAP = 2
BACKGROUND_COLOR = (0, 0, 0)

COLORS = {
    'front': (255, 0, 0),
    'back': (255, 140, 0),
    'left': (0, 255, 0),
    'right': (0, 0, 255),
    'top': (255, 255, 255),
    'bottom': (255, 255, 0)
}

class Point3D:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

def rotate_x(point, angle):
    rad = math.radians(angle)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    new_y = point.y * cos_a - point.z * sin_a
    new_z = point.y * sin_a + point.z * cos_a
    return Point3D(point.x, new_y, new_z)

def rotate_y(point, angle):
    rad = math.radians(angle)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    new_x = point.x * cos_a + point.z * sin_a
    new_z = -point.x * sin_a + point.z * cos_a
    return Point3D(new_x, point.y, new_z)

def rotate_z(point, angle):
    rad = math.radians(angle)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    new_x = point.x * cos_a - point.y * sin_a
    new_y = point.x * sin_a + point.y * cos_a
    return Point3D(new_x, new_y, point.z)

def project(point, scale=1):
    fov = 400
    distance = 400
    factor = fov / (distance + point.z) * scale
    x = point.x * factor + WIDTH // 2
    y = point.y * factor + HEIGHT // 2
    return (int(x), int(y))

class Cubelet:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.size = CUBE_SIZE
        self.colors = {
            'front': COLORS['front'],
            'back': COLORS['back'],
            'left': COLORS['left'],
            'right': COLORS['right'],
            'top': COLORS['top'],
            'bottom': COLORS['bottom']
        }
        self.visible = {
            'front': True,
            'back': True,
            'left': True,
            'right': True,
            'top': True,
            'bottom': True
        }

    def get_vertices(self):
        half = self.size / 2
        return [
            Point3D(self.x - half, self.y - half, self.z - half),
            Point3D(self.x + half, self.y - half, self.z - half),
            Point3D(self.x + half, self.y + half, self.z - half),
            Point3D(self.x - half, self.y + half, self.z - half),
            Point3D(self.x - half, self.y - half, self.z + half),
            Point3D(self.x + half, self.y - half, self.z + half),
            Point3D(self.x + half, self.y + half, self.z + half),
            Point3D(self.x - half, self.y + half, self.z + half)
        ]

    def get_faces(self, vertices):
        return [
            {'name': 'front', 'indices': [4, 5, 6, 7], 'color': self.colors['front'], 'visible': self.visible['front']},
            {'name': 'back', 'indices': [1, 0, 3, 2], 'color': self.colors['back'], 'visible': self.visible['back']},
            {'name': 'left', 'indices': [0, 4, 7, 3], 'color': self.colors['left'], 'visible': self.visible['left']},
            {'name': 'right', 'indices': [5, 1, 2, 6], 'color': self.colors['right'], 'visible': self.visible['right']},
            {'name': 'top', 'indices': [0, 1, 5, 4], 'color': self.colors['top'], 'visible': self.visible['top']},
            {'name': 'bottom', 'indices': [3, 7, 6, 2], 'color': self.colors['bottom'], 'visible': self.visible['bottom']}
        ]

class RubiksCube:
    def __init__(self):
        self.cubelets = []
        offset = CUBE_SIZE + GAP
        for x in range(-1, 2):
            for y in range(-1, 2):
                for z in range(-1, 2):
                    cubelet = Cubelet(x * offset, y * offset, z * offset)
                    self.cubelets.append(cubelet)
        
        self.rotation_x = -30
        self.rotation_y = 45
        self.rotation_z = 0
        
        self.animating = False
        self.animation_angle = 0
        self.animation_target = 0
        self.animation_axis = None
        self.animation_layer = 0
        self.animation_direction = 1
        self.animation_speed = 8
        
        self.update_visibility()

    def update_visibility(self):
        for cubelet in self.cubelets:
            cubelet.visible['front'] = cubelet.z > 0
            cubelet.visible['back'] = cubelet.z < 0
            cubelet.visible['left'] = cubelet.x < 0
            cubelet.visible['right'] = cubelet.x > 0
            cubelet.visible['top'] = cubelet.y < 0
            cubelet.visible['bottom'] = cubelet.y > 0

    def rotate_view(self, dx, dy):
        if not self.animating:
            self.rotation_y += dx * 0.5
            self.rotation_x += dy * 0.5

    def get_cubelet_at(self, x, y, z):
        offset = CUBE_SIZE + GAP
        for cubelet in self.cubelets:
            if abs(cubelet.x - x * offset) < 1 and abs(cubelet.y - y * offset) < 1 and abs(cubelet.z - z * offset) < 1:
                return cubelet
        return None

    def get_layer_cubelets(self, axis, layer):
        offset = CUBE_SIZE + GAP
        layer_value = layer * offset
        return [c for c in self.cubelets if abs(getattr(c, axis) - layer_value) < 1]

    def start_layer_rotation(self, axis, layer, direction):
        self.animating = True
        self.animation_axis = axis
        self.animation_layer = layer
        self.animation_direction = direction
        self.animation_angle = 0
        self.animation_target = 90

    def update_animation(self):
        if self.animating:
            self.animation_angle += self.animation_speed * self.animation_direction
            if abs(self.animation_angle) >= abs(self.animation_target):
                self.animation_angle = 0
                self.apply_layer_rotation()
                self.animating = False
                return True
        return False

    def apply_layer_rotation(self):
        offset = CUBE_SIZE + GAP
        layer_value = self.animation_layer * offset
        axis = self.animation_axis
        direction = 1 if self.animation_direction > 0 else -1
        
        for cubelet in self.cubelets[:]:
            if abs(getattr(cubelet, axis) - layer_value) < 1:
                if axis == 'x':
                    new_y = cubelet.z * direction
                    new_z = -cubelet.y * direction
                    cubelet.y = new_y
                    cubelet.z = new_z
                    
                    temp_front = cubelet.colors['front']
                    temp_back = cubelet.colors['back']
                    cubelet.colors['front'] = cubelet.colors['top'] if direction == 1 else cubelet.colors['bottom']
                    cubelet.colors['back'] = cubelet.colors['bottom'] if direction == 1 else cubelet.colors['top']
                    cubelet.colors['top'] = temp_back if direction == 1 else temp_front
                    cubelet.colors['bottom'] = temp_front if direction == 1 else temp_back
                elif axis == 'y':
                    new_x = cubelet.z * direction
                    new_z = -cubelet.x * direction
                    cubelet.x = new_x
                    cubelet.z = new_z
                    
                    temp_front = cubelet.colors['front']
                    temp_back = cubelet.colors['back']
                    cubelet.colors['front'] = cubelet.colors['right'] if direction == 1 else cubelet.colors['left']
                    cubelet.colors['back'] = cubelet.colors['left'] if direction == 1 else cubelet.colors['right']
                    cubelet.colors['left'] = temp_front if direction == 1 else temp_back
                    cubelet.colors['right'] = temp_back if direction == 1 else temp_front
                elif axis == 'z':
                    new_x = -cubelet.y * direction
                    new_y = cubelet.x * direction
                    cubelet.x = new_x
                    cubelet.y = new_y
                    
                    temp_left = cubelet.colors['left']
                    temp_right = cubelet.colors['right']
                    cubelet.colors['left'] = cubelet.colors['top'] if direction == 1 else cubelet.colors['bottom']
                    cubelet.colors['right'] = cubelet.colors['bottom'] if direction == 1 else cubelet.colors['top']
                    cubelet.colors['top'] = temp_right if direction == 1 else temp_left
                    cubelet.colors['bottom'] = temp_left if direction == 1 else temp_right
        
        self.update_visibility()

    def rotate_cubelet_point(self, point, axis, angle):
        rad = math.radians(angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        
        if axis == 'x':
            new_y = point.y * cos_a - point.z * sin_a
            new_z = point.y * sin_a + point.z * cos_a
            return Point3D(point.x, new_y, new_z)
        elif axis == 'y':
            new_x = point.x * cos_a + point.z * sin_a
            new_z = -point.x * sin_a + point.z * cos_a
            return Point3D(new_x, point.y, new_z)
        elif axis == 'z':
            new_x = point.x * cos_a - point.y * sin_a
            new_y = point.x * sin_a + point.y * cos_a
            return Point3D(new_x, new_y, point.z)

    def draw(self, surface):
        all_faces = []
        
        for cubelet in self.cubelets:
            vertices = cubelet.get_vertices()
            rotated_vertices = []
            
            offset = CUBE_SIZE + GAP
            layer_value = self.animation_layer * offset
            
            if self.animating and abs(getattr(cubelet, self.animation_axis) - layer_value) < 1:
                for v in vertices:
                    rotated = self.rotate_cubelet_point(v, self.animation_axis, self.animation_angle)
                    rotated_vertices.append(rotated)
            else:
                rotated_vertices = vertices
            
            for v in rotated_vertices:
                rotated = rotate_x(v, self.rotation_x)
                rotated = rotate_y(rotated, self.rotation_y)
                rotated = rotate_z(rotated, self.rotation_z)
                v.x, v.y, v.z = rotated.x, rotated.y, rotated.z
            
            faces = cubelet.get_faces(rotated_vertices)
            
            for face in faces:
                if face['visible']:
                    face_vertices = [rotated_vertices[i] for i in face['indices']]
                    center_z = sum(v.z for v in face_vertices) / 4
                    all_faces.append({
                        'vertices': face_vertices,
                        'color': face['color'],
                        'z': center_z
                    })
        
        all_faces.sort(key=lambda f: f['z'], reverse=True)
        
        for face in all_faces:
            points = [project(v, scale=1.5) for v in face['vertices']]
            pygame.draw.polygon(surface, face['color'], points)
            pygame.draw.polygon(surface, (0, 0, 0), points, 2)

    def is_solved(self):
        faces = {
            'front': [],
            'back': [],
            'left': [],
            'right': [],
            'top': [],
            'bottom': []
        }
        
        offset = CUBE_SIZE + GAP
        for cubelet in self.cubelets:
            if abs(cubelet.z - offset) < 1:
                faces['front'].append(cubelet.colors['front'])
            if abs(cubelet.z + offset) < 1:
                faces['back'].append(cubelet.colors['back'])
            if abs(cubelet.x + offset) < 1:
                faces['left'].append(cubelet.colors['left'])
            if abs(cubelet.x - offset) < 1:
                faces['right'].append(cubelet.colors['right'])
            if abs(cubelet.y + offset) < 1:
                faces['top'].append(cubelet.colors['top'])
            if abs(cubelet.y - offset) < 1:
                faces['bottom'].append(cubelet.colors['bottom'])
        
        for face_colors in faces.values():
            if len(face_colors) == 9:
                first_color = face_colors[0]
                if not all(c == first_color for c in face_colors):
                    return False
        return True

def point_in_polygon(point, polygon):
    x, y = point
    n = len(polygon)
    inside = False
    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def get_clicked_face(cube, mouse_pos):
    all_faces = []
    
    for cubelet in cube.cubelets:
        vertices = cubelet.get_vertices()
        rotated_vertices = []
        
        offset = CUBE_SIZE + GAP
        layer_value = cube.animation_layer * offset
        
        if cube.animating and abs(getattr(cubelet, cube.animation_axis) - layer_value) < 1:
            for v in vertices:
                rotated = cube.rotate_cubelet_point(v, cube.animation_axis, cube.animation_angle)
                rotated_vertices.append(rotated)
        else:
            rotated_vertices = vertices
        
        temp_vertices = []
        for v in rotated_vertices:
            rotated = rotate_x(v, cube.rotation_x)
            rotated = rotate_y(rotated, cube.rotation_y)
            rotated = rotate_z(rotated, cube.rotation_z)
            temp_vertices.append(rotated)
        
        faces = cubelet.get_faces(rotated_vertices)
        
        for face in faces:
            if face['visible']:
                face_vertices = [temp_vertices[i] for i in face['indices']]
                center_z = sum(v.z for v in face_vertices) / 4
                points = [project(v, scale=1.5) for v in face_vertices]
                all_faces.append({
                    'cubelet': cubelet,
                    'face': face,
                    'vertices': face_vertices,
                    'points': points,
                    'z': center_z
                })
    
    all_faces.sort(key=lambda f: f['z'], reverse=True)
    
    for face in all_faces:
        if point_in_polygon(mouse_pos, face['points']):
            return face
    
    return None

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("3D魔方游戏")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    
    cube = RubiksCube()
    
    dragging = False
    last_mouse_pos = (0, 0)
    cube_dragging = False
    
    clicked_face = None
    click_start_pos = (0, 0)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if not cube.animating:
                        clicked_face = get_clicked_face(cube, event.pos)
                        if clicked_face:
                            click_start_pos = event.pos
                        else:
                            cube_dragging = True
                            last_mouse_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    cube_dragging = False
                    clicked_face = None
            elif event.type == pygame.MOUSEMOTION:
                if cube_dragging and not cube.animating:
                    dx = event.pos[0] - last_mouse_pos[0]
                    dy = event.pos[1] - last_mouse_pos[1]
                    cube.rotate_view(dx, dy)
                    last_mouse_pos = event.pos
                elif clicked_face and not cube.animating:
                    dx = event.pos[0] - click_start_pos[0]
                    dy = event.pos[1] - click_start_pos[1]
                    
                    if abs(dx) > 10 or abs(dy) > 10:
                        cubelet = clicked_face['cubelet']
                        face_name = clicked_face['face']['name']
                        
                        offset = CUBE_SIZE + GAP
                        layer_x = round(cubelet.x / offset)
                        layer_y = round(cubelet.y / offset)
                        layer_z = round(cubelet.z / offset)
                        
                        if abs(dx) > abs(dy):
                            if face_name == 'front':
                                direction = 1 if dx > 0 else -1
                                cube.start_layer_rotation('y', layer_y, direction)
                            elif face_name == 'back':
                                direction = -1 if dx > 0 else 1
                                cube.start_layer_rotation('y', layer_y, direction)
                            elif face_name == 'left':
                                direction = 1 if dx > 0 else -1
                                cube.start_layer_rotation('z', layer_z, direction)
                            elif face_name == 'right':
                                direction = -1 if dx > 0 else 1
                                cube.start_layer_rotation('z', layer_z, direction)
                            elif face_name == 'top':
                                direction = -1 if dx > 0 else 1
                                cube.start_layer_rotation('y', layer_y, direction)
                            elif face_name == 'bottom':
                                direction = 1 if dx > 0 else -1
                                cube.start_layer_rotation('y', layer_y, direction)
                        else:
                            if face_name == 'front':
                                direction = -1 if dy > 0 else 1
                                cube.start_layer_rotation('x', layer_x, direction)
                            elif face_name == 'back':
                                direction = 1 if dy > 0 else -1
                                cube.start_layer_rotation('x', layer_x, direction)
                            elif face_name == 'left':
                                direction = -1 if dy > 0 else 1
                                cube.start_layer_rotation('x', layer_x, direction)
                            elif face_name == 'right':
                                direction = 1 if dy > 0 else -1
                                cube.start_layer_rotation('x', layer_x, direction)
                            elif face_name == 'top':
                                direction = 1 if dy > 0 else -1
                                cube.start_layer_rotation('x', layer_x, direction)
                            elif face_name == 'bottom':
                                direction = -1 if dy > 0 else 1
                                cube.start_layer_rotation('x', layer_x, direction)
                        
                        clicked_face = None
        
        cube.update_animation()
        
        screen.fill(BACKGROUND_COLOR)
        cube.draw(screen)
        
        if cube.is_solved():
            text = font.render("魔方已还原！", True, (0, 255, 0))
            text_rect = text.get_rect(center=(WIDTH // 2, 50))
            screen.blit(text, text_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()
