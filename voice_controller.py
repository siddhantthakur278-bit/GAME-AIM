import threading
import queue
import time

class VoiceController:
    def __init__(self):
        self.command_queue = queue.Queue()
        self.running = False
        self.thread = None
        self.has_sr = False
        
        try:
            import speech_recognition as sr
            self.sr = sr
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.has_sr = True
        except ImportError:
            print("SpeechRecognition module not found. Voice commands will fallback to keyboard hotkeys.")

    def start(self):
        if not self.has_sr:
            return
        self.running = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def _listen_loop(self):
        try:
            mic = self.sr.Microphone()
            with mic as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.8)
                while self.running:
                    try:
                        audio = self.recognizer.listen(source, timeout=1.5, phrase_time_limit=2.0)
                        text = self.recognizer.recognize_google(audio).lower()
                        print(f"[Voice Heard]: {text}")
                        self._process_text(text)
                    except self.sr.WaitTimeoutError:
                        pass
                    except self.sr.UnknownValueError:
                        pass
                    except Exception as e:
                        time.sleep(0.5)
        except Exception as e:
            print(f"Microphone init failed: {e}")

    def _process_text(self, text):
        if any(w in text for w in ['shield', 'protect', 'defense', 'guard']):
            self.command_queue.put('SHIELD')
        elif any(w in text for w in ['freeze', 'ice', 'stasis', 'stop', 'hold']):
            self.command_queue.put('FREEZE')
        elif any(w in text for w in ['nuke', 'clear', 'boom', 'fire', 'blast', 'destroy']):
            self.command_queue.put('NUKE')

    def get_latest_command(self):
        try:
            return self.command_queue.get_nowait()
        except queue.Empty:
            return None
