import cv2
import numpy as np
import time
from flask import Flask, render_template_string, Response, jsonify

app = Flask(__name__)

# Web Game Engine State
class WebGameEngine:
    def __init__(self):
        self.score = 0
        self.combo = 0
        self.level = 1
        self.enemies = [{'x': 320, 'y': 200, 'vx': 1.5, 'vy': 1.0, 'radius': 50}]
        self.last_spawn = time.time()

    def update(self):
        now = time.time()
        if len(self.enemies) < 3 and (now - self.last_spawn) > 3.0:
            self.last_spawn = now
            self.enemies.append({
                'x': float(np.random.randint(100, 540)),
                'y': float(np.random.randint(120, 300)),
                'vx': float(np.random.uniform(-2, 2)),
                'vy': float(np.random.uniform(-1, 1)),
                'radius': 50
            })

        for e in self.enemies:
            e['x'] += e['vx']
            e['y'] += e['vy']
            if e['x'] < 60 or e['x'] > 580: e['vx'] *= -1
            if e['y'] < 80 or e['y'] > 360: e['vy'] *= -1

    def hit_test(self, x, y):
        hit = False
        for e in self.enemies[:]:
            dist = math.hypot(e['x'] - x, e['y'] - y)
            if dist < e['radius'] + 60:
                self.enemies.remove(e)
                self.score += 100
                self.combo += 1
                hit = True
        return hit

import math
game_engine = WebGameEngine()

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
    <p>Live Web Browser Camera Game</p>
    
    <button onclick="startCamera()">📷 Click to Start Camera & Play</button>

    <div class="canvas-container">
        <video id="webcamVideo" autoplay playsinline style="display:none;"></video>
        <canvas id="gameCanvas" width="640" height="480"></canvas>
    </div>

    <div class="controls">
        <p><span class="badge">CONTROLS</span> Move mouse / finger on video to lock target reticle & blast orbs!</p>
    </div>

    <script>
        const video = document.getElementById('webcamVideo');
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');

        let gameState = { score: 0, combo: 0, level: 1, enemies: [] };
        let pointer = { x: 320, y: 240 };

        async function startCamera() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } });
                video.srcObject = stream;
                video.onloadedmetadata = () => {
                    video.play();
                    requestAnimationFrame(gameLoop);
                };
            } catch (err) {
                alert("Camera permission error: " + err);
            }
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

        async function updateEngine() {
            const res = await fetch('/api/state');
            gameState = await res.json();
        }

        setInterval(updateEngine, 200);

        function gameLoop() {
            ctx.save();
            ctx.scale(-1, 1);
            ctx.drawImage(video, -canvas.width, 0, canvas.width, canvas.height);
            ctx.restore();

            // Render HUD Header
            ctx.fillStyle = 'rgba(10, 15, 25, 0.7)';
            ctx.fillRect(20, 15, canvas.width - 40, 50);
            ctx.strokeStyle = '#00f0ff';
            ctx.lineWidth = 2;
            ctx.strokeRect(20, 15, canvas.width - 40, 50);

            ctx.fillStyle = '#00f0ff';
            ctx.font = 'bold 18px Segoe UI';
            ctx.fillText(`LEVEL ${gameState.level}: COSMIC INCURSION`, 40, 48);

            ctx.fillStyle = '#ffffff';
            ctx.fillText(`SCORE: ${String(gameState.score).padStart(6, '0')}`, canvas.width - 200, 48);

            // Render Volumetric Enemies
            if (gameState.enemies) {
                gameState.enemies.forEach(e => {
                    // Outer glow
                    ctx.beginPath();
                    ctx.arc(e.x, e.y, e.radius + 10, 0, Math.PI * 2);
                    ctx.fillStyle = 'rgba(0, 215, 255, 0.3)';
                    ctx.fill();

                    // Core sphere
                    ctx.beginPath();
                    ctx.arc(e.x, e.y, e.radius, 0, Math.PI * 2);
                    ctx.fillStyle = '#00d7ff';
                    ctx.fill();
                    ctx.strokeStyle = '#ffffff';
                    ctx.lineWidth = 3;
                    ctx.stroke();

                    // Specular Highlight
                    ctx.beginPath();
                    ctx.arc(e.x - 12, e.y - 12, 10, 0, Math.PI * 2);
                    ctx.fillStyle = '#ffffff';
                    ctx.fill();
                });
            }

            // Render Scope Reticle
            ctx.beginPath();
            ctx.arc(pointer.x, pointer.y, 22, 0, Math.PI * 2);
            ctx.strokeStyle = '#ffff00';
            ctx.lineWidth = 3;
            ctx.stroke();

            ctx.beginPath();
            ctx.arc(pointer.x, pointer.y, 6, 0, Math.PI * 2);
            ctx.fillStyle = '#ffff00';
            ctx.fill();

            ctx.beginPath();
            ctx.moveTo(pointer.x - 35, pointer.y);
            ctx.lineTo(pointer.x + 35, pointer.y);
            ctx.moveTo(pointer.x, pointer.y - 35);
            ctx.lineTo(pointer.x, pointer.y + 35);
            ctx.strokeStyle = '#ffff00';
            ctx.lineWidth = 2;
            ctx.stroke();

            requestAnimationFrame(gameLoop);
        }
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

from flask import request

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
