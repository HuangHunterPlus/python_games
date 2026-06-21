import random
import pygame


class Splash:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-1.5, 1.5)
        self.vy = random.uniform(-3.5, -0.8)
        self.life = random.uniform(0.4, 1.2)
        self.mx = self.life
        self.r = random.randint(2, 5)

    def update(self, dt):
        self.x += self.vx * 60 * dt
        self.y += self.vy * 60 * dt
        self.life -= dt

    @property
    def alive(self):
        return self.life > 0

    def draw(self, surf):
        a = int(200 * self.life / self.mx)
        c = (200, 220, 255)
        pygame.draw.circle(surf, c, (int(self.x), int(self.y)), self.r)
