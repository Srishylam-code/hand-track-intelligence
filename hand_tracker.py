"""
hand_tracker.py — MediaPipe Hand Landmarker wrapper for real-time detection.

Uses the new MediaPipe Tasks API (mediapipe.tasks.python.vision).
Detects up to 2 hands and returns 21 normalized landmarks (x, y, z) per hand.
Draws landmarks on the frame for visual debugging.
"""

import os
import cv2
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import (
    HandLandmarker,
    HandLandmarkerOptions,
    RunningMode,
)

# Landmark connections for drawing (pairs of landmark indices)
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),        # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),        # Index
    (0, 9), (9, 10), (10, 11), (11, 12),   # Middle
    (0, 13), (13, 14), (14, 15), (15, 16), # Ring
    (0, 17), (17, 18), (18, 19), (19, 20), # Pinky
    (5, 9), (9, 13), (13, 17),             # Palm
]

LANDMARK_NAMES = [
    "WRIST",
    "THUMB_CMC", "THUMB_MCP", "THUMB_IP", "THUMB_TIP",
    "INDEX_FINGER_MCP", "INDEX_FINGER_PIP", "INDEX_FINGER_DIP", "INDEX_FINGER_TIP",
    "MIDDLE_FINGER_MCP", "MIDDLE_FINGER_PIP", "MIDDLE_FINGER_DIP", "MIDDLE_FINGER_TIP",
    "RING_FINGER_MCP", "RING_FINGER_PIP", "RING_FINGER_DIP", "RING_FINGER_TIP",
    "PINKY_MCP", "PINKY_PIP", "PINKY_DIP", "PINKY_TIP",
]


class HandTracker:
    """Wraps MediaPipe Hand Landmarker (Tasks API) for easy hand detection."""

    def __init__(
        self,
        model_path: str = None,
        max_num_hands: int = 2,
        min_detection_confidence: float = 0.7,
        min_tracking_confidence: float = 0.5,
    ):
        """
        Args:
            model_path: Path to hand_landmarker.task model file.
                        Defaults to 'hand_landmarker.task' in the same directory.
            max_num_hands: Maximum number of hands to detect (1 or 2).
            min_detection_confidence: Minimum confidence for initial detection.
            min_tracking_confidence: Minimum confidence for frame-to-frame tracking.
        """
        if model_path is None:
            model_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "hand_landmarker.task",
            )

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model file not found: {model_path}\n"
                "Download it from: https://storage.googleapis.com/mediapipe-models/"
                "hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
            )

        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=RunningMode.VIDEO,
            num_hands=max_num_hands,
            min_hand_detection_confidence=min_detection_confidence,
            min_hand_presence_confidence=min_tracking_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

        self.landmarker = HandLandmarker.create_from_options(options)
        self._frame_timestamp_ms = 0

    def process(self, frame):
        """
        Process a BGR frame and return detected hand landmarks.

        Args:
            frame: BGR image (numpy array) from OpenCV.

        Returns:
            list of hands, where each hand is a list of 21 dicts:
                [{"id": int, "name": str, "x": float, "y": float, "z": float}, ...]
            Returns an empty list if no hands are detected.
        """
        # Convert BGR → RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # Increment timestamp (must be monotonically increasing)
        self._frame_timestamp_ms += 33  # ~30 FPS

        result = self.landmarker.detect_for_video(mp_image, self._frame_timestamp_ms)
        self._last_result = result  # Cache for draw_landmarks()

        all_hands = []
        if result.hand_landmarks:
            for hand_landmarks in result.hand_landmarks:
                landmarks = []
                for idx, lm in enumerate(hand_landmarks):
                    landmarks.append({
                        "id": idx,
                        "name": LANDMARK_NAMES[idx],
                        "x": lm.x,      # 0.0 – 1.0 (normalized to frame width)
                        "y": lm.y,      # 0.0 – 1.0 (normalized to frame height)
                        "z": lm.z,      # Depth relative to wrist
                    })
                all_hands.append(landmarks)

        return all_hands

    def draw_on_frame(self, frame, hands):
        """
        Draw pre-computed hand landmarks on the frame (in-place).
        Uses data already returned by process() — no extra detection.

        Args:
            frame: BGR image (numpy array).
            hands: List of hands from process().

        Returns:
            The annotated frame.
        """
        h, w, _ = frame.shape

        for hand in hands:
            # Draw connections
            for start_idx, end_idx in HAND_CONNECTIONS:
                s = hand[start_idx]
                e = hand[end_idx]
                start_pt = (int(s["x"] * w), int(s["y"] * h))
                end_pt = (int(e["x"] * w), int(e["y"] * h))
                cv2.line(frame, start_pt, end_pt, (0, 255, 0), 2)

            # Draw landmark dots
            for lm in hand:
                cx, cy = int(lm["x"] * w), int(lm["y"] * h)
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
                cv2.circle(frame, (cx, cy), 7, (255, 255, 255), 1)

        return frame

    def close(self):
        """Release MediaPipe resources."""
        self.landmarker.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
