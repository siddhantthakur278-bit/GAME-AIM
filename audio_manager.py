import math
import numpy as np
import pygame

class SoundManager:
    def __init__(self):
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.audio_enabled = True
        except Exception as e:
            print(f"Audio init warning: {e}")
            self.audio_enabled = False
            return
            
        self.sounds = {}
        self._generate_all_sounds()

    def _generate_wav_bytes(self, samples, sample_rate=44100):
        samples = np.clip(samples, -1.0, 1.0)
        samples_int = (samples * 32767).astype(np.int16)
        if len(samples_int.shape) == 1:
            samples_int = np.column_stack((samples_int, samples_int))
        byte_buffer = samples_int.tobytes()
        return pygame.mixer.Sound(buffer=byte_buffer)

    def _generate_all_sounds(self):
        if not self.audio_enabled:
            return
        sr = 44100

        # 1. Laser Blast Sound (Frequency sweep down)
        t = np.linspace(0, 0.15, int(sr * 0.15), False)
        freq = np.linspace(800, 150, len(t))
        wave_data = np.sin(2 * np.pi * freq * t) * np.exp(-t * 20)
        self.sounds['laser'] = self._generate_wav_bytes(wave_data)

        # 2. Punch Impact Sound (Noise + Low Frequency thump)
        t = np.linspace(0, 0.2, int(sr * 0.2), False)
        thump = np.sin(2 * np.pi * 70 * t) * np.exp(-t * 25)
        noise = (np.random.rand(len(t)) * 2 - 1) * np.exp(-t * 30)
        wave_data = thump * 0.7 + noise * 0.5
        self.sounds['punch'] = self._generate_wav_bytes(wave_data)

        # 3. Shield Sound (Harmonic resonance sweep up)
        t = np.linspace(0, 0.35, int(sr * 0.35), False)
        freq = np.linspace(200, 600, len(t))
        wave_data = (np.sin(2 * np.pi * freq * t) + 0.5 * np.sin(4 * np.pi * freq * t)) * (1 - np.exp(-t*10)) * np.exp(-t*3)
        self.sounds['shield'] = self._generate_wav_bytes(wave_data)

        # 4. Freeze Sound (Crystal/Chime sound)
        t = np.linspace(0, 0.5, int(sr * 0.5), False)
        wave_data = (np.sin(2 * np.pi * 1200 * t) + np.sin(2 * np.pi * 1500 * t) + np.sin(2 * np.pi * 1800 * t)) * np.exp(-t * 8)
        self.sounds['freeze'] = self._generate_wav_bytes(wave_data)

        # 5. Explosion / Nuke Sound (Low noise boom)
        t = np.linspace(0, 0.6, int(sr * 0.6), False)
        noise = (np.random.rand(len(t)) * 2 - 1)
        sub = np.sin(2 * np.pi * 50 * t)
        wave_data = (noise * 0.6 + sub * 0.8) * np.exp(-t * 5)
        self.sounds['explosion'] = self._generate_wav_bytes(wave_data)

        # 6. Combo Sound (Rising high pitch chime)
        t = np.linspace(0, 0.1, int(sr * 0.1), False)
        freq = 900
        wave_data = np.sin(2 * np.pi * freq * t) * np.exp(-t * 15)
        self.sounds['combo'] = self._generate_wav_bytes(wave_data)

    def play(self, sound_name):
        if self.audio_enabled and sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except Exception:
                pass
