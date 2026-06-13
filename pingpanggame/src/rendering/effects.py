"""
Particle effects — hit sparks, score bursts
"""

import math
import random
import pygame
from src.config import (
    PARTICLE_HIT_COUNT, PARTICLE_SCORE_COUNT, PARTICLE_LIFETIME,
    WHITE, GOLD,
)


class Particle:
    """Single particle."""

    def __init__(self, x: float, y: float, vx: float, vy: float,
                 lifetime: float, color: tuple[int, int, int], size: float):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.color = color
        self.size = size
        self.alive = True

    def update(self, dt: float) -> None:
        """Update position and lifetime."""
        dt_factor = dt * 60
        self.x += self.vx * dt_factor
        self.y += self.vy * dt_factor
        self.vy += 0.5 * dt_factor
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False

    def draw(self, screen: pygame.Surface) -> None:
        """Draw particle with alpha fade."""
        if not self.alive:
            return
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        r, g, b = self.color
        color = (r, g, b, alpha)

        size = self.size * (self.lifetime / self.max_lifetime)

        surf = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (int(size), int(size)), int(size))
        screen.blit(surf, (int(self.x - size), int(self.y - size)))


class ParticleSystem:
    """Particle system manager."""

    def __init__(self):
        self.particles: list[Particle] = []

    def emit_hit(self, x: float, y: float) -> None:
        """Hit spark effect: scatter in all directions."""
        for _ in range(PARTICLE_HIT_COUNT):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 4)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            lifetime = random.uniform(0.2, PARTICLE_LIFETIME)
            color = (255, random.randint(150, 255), random.randint(50, 150))
            size = random.uniform(2, 5)
            self.particles.append(Particle(x, y, vx, vy, lifetime, color, size))

    def emit_score(self, x: float, y: float) -> None:
        """Score burst effect: bloom upward."""
        for _ in range(PARTICLE_SCORE_COUNT):
            angle = random.uniform(-math.pi, 0)
            speed = random.uniform(2, 6)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 2
            lifetime = random.uniform(0.3, PARTICLE_LIFETIME + 0.2)
            color = (*GOLD,)
            size = random.uniform(2, 6)
            self.particles.append(Particle(x, y, vx, vy, lifetime, color, size))

    def update(self, dt: float) -> None:
        """Update all particles and remove dead ones."""
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive]

    def draw(self, screen: pygame.Surface) -> None:
        """Draw all live particles."""
        for p in self.particles:
            p.draw(screen)
