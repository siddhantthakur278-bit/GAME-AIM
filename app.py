import cv2
import numpy as np
import time
import math
from flask import Flask, render_template_string, Response, jsonify, request

app = Flask(__name__)

# Web Game Engine State
class WebGameEngine:
    def __init__(self):
        self.score = 0
        self.combo = 0
        self.level = 1
        self.enemies = [{'x': 320, 'y': 200, 'vx': 1.0, 'vy': 0.8, 'radius': 55}]
        self.last_spawn = time.time()

    def update(self):
        now = time.time()
        if len(self.enemies) < 3 and (now - self.last_spawn) > 3.0:
            self.last_spawn = now
            self.enemies.append({
                'x': float(np.random.randint(100, 540)),
                'y': float(np.random.randint(120, 300)),
                'vx': float(np.random.uniform(-1.5, 1.5)),
                'vy': float(np.random.uniform(-1.0, 1.0)),
                'radius': 55
            })

        for e in self.enemies:
            e['x'] += e['vx']
            e['y'] += e['vy']
            if e['x'] < 60 or e['x'] > 580: e['vx'] *= -1
            if e['y'] < 80 or e['y'] > 360: e['vy'] *= -1

    def hit_test(self, x, y):
        for e in self.enemies[:]:
            dist = math.hypot(e['x'] - x, e['y'] - y)
            if dist < e['radius'] + 100: # Super large 100px hit range
                self.enemies.remove(e)
                self.score += 100
                self.combo += 1
                return True
        return False

game_engine = WebGameEngine()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Altered Reality AR Game - Web Client</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- MediaPipe Hands CDN for in-browser client-side hand tracking -->
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/hands/hands.js" crossorigin="anonymous"></script>
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
            padding: 12px 24px;
            font-size: 1.1rem;
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
    <p>Client-Side MediaPipe Hand Tracking AR Engine</p>
    
    <button id="startBtn" onclick="startCamera()">🖐️ Click to Start Hand Tracking & Play</button>

    <div class="canvas-container">
        <video id="webcamVideo" autoplay playsinline style="display:none;"></video>
        <canvas id="gameCanvas" width="640" height="480"></canvas>
    </div>

    <div class="controls">
        <p><span class="badge">CONTROLS</span> Raise your hand in front of your webcam to lock scope & blast orbs!</p>
    </div>

    <script>
        const video = document.getElementById('webcamVideo');
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');

        let gameState = { score: 0, combo: 0, level: 1, enemies: [] };
        let pointer = { x: 320, y: 240 };
        let handsDetector = null;
        let camera = null;

        async function updateEngine() {
            try {
                const res = await fetch('/api/state');
                gameState = await res.json();
            } catch(e) {}
        }
        setInterval(updateEngine, 200);

        function onResults(results) {
            // Draw mirrored camera frame
            ctx.save();
            ctx.scale(-1, 1);
            ctx.drawImage(results.image, -canvas.width, 0, canvas.width, canvas.height);
            ctx.restore();

            // Track Index Fingertip Landmark (ID 8)
            if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
                const lm = results.multiHandLandmarks[0][8];
                pointer.x = (1 - lm.x) * canvas.width; // Mirrored X
                pointer.y = lm.y * canvas.height;

                // Auto-trigger blast attack at fingertip position
                fetch(`/api/hit?x=${Math.round(pointer.x)}&y=${Math.round(pointer.y)}`)
                    .then(res => res.json())
                    .then(data => gameState = data);
            }

            // Render HUD Header
            ctx.fillStyle = 'rgba(10, 15, 25, 0.75)';
            ctx.fillRect(20, 15, canvas.width - 40, 50);
            ctx.strokeStyle = '#00f0ff';
            ctx.lineWidth = 2;
            ctx.strokeRect(20, 15, canvas.width - 40, 50);

            ctx.fillStyle = '#00f0ff';
            ctx.font = 'bold 18px Segoe UI';
            ctx.fillText(`LEVEL ${gameState.level}: COSMIC INCURSION`, 40, 48);

            ctx.fillStyle = '#ffffff';
            ctx.fillText(`SCORE: ${String(gameState.score).padStart(6, '0')}`, canvas.width - 200, 48);

            // Render Flying Orbs
            if (gameState.enemies) {
                gameState.enemies.forEach(e => {
                    ctx.beginPath();
                    ctx.arc(e.x, e.y, e.radius + 12, 0, Math.PI * 2);
                    ctx.fillStyle = 'rgba(0, 215, 255, 0.35)';
                    ctx.fill();

                    ctx.beginPath();
                    ctx.arc(e.x, e.y, e.radius, 0, Math.PI * 2);
                    ctx.fillStyle = '#00d7ff';
                    ctx.fill();
                    ctx.strokeStyle = '#ffffff';
                    ctx.lineWidth = 3;
                    ctx.stroke();

                    ctx.beginPath();
                    ctx.arc(e.x - 12, e.y - 12, 10, 0, Math.PI * 2);
                    ctx.fillStyle = '#ffffff';
                    ctx.fill();
                });
            }

            // Render Target Scope Reticle on Fingertip
            ctx.beginPath();
            ctx.arc(pointer.x, pointer.y, 24, 0, Math.PI * 2);
            ctx.strokeStyle = '#ffff00';
            ctx.lineWidth = 3;
            ctx.stroke();

            ctx.beginPath();
            ctx.arc(pointer.x, pointer.y, 6, 0, Math.PI * 2);
            ctx.fillStyle = '#ffff00';
            ctx.fill();

            ctx.beginPath();
            ctx.moveTo(pointer.x - 38, pointer.y);
            ctx.lineTo(pointer.x + 38, pointer.y);
            ctx.moveTo(pointer.x, pointer.y - 38);
            ctx.lineTo(pointer.x, pointer.y + 38);
            ctx.strokeStyle = '#ffff00';
            ctx.lineWidth = 2;
            ctx.stroke();
        }

        async function startCamera() {
            document.getElementById('startBtn').innerText = "⏳ Loading Hand Tracker...";
            
            handsDetector = new Hands({
                locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
            });

            handsDetector.setOptions({
                maxNumHands: 1,
                modelComplexity: 1,
                minDetectionConfidence: 0.5,
                minTrackingConfidence: 0.5
            });

            handsDetector.onResults(onResults);

            camera = new Camera(video, {
                onFrame: async () => {
                    await handsDetector.send({ image: video });
                },
                width: 640,
                height: 480
            });

            camera.start();
            document.getElementById('startBtn').style.display = 'none';
        }

        canvas.addEventListener('mousemove', (e) => {
            const rect = canvas.getBoundingClientRect();
            pointer.x = (e.clientX - rect.left) * (canvas.width / rect.width);
            pointer.y = (e.clientY - rect.top) * (canvas.height / rect.height);
        });

        canvas.addEventListener('click', async (e) => {
            const res = await fetch(`/api/hit?x=${Math.round(pointer.x)}&y=${Math.round(pointer.y)}`);
            const data = await res.json();
            gameState = data;
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/state')
def get_state():
    game_engine.update()
    return jsonify({
        'score': game_engine.score,
        'combo': game_engine.combo,
        'level': game_engine.level,
        'enemies': game_engine.enemies
    })

@app.route('/api/hit')
def hit():
    x = float(request.args.get('x', 320))
    y = float(request.args.get('y', 240))
    game_engine.hit_test(x, y)
    return jsonify({
        'score': game_engine.score,
        'combo': game_engine.combo,
        'level': game_engine.level,
        'enemies': game_engine.enemies
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
