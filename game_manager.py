import cv2
import numpy as np
import math
import random
import time

class Enemy:
    def __init__(self, x, y, e_type='DRONE', level=1):
        self.x = float(x)
        self.y = float(y)
        self.vx = random.uniform(-0.8, 0.8)
        self.vy = random.uniform(-0.5, 0.5)
        self.e_type = e_type
        self.radius = 65 if e_type != 'BOSS' else 110
        self.hp = 1
        self.max_hp = 1
        self.pulse = random.uniform(0, math.pi)

    def update(self, frame_w, frame_h, is_frozen=False):
        if is_frozen:
            return

        self.pulse += 0.05
        
        # Smooth floating physics with subtle spring force towards center
        target_x = frame_w / 2.0
        target_y = frame_h / 2.5
        
        ax = (target_x - self.x) * 0.0003
        ay = (target_y - self.y) * 0.0003

        self.vx = (self.vx + ax) * 0.98
        self.vy = (self.vy + ay) * 0.98

        self.x += self.vx
        self.y += self.vy + math.sin(self.pulse) * 0.4

        # Smooth screen boundary bounce
        if self.x < 80: self.vx = abs(self.vx)
        if self.x > frame_w - 80: self.vx = -abs(self.vx)
        if self.y < 100: self.vy = abs(self.vy)
        if self.y > frame_h - 100: self.vy = -abs(self.vy)

class GameManager:
    def __init__(self, sound_mgr, graphics_engine, particle_engine):
        self.sound_mgr = sound_mgr
        self.graphics = graphics_engine
        self.particles = particle_engine

        self.score = 0
        self.combo = 0
        self.health = 100
        self.energy = 100
        self.level = 1
        self.level_titles = {
            1: "Cosmic Incursion",
            2: "Elemental Tempest",
            3: "Cyber Overlord Boss"
        }

        self.enemies = []
        self.last_spawn = time.time()
        self.shield_until = 0
        self.freeze_until = 0
        self.game_over = False
        self.victory = False

    def is_shield_active(self):
        return time.time() < self.shield_until

    def is_freeze_active(self):
        return time.time() < self.freeze_until

    def activate_shield(self, duration=5.0):
        self.shield_until = time.time() + duration
        self.sound_mgr.play('shield')

    def activate_freeze(self, duration=5.0):
        self.freeze_until = time.time() + duration
        self.sound_mgr.play('freeze')

    def trigger_nuke(self):
        self.sound_mgr.play('explosion')
        self.graphics.trigger_shake(25)
        for e in self.enemies:
            self.particles.add_explosion(int(e.x), int(e.y), (0, 215, 255), count=30)
            self.score += 150
        self.enemies.clear()

    def update(self, frame_w, frame_h):
        if self.game_over or self.victory:
            return

        now = time.time()
        is_frozen = self.is_freeze_active()

        # Spawn enemies (Max 3 on screen, 3s delay)
        if len(self.enemies) < 3 and (now - self.last_spawn) > 3.0:
            self.last_spawn = now
            x = random.randint(100, frame_w - 100)
            y = random.randint(120, frame_h // 2)
            self.enemies.append(Enemy(x, y, 'DRONE', self.level))

        # Check level advancement
        if self.level == 1 and self.score >= 600:
            self.level = 2
            self.sound_mgr.play('combo')
        elif self.level == 2 and self.score >= 1400:
            self.level = 3
            self.sound_mgr.play('combo')

        # Update enemies
        for e in self.enemies:
            e.update(frame_w, frame_h, is_frozen)

    def process_player_attack(self, attack_type, target_pos):
        if self.game_over or not target_pos:
            return

        tx, ty = target_pos

        for e in self.enemies[:]:
            dist = math.hypot(e.x - tx, e.y - ty)
            hit_threshold = e.radius + 150 # Massive easy hit range

            if dist <= hit_threshold:
                self.particles.add_explosion(int(e.x), int(e.y), (0, 215, 255), count=30)
                self.sound_mgr.play('laser')
                self.enemies.remove(e)
                self.score += 100 * self.level
                self.combo += 1
                self.sound_mgr.play('combo')
                if e.e_type == 'BOSS':
                    self.victory = True

    def draw_enemies(self, img):
        is_frozen = self.is_freeze_active()
        for e in self.enemies:
            color = (0, 215, 255) if e.e_type == 'DRONE' else (0, 0, 255)
            self.graphics.draw_photoreal_orb(img, e.x, e.y, e.radius, color, is_frozen)
