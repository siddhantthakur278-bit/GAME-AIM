import cv2
import numpy as np
import random
import math

class Particle:
    def __init__(self, x, y, vx, vy, color, lifetime, radius=3, p_type='SPARK'):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.max_lifetime = lifetime
        self.lifetime = lifetime
        self.radius = radius
        self.p_type = p_type

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        if self.p_type == 'SPARK':
            self.vy += 0.15 # gravity
            self.vx *= 0.98
        elif self.p_type == 'ENERGY':
            self.vx *= 0.95
            self.vy *= 0.95

    def draw(self, img):
        if self.lifetime <= 0:
            return
        alpha = max(0, self.lifetime / self.max_lifetime)
        curr_r = max(1, int(self.radius * alpha))
        
        # Draw glowing particle
        overlay = img.copy()
        cv2.circle(overlay, (int(self.x), int(self.y)), curr_r, self.color, -1)
        cv2.circle(overlay, (int(self.x), int(self.y)), curr_r + 2, (255, 255, 255), 1)
        cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)

class ParticleEngine:
    def __init__(self):
        self.particles = []

    def add_explosion(self, x, y, color=(0, 215, 255), count=30):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 12)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            life = random.randint(15, 35)
            r = random.randint(3, 7)
            self.particles.append(Particle(x, y, vx, vy, color, life, r, 'SPARK'))

    def add_laser_trail(self, start_p, end_p, color=(255, 0, 255)):
        dx = end_p[0] - start_p[0]
        dy = end_p[1] - start_p[1]
        dist = math.hypot(dx, dy)
        steps = int(dist / 10) + 1
        for i in range(steps):
            px = start_p[0] + dx * (i / steps) + random.uniform(-3, 3)
            py = start_p[1] + dy * (i / steps) + random.uniform(-3, 3)
            self.particles.append(Particle(px, py, 0, 0, color, random.randint(5, 12), 2, 'ENERGY'))

    def add_aura(self, x, y, color=(0, 255, 0)):
        for _ in range(3):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 4)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            self.particles.append(Particle(x, y, vx, vy, color, random.randint(10, 20), 4, 'ENERGY'))

    def update_and_draw(self, img):
        active_particles = []
        for p in self.particles:
            p.update()
            if p.lifetime > 0:
                p.draw(img)
                active_particles.append(p)
        self.particles = active_particles
