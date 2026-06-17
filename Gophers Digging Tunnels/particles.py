import random
import math
import pygame


class Particle:
    def __init__(self, x, y, color, velocity, lifetime, size=3):
        self.x = x
        self.y = y
        self.color = color
        self.vx, self.vy = velocity
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.alive = True

    def update(self, dt):
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        self.vy += 200 * dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False

    def draw(self, screen):
        alpha = max(0, min(255, int(255 * self.lifetime / self.max_lifetime)))
        size = max(1, int(self.size * self.lifetime / self.max_lifetime))
        color = self.color
        surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*color, alpha), (size, size), size)
        screen.blit(surf, (int(self.x - size), int(self.y - size)))


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit_dig(self, x, y, count=8):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(40, 120)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 60
            lifetime = random.uniform(0.3, 0.7)
            color = random.choice([
                (140, 100, 60), (160, 120, 70), (120, 80, 40), (100, 70, 30)
            ])
            size = random.uniform(2, 5)
            self.particles.append(Particle(x, y, color, (vx, vy), lifetime, size))

    def emit_coin(self, x, y, color, count=10):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(80, 200)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 100
            lifetime = random.uniform(0.4, 0.9)
            size = random.uniform(2, 4)
            self.particles.append(Particle(x, y, color, (vx, vy), lifetime, size))

    def emit_explosion(self, x, y, count=25):
        colors = [(255, 100, 30), (255, 180, 50), (255, 60, 30), (255, 220, 80)]
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(100, 300)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            lifetime = random.uniform(0.3, 0.8)
            size = random.uniform(3, 7)
            color = random.choice(colors)
            self.particles.append(Particle(x, y, color, (vx, vy), lifetime, size))

    def emit_damage(self, x, y, count=15):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(60, 150)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 50
            lifetime = random.uniform(0.3, 0.6)
            size = random.uniform(2, 5)
            self.particles.append(Particle(x, y, (220, 50, 50), (vx, vy), lifetime, size))

    def emit_heal(self, x, y, count=10):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(50, 120)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 80
            lifetime = random.uniform(0.5, 1.0)
            size = random.uniform(2, 4)
            self.particles.append(Particle(x, y, (100, 255, 100), (vx, vy), lifetime, size))

    def emit_boss(self, x, y, count=40):
        colors = [(255, 30, 30), (180, 20, 20), (255, 100, 50), (255, 180, 20)]
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(150, 400)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            lifetime = random.uniform(0.5, 1.5)
            size = random.uniform(3, 8)
            color = random.choice(colors)
            self.particles.append(Particle(x, y, color, (vx, vy), lifetime, size))

    def emit_combo(self, x, y, combo):
        count = min(20, 5 + combo)
        c = int(min(255, 100 + combo * 20))
        color = (255, 255 - c, 50)
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(60, 150)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 120
            lifetime = random.uniform(0.4, 1.0)
            size = random.uniform(2, 5)
            self.particles.append(Particle(x, y, color, (vx, vy), lifetime, size))

    def update(self, dt):
        for p in self.particles[:]:
            p.update(dt)
            if not p.alive:
                self.particles.remove(p)

    def draw(self, screen):
        for p in self.particles:
            p.draw(screen)
