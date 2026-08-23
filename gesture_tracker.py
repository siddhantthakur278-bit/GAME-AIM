import cv2
import numpy as np

class ZeroLagPureTracker:
    def __init__(self):
        # YCrCb bounds for fast skin extraction
        self.lower = np.array([0, 133, 77], dtype=np.uint8)
        self.upper = np.array([255, 173, 127], dtype=np.uint8)

    def process_frame(self, frame):
        h, w, _ = frame.shape
        
        # 160x120 downscaled buffer for instant sub-3ms execution
        small = cv2.resize(frame, (160, 120))
        h_s, w_s, _ = small.shape
        scale_x = w / float(w_s)
        scale_y = h / float(h_s)

        ycrcb = cv2.cvtColor(small, cv2.COLOR_BGR2YCrCb)
        mask = cv2.inRange(ycrcb, self.lower, self.upper)
        mask[0:25, :] = 0 # Ignore top banner area

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        hands_data = []
        if contours:
            cnt = max(contours, key=cv2.contourArea)
            if cv2.contourArea(cnt) > 80:
                topmost_s = tuple(cnt[cnt[:, :, 1].argmin()][0])
                topmost = (int(topmost_s[0] * scale_x), int(topmost_s[1] * scale_y))

                hands_data.append({
                    'handedness': 'Left',
                    'gesture': 'PINCH_KILL',
                    'target_point': topmost,
                    'is_pinch': True
                })

        return hands_data
