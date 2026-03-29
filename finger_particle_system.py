"""
finger_particle_system.py

High-performance fingertip particle engine for OpenCV + MediaPipe pipelines.
"""

from __future__ import annotations

import colorsys
import random
from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, Mapping, Sequence, Tuple

import cv2
import numpy as np


# MediaPipe fingertip landmark ids.
FINGERTIP_IDS: Dict[str, int] = {
    "thumb": 4,
    "index": 8,
    "middle": 12,
    "ring": 16,
    "pinky": 20,
}


@dataclass(slots=True)
class FingerParticle:
    """Single particle with velocity and lifetime."""

    x: float
    y: float
    vx: float
    vy: float
    life: float
    max_life: float
    size: float
    color: Tuple[int, int, int]  # BGR


class FingerParticleSystem:
    """
    Real-time particle system where each fingertip emits glowing particles.

    Key properties:
    - Each finger gets one random color at startup (stable, no flicker).
    - Continuous emission from all fingertips.
    - Gravity-based downward motion.
    - Per-particle fade and automatic cleanup.
    - Glow + core rendering for a futuristic look.
    - Particle cap and deque storage for stable performance.
    """

    def __init__(
        self,
        max_particles: int = 2200,
        emit_rate: float = 22.0,
        gravity: float = 1200.0,
        drag: float = 0.93,
        horizontal_speed: float = 95.0,
        vertical_speed: float = 180.0,
        min_life: float = 0.35,
        max_life: float = 0.95,
        min_size: float = 1.7,
        max_size: float = 4.2,
        glow_scale: float = 2.8,
        color_jitter: int = 22,
        seed: int | None = None,
    ) -> None:
        self.max_particles = max_particles
        self.emit_rate = emit_rate
        self.gravity = gravity
        self.drag = drag
        self.horizontal_speed = horizontal_speed
        self.vertical_speed = vertical_speed
        self.min_life = min_life
        self.max_life = max_life
        self.min_size = min_size
        self.max_size = max_size
        self.glow_scale = glow_scale
        self.color_jitter = color_jitter

        self._rng = random.Random(seed)
        self.particles: Deque[FingerParticle] = deque()
        self._emit_accumulator: Dict[Tuple[int, str], float] = {}
        self.finger_colors = self._generate_stable_finger_colors()

    def _generate_stable_finger_colors(self) -> Dict[str, Tuple[int, int, int]]:
        """
        Generate one random-but-stable color per finger.

        Blue/cyan hues are intentionally avoided.
        """
        colors: Dict[str, Tuple[int, int, int]] = {}
        used_hues: list[float] = []

        for finger_name in FINGERTIP_IDS:
            hue = self._sample_non_blue_hue(used_hues)
            sat = self._rng.uniform(0.78, 1.0)
            val = self._rng.uniform(0.88, 1.0)
            r, g, b = colorsys.hsv_to_rgb(hue, sat, val)
            colors[finger_name] = (int(b * 255), int(g * 255), int(r * 255))
            used_hues.append(hue)

        return colors

    def _sample_non_blue_hue(self, used_hues: Sequence[float]) -> float:
        # Favor warm + neon greens. Avoid blue/cyan/pure-blue sector.
        for _ in range(200):
            if self._rng.random() < 0.7:
                hue = self._rng.uniform(0.0, 0.40)
            else:
                hue = self._rng.uniform(0.90, 1.0)
            if all(self._hue_distance(hue, prev) >= 0.08 for prev in used_hues):
                return hue
        return self._rng.uniform(0.0, 0.4)

    @staticmethod
    def _hue_distance(a: float, b: float) -> float:
        diff = abs(a - b)
        return min(diff, 1.0 - diff)

    def _vary_color(self, base_color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        def clamp(v: int) -> int:
            return max(0, min(255, v))

        return (
            clamp(base_color[0] + self._rng.randint(-self.color_jitter, self.color_jitter)),
            clamp(base_color[1] + self._rng.randint(-self.color_jitter, self.color_jitter)),
            clamp(base_color[2] + self._rng.randint(-self.color_jitter, self.color_jitter)),
        )

    def _append_particle(self, particle: FingerParticle) -> None:
        # Keep memory bounded and avoid lag spikes.
        overflow = len(self.particles) - self.max_particles + 1
        for _ in range(max(0, overflow)):
            self.particles.popleft()
        self.particles.append(particle)

    def _spawn_particle(self, x: float, y: float, finger_name: str) -> None:
        base_color = self.finger_colors[finger_name]
        particle_color = self._vary_color(base_color)

        vx = self._rng.uniform(-self.horizontal_speed, self.horizontal_speed)
        vy = self._rng.uniform(self.vertical_speed * 0.55, self.vertical_speed * 1.35)
        life = self._rng.uniform(self.min_life, self.max_life)
        size = self._rng.uniform(self.min_size, self.max_size)

        self._append_particle(
            FingerParticle(
                x=x + self._rng.uniform(-2.0, 2.0),
                y=y + self._rng.uniform(-2.0, 2.0),
                vx=vx,
                vy=vy,
                life=life,
                max_life=life,
                size=size,
                color=particle_color,
            )
        )

    def emit_from_hands(
        self,
        hands: Sequence[Sequence[Mapping[str, float]]],
        frame_width: int,
        frame_height: int,
        dt: float,
    ) -> None:
        if dt <= 0:
            return

        for hand_idx, hand in enumerate(hands):
            if len(hand) <= 20:
                continue
            for finger_name, tip_idx in FINGERTIP_IDS.items():
                tip = hand[tip_idx]
                tip_x = float(tip["x"]) * frame_width
                tip_y = float(tip["y"]) * frame_height

                key = (hand_idx, finger_name)
                self._emit_accumulator[key] = self._emit_accumulator.get(key, 0.0) + self.emit_rate * dt
                spawn_count = int(self._emit_accumulator[key])
                if spawn_count <= 0:
                    continue
                self._emit_accumulator[key] -= spawn_count

                for _ in range(spawn_count):
                    self._spawn_particle(tip_x, tip_y, finger_name)

    def update(self, dt: float, frame_width: int, frame_height: int) -> None:
        if not self.particles or dt <= 0:
            return

        drag_factor = self.drag ** (dt * 60.0)
        bounds_margin = 30
        alive: Deque[FingerParticle] = deque()

        for p in self.particles:
            p.vx *= drag_factor
            p.vy = (p.vy * drag_factor) + (self.gravity * dt)
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.life -= dt

            if (
                p.life > 0.0
                and -bounds_margin <= p.x <= frame_width + bounds_margin
                and -bounds_margin <= p.y <= frame_height + bounds_margin
            ):
                alive.append(p)

        self.particles = alive

    def render(self, frame: np.ndarray) -> np.ndarray:
        if not self.particles:
            return frame

        h, w = frame.shape[:2]
        glow_layer = np.zeros_like(frame)
        core_layer = np.zeros_like(frame)

        for p in self.particles:
            alpha = p.life / p.max_life
            if alpha <= 0:
                continue

            x = int(round(p.x))
            y = int(round(p.y))
            if x < 0 or x >= w or y < 0 or y >= h:
                continue

            glow_radius = max(2, int(round(p.size * self.glow_scale)))
            core_radius = max(1, int(round(p.size)))

            glow_alpha = 0.38 * alpha
            glow_color = tuple(int(channel * glow_alpha) for channel in p.color)
            core_color = tuple(int(channel * alpha) for channel in p.color)

            cv2.circle(glow_layer, (x, y), glow_radius, glow_color, -1, cv2.LINE_AA)
            cv2.circle(core_layer, (x, y), core_radius, core_color, -1, cv2.LINE_AA)

        cv2.add(frame, glow_layer, dst=frame)
        cv2.add(frame, core_layer, dst=frame)
        return frame

    def step(
        self,
        frame: np.ndarray,
        hands: Sequence[Sequence[Mapping[str, float]]],
        dt: float,
    ) -> np.ndarray:
        """Convenience helper: emit -> update -> render in one call."""
        h, w = frame.shape[:2]
        self.emit_from_hands(hands, w, h, dt)
        self.update(dt, w, h)
        return self.render(frame)

    def reset(self) -> None:
        self.particles.clear()
        self._emit_accumulator.clear()

