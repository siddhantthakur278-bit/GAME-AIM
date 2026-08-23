import cv2
import numpy as np
import time
import sys

from audio_manager import SoundManager
from gesture_tracker import ZeroLagPureTracker
from voice_controller import VoiceController
from particle_system import ParticleEngine
from graphics_engine import UltraLightGraphics
from game_manager import GameManager

def main():
    print("=" * 60)
    print("      HIGH GRAPHICS ALTERED REALITY WEBCAM AR GAME      ")
    print("==========================================================")
    print("Controls (0% Lag Ultra Mode):")
    print("  - MOVE HAND: Target scope is 100% INSTANT SYNCED!")
    print("  - Voice Commands: 'Shield', 'Freeze', 'Nuke'")
    print("  - Hotkeys: [S] Shield, [F] Freeze, [N] Nuke, [Q] Quit")
    print("=" * 60)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    # Fast 640x480 webcam capture
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 60)

    sound_mgr = SoundManager()
    gesture_tracker = ZeroLagPureTracker()
    voice_controller = VoiceController()
    voice_controller.start()

    particle_engine = ParticleEngine()
    graphics_engine = UltraLightGraphics()
    game_mgr = GameManager(sound_mgr, graphics_engine, particle_engine)

    last_attack_time = 0
    voice_msg_display = None
    voice_msg_timer = 0

    cv2.namedWindow("Altered Reality AR Game", cv2.WINDOW_NORMAL)

    def mouse_callback(event, x, y, flags, param):
        is_click = (event == cv2.EVENT_LBUTTONDOWN)
        gesture_tracker.set_pos(x, y, is_click)
        if is_click:
            nonlocal last_attack_time
            game_mgr.process_player_attack('PINCH', (x, y))
            particle_engine.add_laser_trail((320, 480), (x, y), color=(0, 255, 255))
            last_attack_time = time.time()

    cv2.setMouseCallback("Altered Reality AR Game", mouse_callback)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape

        voice_cmd = voice_controller.get_latest_command()
        if voice_cmd:
            voice_msg_display = voice_cmd
            voice_msg_timer = time.time() + 2.0
            if voice_cmd == 'SHIELD':
                game_mgr.activate_shield()
            elif voice_cmd == 'FREEZE':
                game_mgr.activate_freeze()
            elif voice_cmd == 'NUKE':
                game_mgr.trigger_nuke()

        hands = gesture_tracker.process_frame(frame)
        current_time = time.time()

        for hand in hands:
            target = hand['target_point']
            is_pinch = hand.get('is_pinch', False)
            
            # Render scope right on fingertip
            graphics_engine.draw_hand_aura(frame, hand)

            # Continuous fingertip aim & instant Pinch Kill
            if is_pinch or current_time - last_attack_time > 0.1:
                particle_engine.add_laser_trail((w // 2, h), target, color=(0, 255, 255))
                game_mgr.process_player_attack('PINCH', target)
                last_attack_time = current_time

        # 3. Update Game State & Enemies
        game_mgr.update(w, h)

        # 4. Render Particle System
        particle_engine.update_and_draw(frame)

        # 5. Render AR Enemies & Photorealistic Volumetric Orbs
        game_mgr.draw_enemies(frame)

        # 6. Apply Cinematic Color Grade, Lens Vignette & Screen Shake
        frame = graphics_engine.apply_cinematic_grade(frame)
        
        # 7. Render Frosted Glass AR HUD
        active_voice_text = voice_msg_display if time.time() < voice_msg_timer else None
        graphics_engine.draw_glass_hud(
            frame,
            game_mgr.score,
            game_mgr.combo,
            game_mgr.health,
            game_mgr.level,
            game_mgr.level_titles[game_mgr.level],
            game_mgr.is_shield_active(),
            game_mgr.is_freeze_active(),
            active_voice_text
        )

        # 8. Render Game Over / Victory Overlay
        if game_mgr.game_over:
            cv2.putText(frame, "GAME OVER", (w // 2 - 200, h // 2),
                        cv2.FONT_HERSHEY_DUPLEX, 2.0, (0, 0, 255), 4)
            cv2.putText(frame, "Press 'R' to Restart or 'Q' to Quit", (w // 2 - 220, h // 2 + 60),
                        cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 2)
        elif game_mgr.victory:
            cv2.putText(frame, "VICTORY! OVERLORD DEFEATED", (w // 2 - 350, h // 2),
                        cv2.FONT_HERSHEY_DUPLEX, 1.8, (0, 255, 0), 4)

        # Display Frame
        cv2.imshow("Altered Reality AR Game", frame)

        # Handle Keyboard Input
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break
        elif key == ord('s'):
            game_mgr.activate_shield()
        elif key == ord('f'):
            game_mgr.activate_freeze()
        elif key == ord('n'):
            game_mgr.trigger_nuke()
        elif key == ord('r') and (game_mgr.game_over or game_mgr.victory):
            game_mgr = GameManager(sound_mgr, graphics_engine, particle_engine)

    voice_controller.stop()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
