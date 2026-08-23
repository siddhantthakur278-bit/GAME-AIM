import cv2
import numpy as np

class UltraLightGraphics:
    def __init__(self):
        pass

    def trigger_shake(self, intensity=0):
        pass

    def apply_cinematic_grade(self, frame):
        return frame # Direct zero-cost pass-through for 0% lag!

    def draw_photoreal_orb(self, img, x, y, radius, color=(0, 215, 255), is_frozen=False):
        ix, iy = int(x), int(y)
        r = int(radius)
        cv2.circle(img, (ix, iy), r, color, -1, cv2.LINE_AA)
        cv2.circle(img, (ix, iy), r, (255, 255, 255), 3, cv2.LINE_AA)

    def draw_laser_beam(self, img, start_pos, end_pos, color=(0, 255, 255)):
        cv2.line(img, start_pos, end_pos, color, 4, cv2.LINE_AA)

    def draw_hand_aura(self, img, hand_info):
        target = hand_info.get('target_point', (320, 240))
        cv2.circle(img, target, 20, (0, 255, 255), 2, cv2.LINE_AA)
        cv2.circle(img, target, 5, (0, 255, 255), -1, cv2.LINE_AA)

    def draw_glass_hud(self, img, score, combo, health, level_num, level_title, active_shield, active_freeze, voice_msg=None):
        h, w, _ = img.shape
        cv2.rectangle(img, (0, 0), (w, 50), (20, 20, 20), -1)
        cv2.putText(img, f"LEVEL {level_num}: {level_title.upper()} | SCORE: {score:06d}", (20, 32),
                    cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 255, 255), 1, cv2.LINE_AA)
