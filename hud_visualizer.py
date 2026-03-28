import cv2
import math
import time
import numpy as np
import random
from collections import deque

class Particle:
    """Physics-based spark particle for explosion bursts."""
    def __init__(self, x, y, vx, vy, color, life=20, size=3.0):
        self.x = x
        self.y = y
        self.vx = vx + random.uniform(-1, 1)
        self.vy = vy + random.uniform(-1, 1)
        self.life = float(life)
        self.max_life = float(life)
        self.color = color
        self.size = size

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.90
        self.vy *= 0.90
        self.vy += 0.5  # Gravity
        self.life -= 1
        return self.life > 0

    def draw(self, canvas):
        if self.life <= 0: return
        alpha = self.life / self.max_life
        r = int(self.size * alpha)
        if r > 0:
            cv2.circle(canvas, (int(self.x), int(self.y)), r, self.color, -1)


class HUDVisualizer:
    """Pro-level Cyberpunk Interactive Intelligence visualizer."""

    def __init__(self):
        # Cyberpunk Neon Theme Colors (BGR)
        self.c_neon_blue  = (255, 255, 0)     # Glowing Cyan (Close)
        self.c_neon_pink  = (200, 50, 255)    # Electric Magenta (Medium)
        self.c_neon_green = (100, 255, 100)   # Action Green
        self.c_alert_red  = (50, 50, 255)     # Explosion Red (Far)
        self.c_white      = (255, 255, 255)
        self.c_ui_bg      = (20, 10, 10)      # Deep transparent BG
        
        self.start_time = time.time()
        
        # State Machine memory
        self.current_state = "OPEN HAND"
        self.current_vfx_mode = "OPEN HAND"
        self.last_state = "OPEN HAND"
        self.state_change_time = 0
        
        # Interaction Timer metrics
        self.pinch_start_time = None
        self.pinch_elapsed = 0.0
        self.pinch_center_history = deque(maxlen=20)
        self.stability_score = 100
        
        # Advanced Physics Metrics
        self.light_trail = deque(maxlen=40)
        self.current_depth = 0
        
        # Effects
        self.particles = []

    def draw(self, frame, hands, fps=0):
        h, w, _ = frame.shape
        
        # Layers for professional compositing
        overlay = np.zeros_like(frame)     # For glowing effects and strokes
        ui_overlay = np.zeros_like(frame)  # For semi-transparent HUD panels

        # Process gestures and interaction intelligence per hand
        for hand in hands:
            self._process_gesture_intelligence(overlay, hand, w, h)
            self._draw_cyber_mesh(overlay, hand, w, h)
            self._draw_finger_distances(overlay, hand, w, h)
            self._draw_fingertip_shapes(overlay, hand, self.current_vfx_mode, w, h)
            self._draw_edge_shapes_and_sparkles(overlay, hand, self.current_vfx_mode, w, h)

        # NEW: Dual Hand Lightning Tether Physics
        if len(hands) == 2:
            ix1, iy1 = int(hands[0][8]["x"] * w), int(hands[0][8]["y"] * h)
            ix2, iy2 = int(hands[1][8]["x"] * w), int(hands[1][8]["y"] * h)
            dist_hands = math.hypot(ix2 - ix1, iy2 - iy1)
            
            if dist_hands < 500: # Tether threshold
                # Draw energy tether
                num_zigs = 10
                pts = [(ix1, iy1)]
                for i in range(1, num_zigs):
                    fraction = i / num_zigs
                    # Stretch physics: more chaotic when further apart
                    chaos = int((dist_hands / 500.0) * 40)
                    px = ix1 + (ix2 - ix1) * fraction + random.randint(-chaos, chaos)
                    py = iy1 + (iy2 - iy1) * fraction + random.randint(-chaos, chaos)
                    pts.append((px, py))
                pts.append((ix2, iy2))
                
                # Color shifts based on tension: Blue (close) to Red (far)
                r_color = int(255 * (dist_hands / 500.0))
                b_color = int(255 * (1.0 - dist_hands / 500.0))
                tether_color = (b_color, 50, r_color) 
                
                for i in range(len(pts)-1):
                    cv2.line(overlay, (int(pts[i][0]), int(pts[i][1])), (int(pts[i+1][0]), int(pts[i+1][1])), tether_color, max(1, int(4 - (dist_hands/150))), cv2.LINE_AA)

        # Draw Static UI Panel on the side
        self._draw_transparent_panels(ui_overlay, w, h)
        
        # New: Draw FPS Counter
        self._draw_fps_counter(ui_overlay, w, h, fps)

        # Update and render active explosive particles
        alive_particles = []
        for p in self.particles:
            if p.update():
                p.draw(overlay)
                alive_particles.append(p)
        self.particles = alive_particles

        # Compositing engine
        # Step 1: Add dark transparent UI panels to the base frame
        frame = cv2.addWeighted(frame, 1.0, ui_overlay, 0.8, 0)
        
        # Step 2: Overlay sharp geometry
        frame = cv2.addWeighted(frame, 1.0, overlay, 1.0, 0)
        
        # Step 3: Overlay heavy Gaussian blur for neon light bleeding
        glow = cv2.GaussianBlur(overlay, (21, 21), 0)
        frame = cv2.addWeighted(frame, 1.0, glow, 0.7, 0)

        return frame

    def _process_gesture_intelligence(self, canvas, hand, w, h):
        """Analyzes distances to classify gestures and trigger smart VFX & HCI timers."""
        # Focus interaction between thumb (4) and index (8)
        tx, ty = int(hand[4]["x"] * w), int(hand[4]["y"] * h)
        ix, iy = int(hand[8]["x"] * w), int(hand[8]["y"] * h)
        
        cx, cy = (tx + ix) // 2, (ty + iy) // 2
        dist = math.hypot(ix - tx, iy - ty)
        
        # Finger Extension Analysis
        wx, wy = hand[0]["x"], hand[0]["y"]
        tips = [4, 8, 12, 16, 20]
        mips = [2, 6, 10, 14, 18] # Middle/base joints to compare distance
        
        fingers_up = []
        for i in range(5):
            d_tip = math.hypot(hand[tips[i]]["x"] - wx, hand[tips[i]]["y"] - wy)
            d_mip = math.hypot(hand[mips[i]]["x"] - wx, hand[mips[i]]["y"] - wy)
            fingers_up.append(d_tip > d_mip)
            
        up_count = sum(fingers_up)
        
        # Classification Engine
        if dist < 40 and fingers_up[2] and fingers_up[3] and fingers_up[4]:
            state = "OK GESTURE"
            color = self.c_neon_blue
        elif dist < 40:
            state = "PINCH DETECTED"
            color = self.c_neon_blue
        elif up_count == 0:
            state = "CLOSED FIST"
            color = self.c_alert_red
        elif up_count == 5:
            state = "OPEN HAND"
            color = self.c_neon_green
        elif fingers_up[1] and fingers_up[2] and not fingers_up[3] and not fingers_up[4]:
            state = "PEACE SIGN [2]"
            color = self.c_neon_pink
        elif fingers_up[1] and not fingers_up[2] and not fingers_up[3] and not fingers_up[4]:
            state = "POINTING [1]"
            color = self.c_neon_pink
        elif fingers_up[0] and not fingers_up[1] and not fingers_up[2] and not fingers_up[3] and not fingers_up[4]:
            state = "THUMBS UP"
            color = self.c_neon_green
        elif fingers_up[1] and fingers_up[4] and not fingers_up[2] and not fingers_up[3]:
            state = "ROCK ON"
            color = self.c_neon_pink
        else:
            state = f"{up_count} FINGERS ACTIVE"
            color = self.c_neon_pink if dist < 120 else self.c_neon_green

        vfx_mode = "OPEN HAND"
        if state in ["PINCH DETECTED", "OK GESTURE"]:
            vfx_mode = "PINCH DETECTED"
        elif dist < 140 or state in ["CLOSED FIST", "POINTING [1]", "PEACE SIGN [2]", "ROCK ON"]:
            vfx_mode = "HOLD GESTURE"

        # ADVANCED PHYSICS 1: Light Painting Trajectory
        if state == "POINTING [1]":
            self.light_trail.append((ix, iy))
        else:
            if len(self.light_trail) > 0:
                self.light_trail.popleft() # slowly fade trail if not pointing

        # Draw the neon Light Trail
        if len(self.light_trail) > 1:
            for i in range(1, len(self.light_trail)):
                thickness = max(1, int((i / len(self.light_trail)) * 12))
                cv2.line(canvas, self.light_trail[i-1], self.light_trail[i], self.c_neon_blue, thickness, cv2.LINE_AA)

        # ADVANCED PHYSICS 2: Z-Axis Depth Estimation (Bounding Box Area)
        # Approximate width of hand
        hx_min = min([int(hand[p]["x"] * w) for p in range(21)])
        hx_max = max([int(hand[p]["x"] * w) for p in range(21)])
        hy_min = min([int(hand[p]["y"] * h) for p in range(21)])
        hy_max = max([int(hand[p]["y"] * h) for p in range(21)])
        
        area = (hx_max - hx_min) * (hy_max - hy_min)
        # Map area roughly 10000(far) to 60000(close) -> Depth 0 to 100%
        self.current_depth = max(0, min(100, int((area - 5000) / 400)))

        # Trap State Transitions for Animation
        if state != self.current_state:
            self.last_state = self.current_state
            self.current_state = state
            self.current_vfx_mode = vfx_mode
            self.state_change_time = time.time()
            
            # Reset pinch interaction properties
            if vfx_mode == "PINCH DETECTED":
                self.pinch_start_time = time.time()
                self.pinch_center_history.clear()
            else:
                self.pinch_start_time = None
                self.pinch_elapsed = 0.0

        # Rendering Smart Visual Effects (VFX) based on state
        self._render_vfx_for_state(canvas, vfx_mode, tx, ty, ix, iy, cx, cy, dist)

        # Rendering Animated State Floating Text (more minimal, positioned near wrist to avoid clutter)
        t_since_change = time.time() - self.state_change_time
        scale = max(0.5, 0.9 - (t_since_change * 2)) # Subtle digital pop
        wx, wy = int(hand[0]["x"] * w), int(hand[0]["y"] * h)
        cv2.putText(canvas, f"[{state}]", (wx - 40, wy - 40), cv2.FONT_HERSHEY_DUPLEX, scale, color, 1, cv2.LINE_AA)

    def _render_vfx_for_state(self, canvas, state, tx, ty, ix, iy, cx, cy, dist):
        """Generates specific VFX and HCI logic based on the detected state."""
        if state == "PINCH DETECTED":
            # 🔵 VFX: Glowing Orb with pulsing core
            pulse = int(abs(math.sin(time.time() * 8)) * 5)
            cv2.circle(canvas, (cx, cy), 15 + pulse, self.c_neon_blue, -1)
            cv2.circle(canvas, (cx, cy), 25, self.c_white, 2)
            
            # Interaction Timer & HCI Stability Logic
            if self.pinch_start_time is None:
                self.pinch_start_time = time.time()
                
            self.pinch_elapsed = time.time() - self.pinch_start_time
            self.pinch_center_history.append((cx, cy))
            
            # Compute stability: measuring Euclidean variance of hold center
            if len(self.pinch_center_history) >= 2:
                pts = np.array(self.pinch_center_history)
                centroid = np.mean(pts, axis=0)
                variance = np.mean(np.linalg.norm(pts - centroid, axis=1))
                # Map 0 variance to 100%, high variance to 0%
                self.stability_score = max(0, min(100, int(100 - (variance * 4))))
                
            # Circular Progress Bar
            # Represent 3 seconds as a full circle, repeats
            angle = int((self.pinch_elapsed % 3.0) / 3.0 * 360)
            cv2.ellipse(canvas, (cx, cy), (40, 40), -90, 0, angle, self.c_neon_green, 3)
            
            # Side UI next to orb
            cv2.putText(canvas, f"{self.pinch_elapsed:.2f}s", (cx + 50, cy - 10), cv2.FONT_HERSHEY_PLAIN, 1.2, self.c_neon_green, 1)
            cv2.putText(canvas, f"STABILITY: {self.stability_score}%", (cx + 50, cy + 10), cv2.FONT_HERSHEY_PLAIN, 0.9, self.c_neon_blue, 1)

        elif state == "HOLD GESTURE":
            # ⚡ VFX: Electric Particles between fingertips
            num_zigs = 6
            pts = [(tx, ty)]
            for i in range(1, num_zigs):
                fraction = i / num_zigs
                px = tx + (ix - tx) * fraction + random.randint(-15, 15)
                py = ty + (iy - ty) * fraction + random.randint(-15, 15)
                pts.append((px, py))
            pts.append((ix, iy))
            
            # Draw the lightning bolt
            for i in range(len(pts)-1):
                cv2.line(canvas, (int(pts[i][0]), int(pts[i][1])), (int(pts[i+1][0]), int(pts[i+1][1])), self.c_neon_pink, 2)
                
            # Central charging orb
            cv2.circle(canvas, (cx, cy), 8, self.c_neon_pink, -1)
            cv2.putText(canvas, f"LINKING: {dist:.0f}mm", (cx + 20, cy), cv2.FONT_HERSHEY_PLAIN, 0.8, self.c_neon_pink, 1)

        elif state == "OPEN HAND":
            # 💥 VFX: Explosion bursts (Particles emit from tips)
            for _ in range(3):
                # Throw sparks from both thumb and index
                self.particles.append(Particle(tx, ty, random.uniform(-8,8), random.uniform(-8,8), self.c_alert_red, life=15, size=random.uniform(2,5)))
                self.particles.append(Particle(ix, iy, random.uniform(-8,8), random.uniform(-8,8), self.c_alert_red, life=15, size=random.uniform(2,5)))

    def _draw_cyber_mesh(self, canvas, hand, w, h):
        """Draws glowing structural wireframe for the full hand."""
        # Draw connections for palm and key knuckle lines (subtle dark cyan)
        for connection in [(0, 5), (5, 9), (9, 13), (13, 17), (0, 17)]:
            start = hand[connection[0]]
            end = hand[connection[1]]
            p1 = (int(start["x"] * w), int(start["y"] * h))
            p2 = (int(end["x"] * w), int(end["y"] * h))
            cv2.line(canvas, p1, p2, (80, 80, 40), 1, cv2.LINE_AA)

    def _draw_transparent_panels(self, ui_canvas, w, h):
        """Renders the sleek HUD info panels on the left side of the screen, adaptive to resolution."""
        # Scalable UI Sizing (e.g., panel is 40% of standard width)
        panel_x = int(w * 0.03) # 3% from left
        panel_y = int(h * 0.08) # 8% from top
        panel_w = int(w * 0.35) # 35% of width
        panel_h = int(h * 0.40) # 40% of height
        
        # Soft dark background
        cv2.rectangle(ui_canvas, (panel_x, panel_y), (panel_x + panel_w, panel_y + panel_h), self.c_ui_bg, -1)
        
        # Techy corner accents
        accent = 30
        cv2.line(ui_canvas, (panel_x, panel_y), (panel_x + accent, panel_y), self.c_neon_blue, 2)
        cv2.line(ui_canvas, (panel_x, panel_y), (panel_x, panel_y + accent), self.c_neon_blue, 2)
        cv2.line(ui_canvas, (panel_x + panel_w, panel_y + panel_h), (panel_x + panel_w - accent, panel_y + panel_h), self.c_neon_blue, 2)
        cv2.line(ui_canvas, (panel_x + panel_w, panel_y + panel_h), (panel_x + panel_w, panel_y + panel_h - accent), self.c_neon_blue, 2)

        # Content Layer - Scalable Fonts
        col_x = panel_x + 15
        f_scale = w / 1280.0 # Baseline at 720p
        
        cv2.putText(ui_canvas, "SYS LOGISTICS [ONLINE]", (col_x, panel_y + int(25 * f_scale + 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.45 * f_scale + 0.1, self.c_white, 1, cv2.LINE_AA)
        cv2.line(ui_canvas, (col_x, panel_y + 35), (col_x + int(120 * f_scale), panel_y + 35), self.c_neon_pink, 1)
        
        uptime = time.time() - self.start_time
        mins, secs = divmod(uptime, 60)
        cv2.putText(ui_canvas, f"UPTIME: {int(mins):02d}:{secs:05.2f}", (col_x, panel_y + int(60 * f_scale)), cv2.FONT_HERSHEY_PLAIN, 0.9 * f_scale + 0.2, self.c_neon_green, 1, cv2.LINE_AA)
        
        cv2.putText(ui_canvas, "STATE INTERLOCK:", (col_x, panel_y + int(90 * f_scale)), cv2.FONT_HERSHEY_PLAIN, 0.8 * f_scale + 0.2, self.c_white, 1, cv2.LINE_AA)
        cv2.putText(ui_canvas, f"> {self.current_state}", (col_x, panel_y + int(115 * f_scale)), cv2.FONT_HERSHEY_SIMPLEX, 0.55 * f_scale + 0.1, self.c_neon_blue, 1, cv2.LINE_AA)
        
        cv2.putText(ui_canvas, f"Z-DEPTH VAL: {self.current_depth}%", (col_x, panel_y + int(140 * f_scale)), cv2.FONT_HERSHEY_PLAIN, 0.8 * f_scale + 0.2, self.c_neon_pink, 1, cv2.LINE_AA)
        
        if self.current_vfx_mode == "PINCH DETECTED":
            cv2.putText(ui_canvas, f"STABILITY: {self.stability_score}%", (col_x, panel_y + int(170 * f_scale)), cv2.FONT_HERSHEY_PLAIN, 0.9 * f_scale + 0.2, self.c_neon_green, 1, cv2.LINE_AA)
            cv2.line(ui_canvas, (col_x, panel_y + int(180 * f_scale)), (col_x + int(self.stability_score * 1.5 * f_scale), panel_y + int(180 * f_scale)), self.c_neon_green, 2)
        else:
            cv2.putText(ui_canvas, "STABILITY: STANDBY", (col_x, panel_y + int(170 * f_scale)), cv2.FONT_HERSHEY_PLAIN, 0.9 * f_scale + 0.2, self.c_alert_red, 1, cv2.LINE_AA)

    def _draw_fps_counter(self, ui_canvas, w, h, fps):
        """Draws a dedicated FPS counter in the top-left area, highly legible."""
        f_scale = w / 800.0 # Scale baseline
        
        # Position slightly offset to avoid rounded corners of website video container
        fps_x = int(w * 0.03 + 15)
        fps_y = int(h * 0.08 + 15) # Inside the logistics panel
        
        fps_text = f"FPS: {int(fps)}"
        cv2.putText(ui_canvas, fps_text, (int(w * 0.04), int(h * 0.08 - 15)), cv2.FONT_HERSHEY_DUPLEX, 0.8 * f_scale, self.c_neon_green, 1, cv2.LINE_AA)

    def _draw_finger_distances(self, canvas, hand, w, h):
        """Draws dynamic distance measurements between adjacent fingertips in pseudo-mm."""
        # Only draw distances if fingers are reasonably spread out to avoid text bunching
        tips = [4, 8, 12, 16, 20]
        for i in range(len(tips) - 1):
            p1 = hand[tips[i]]
            p2 = hand[tips[i + 1]]
            
            x1, y1 = int(p1["x"] * w), int(p1["y"] * h)
            x2, y2 = int(p2["x"] * w), int(p2["y"] * h)
            
            dist_px = math.hypot(x2 - x1, y2 - y1)
            if dist_px < 40:  # Skip drawing text if fingers are touching/clustered
                continue
                
            dist_mm = int(dist_px * 0.45) 
            mx, my = (x1 + x2) // 2, (y1 + y2) // 2
            
            # Draw structural measuring line (subtle)
            cv2.line(canvas, (x1, y1), (x2, y2), (100, 100, 0), 1, cv2.LINE_AA)
            
            # Render the measurement text extremely cleanly
            cv2.putText(canvas, f"{dist_mm}mm", (mx - 15, my - 5), cv2.FONT_HERSHEY_PLAIN, 0.8, (200, 200, 200), 1, cv2.LINE_AA)

    def _draw_fingertip_shapes(self, canvas, hand, state, w, h):
        """Draws dynamic shapes and sparkles on fingertips based on current gesture state."""
        tips = [4, 8, 12, 16, 20] # Thumb, Index, Middle, Ring, Pinky
        
        for tip_idx in tips:
            tx = int(hand[tip_idx]["x"] * w)
            ty = int(hand[tip_idx]["y"] * h)
            
            if state == "PINCH DETECTED":
                # Draw pulsating circle
                size = 6 + int(math.sin(time.time() * 10) * 3)
                cv2.circle(canvas, (tx, ty), size, self.c_neon_blue, -1)
                cv2.circle(canvas, (tx, ty), size + 4, self.c_white, 1)
                # Emit small sparkles
                if random.random() < 0.1:
                    self.particles.append(Particle(tx, ty, random.uniform(-2,2), random.uniform(-2,2), self.c_neon_blue, life=10, size=2))
                    
            elif state == "HOLD GESTURE":
                # Draw spinning triangles
                size = 8
                angle = time.time() * 5
                pts = []
                for i in range(3):
                    a = angle + i * (2 * math.pi / 3)
                    px = tx + int(math.cos(a) * size)
                    py = ty + int(math.sin(a) * size)
                    pts.append([px, py])
                pts = np.array(pts, np.int32)
                cv2.polylines(canvas, [pts], True, self.c_neon_pink, 2)
                # Small energy sparkles
                if random.random() < 0.05:
                    self.particles.append(Particle(tx, ty, random.uniform(-1,1), random.uniform(-1,1), self.c_neon_pink, life=12, size=random.uniform(1,3)))
                
            elif state == "OPEN HAND":
                # Draw rotating stars
                size = 6
                pts = []
                for i in range(10):
                    r = size if i % 2 == 0 else size // 2
                    a = i * (math.pi / 5) - (time.time() * 2)
                    px = tx + int(math.cos(a) * r)
                    py = ty + int(math.sin(a) * r)
                    pts.append([px, py])
                pts = np.array(pts, np.int32)
                cv2.fillPoly(canvas, [pts], self.c_neon_green)
                # Passive falling sparkles
                if random.random() < 0.05:
                    self.particles.append(Particle(tx, ty, random.uniform(-1,1), random.uniform(0,3), self.c_neon_green, life=15, size=random.uniform(1,3)))

    def _draw_edge_shapes_and_sparkles(self, canvas, hand, state, w, h):
        """Draws dynamic shapes and sparkles on the edges of the hand."""
        # Define edge landmarks (wrist, thumb edge, pinky edge)
        # 0: wrist, 1-3: thumb edge, 17-19: pinky edge
        edges = [0, 1, 2, 3, 17, 18, 19]
        
        for edge_idx in edges:
            tx = int(hand[edge_idx]["x"] * w)
            ty = int(hand[edge_idx]["y"] * h)
            
            if state == "PINCH DETECTED":
                # Draw small pulsating diamond
                size = 3 + int(math.sin(time.time() * 10) * 2)
                pts = np.array([[tx, ty-size], [tx+size, ty], [tx, ty+size], [tx-size, ty]], np.int32)
                cv2.fillPoly(canvas, [pts], self.c_neon_blue)
                # Emit small sparkles
                if random.random() < 0.05:
                    self.particles.append(Particle(tx, ty, random.uniform(-1,1), random.uniform(-1,1), self.c_neon_blue, life=8, size=1.5))
                    
            elif state == "HOLD GESTURE":
                # Draw small spinning squares
                size = 4
                angle = time.time() * 3
                pts = []
                for i in range(4):
                    a = angle + i * (math.pi / 2)
                    px = tx + int(math.cos(a) * size)
                    py = ty + int(math.sin(a) * size)
                    pts.append([px, py])
                pts = np.array(pts, np.int32)
                cv2.polylines(canvas, [pts], True, self.c_neon_pink, 1)
                if random.random() < 0.03:
                    self.particles.append(Particle(tx, ty, random.uniform(-0.5,0.5), random.uniform(-0.5,0.5), self.c_neon_pink, life=10, size=random.uniform(1,2)))
                
            elif state == "OPEN HAND":
                # Draw small hollow circles
                size = 4
                cv2.circle(canvas, (tx, ty), size, self.c_neon_green, 1)
                # Passive falling sparkles
                if random.random() < 0.03:
                    self.particles.append(Particle(tx, ty, random.uniform(-0.5,0.5), random.uniform(0,2), self.c_neon_green, life=10, size=random.uniform(1,2)))

