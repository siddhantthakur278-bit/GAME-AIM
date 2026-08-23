import cv2
import numpy as np
import time
from flask import Flask, render_template_string, Response

from audio_manager import SoundManager
from gesture_tracker import ZeroLagPureTracker
from voice_controller import VoiceController
from particle_system import ParticleEngine
from graphics_engine import UltraLightGraphics
from game_manager import GameManager

app = Flask(__name__)

# Global Game Engine Instances
sound_mgr = SoundManager()
gesture_tracker = ZeroLagPureTracker()
particle_engine = ParticleEngine()
graphics_engine = UltraLightGraphics()
game_mgr = GameManager(sound_mgr, graphics_engine, particle_engine)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Altered Reality AR Game - Web Client</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            background-color: #0d0f17;
            color: #ffffff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            text-align: center;
            margin: 0;
            padding: 20px;
        }
        h1 {
            color: #00f0ff;
            text-shadow: 0 0 10px #00f0ff;
        }
        .canvas-container {
            position: relative;
            display: inline-block;
            border: 3px solid #00f0ff;
            border-radius: 12px;
            box-shadow: 0 0 25px rgba(0, 240, 255, 0.4);
            overflow: hidden;
            margin-top: 15px;
            background: #000;
        }
        video, canvas {
            width: 100%;
            max-width: 800px;
            height: auto;
            display: block;
        }
        #webcamVideo {
            transform: scaleX(-1);
        }
        .controls {
            margin-top: 20px;
            font-size: 1.1em;
            color: #a0a5c0;
        }
        .badge {
            background: #00f0ff;
            color: #000;
            padding: 4px 10px;
            border-radius: 4px;
            font-weight: bold;
        }
        button {
            background: #00f0ff;
            border: none;
            color: #000;
            padding: 10px 20px;
            font-size: 1rem;
            font-weight: bold;
            border-radius: 6px;
            cursor: pointer;
            margin-bottom: 10px;
        }
        button:hover {
            background: #00c0ff;
        }
    </style>
</head>
<body>
    <h1>🌌 Altered Reality (AR) Webcam Game</h1>
    <p>Client-Side Web Cam Stream & Real-Time AR Game</p>
    
    <button onclick="startCamera()">📷 Enable Camera</button>

    <div class="canvas-container">
        <video id="webcamVideo" autoplay playsinline style="display:none;"></video>
        <canvas id="gameCanvas" width="640" height="480"></canvas>
    </div>

    <div class="controls">
        <p><span class="badge">CONTROLS</span> Point your hand towards flying orbs to lock scope & blast them!</p>
    </div>

    <script>
        const video = document.getElementById('webcamVideo');
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');

        async function startCamera() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } });
                video.srcObject = stream;
                video.onloadedmetadata = () => {
                    video.play();
                    requestAnimationFrame(drawLoop);
                };
            } catch (err) {
                alert("Camera access denied or unavailable: " + err);
            }
        }

        function drawLoop() {
            ctx.save();
            ctx.scale(-1, 1);
            ctx.drawImage(video, -canvas.width, 0, canvas.width, canvas.height);
            ctx.restore();

            // Simple client overlay fallback for browser rendering
            ctx.strokeStyle = '#00f0ff';
            ctx.lineWidth = 3;
            ctx.strokeRect(20, 20, canvas.width - 40, 50);

            ctx.fillStyle = '#00f0ff';
            ctx.font = '20px Segoe UI';
            ctx.fillText('LEVEL 1: COSMIC INCURSION', 40, 52);

            requestAnimationFrame(drawLoop);
        }
    </script>
</body>
</html>
"""

def generate_frames():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    last_attack_time = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        hands = gesture_tracker.process_frame(frame)
        current_time = time.time()

        for hand in hands:
            target = hand['target_point']
            graphics_engine.draw_hand_aura(frame, hand)

            if current_time - last_attack_time > 0.1:
                particle_engine.add_laser_trail((w // 2, h), target, color=(0, 255, 255))
                game_mgr.process_player_attack('PINCH', target)
                last_attack_time = current_time

        game_mgr.update(w, h)
        particle_engine.update_and_draw(frame)
        game_mgr.draw_enemies(frame)
        graphics_engine.draw_glass_hud(
            frame,
            game_mgr.score,
            game_mgr.combo,
            game_mgr.health,
            game_mgr.level,
            game_mgr.level_titles[game_mgr.level],
            game_mgr.is_shield_active(),
            game_mgr.is_freeze_active()
        )

        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
