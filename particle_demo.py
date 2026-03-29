"""
particle_demo.py

Local real-time demo:
MediaPipe hand tracking + per-finger glowing particle rain.
"""

from __future__ import annotations

import time

import cv2

from finger_particle_system import FingerParticleSystem
from hand_tracker import HandTracker


def draw_finger_color_legend(frame, finger_colors):
    x = 12
    y = 34
    cv2.putText(frame, "Finger Colors", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (230, 230, 230), 1, cv2.LINE_AA)
    y += 22

    for name, color in finger_colors.items():
        cv2.circle(frame, (x + 6, y - 5), 6, color, -1, cv2.LINE_AA)
        cv2.putText(
            frame,
            name.upper(),
            (x + 18, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (220, 220, 220),
            1,
            cv2.LINE_AA,
        )
        y += 20


def main() -> None:
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam.")

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    particles = FingerParticleSystem(
        max_particles=2400,
        emit_rate=24.0,
        gravity=1300.0,
        drag=0.94,
        horizontal_speed=90.0,
        vertical_speed=190.0,
    )

    with HandTracker(max_num_hands=2) as tracker:
        prev_time = time.perf_counter()
        fps = 0.0

        while True:
            ok, frame = cap.read()
            if not ok:
                break

            frame = cv2.flip(frame, 1)
            now = time.perf_counter()
            dt = max(1.0 / 240.0, min(0.05, now - prev_time))
            prev_time = now

            hands = tracker.process(frame)
            tracker.draw_on_frame(frame, hands)
            particles.step(frame, hands, dt)

            # Smoothed FPS
            current_fps = 1.0 / dt
            fps = current_fps if fps == 0.0 else (fps * 0.9 + current_fps * 0.1)
            cv2.putText(
                frame,
                f"FPS: {fps:.1f}",
                (frame.shape[1] - 140, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (220, 255, 220),
                2,
                cv2.LINE_AA,
            )

            draw_finger_color_legend(frame, particles.finger_colors)
            cv2.imshow("Finger Particle System Demo", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == 27 or key == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

