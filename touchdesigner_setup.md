# TouchDesigner Setup Guide

This guide explains how to receive hand tracking data from the Python application
in **TouchDesigner** via OSC.

---

## 1. Create an OSC In CHOP

1. Open TouchDesigner
2. Press **Tab** → search for **OSC In** → place the CHOP
3. In the parameters panel, set:
   - **Protocol**: UDP
   - **Port**: `9000` (must match `--port` argument in `main.py`)
   - **Active**: On

You should immediately see channels appearing when the Python script is running
and a hand is visible.

---

## 2. Incoming OSC Channels

The Python app sends the following OSC addresses:

| Address                           | Arguments     | Description                    |
| --------------------------------- | ------------- | ------------------------------ |
| `/hand/count`                     | `int`         | Number of hands detected (0–2) |
| `/hand/<H>/detected`             | `int` (0/1)   | Whether hand H is visible      |
| `/hand/<H>/landmark/<L>`         | `float × 3`   | x, y, z of landmark L          |
| `/hand/<H>/wrist`                | `float × 3`   | Wrist position shortcut        |
| `/hand/<H>/thumb_tip`            | `float × 3`   | Thumb tip shortcut             |
| `/hand/<H>/index_tip`            | `float × 3`   | Index finger tip shortcut      |
| `/hand/<H>/middle_tip`           | `float × 3`   | Middle finger tip shortcut     |
| `/hand/<H>/ring_tip`             | `float × 3`   | Ring finger tip shortcut       |
| `/hand/<H>/pinky_tip`            | `float × 3`   | Pinky tip shortcut             |

- `<H>` = hand index (0 or 1)
- `<L>` = landmark index (0–20)
- x, y are normalized 0.0–1.0; z is depth relative to wrist

---

## 3. Example: Drive a Sphere with Index Finger

### Step-by-step

1. **OSC In CHOP** → receiving data on port 9000
2. **Select CHOP** → filter channel: `hand/0/index_tip*`
3. **Math CHOP** → remap x from 0–1 to -5 to 5 (your scene range)
4. **Sphere SOP** → create a sphere
5. **Geometry COMP** → wrap the sphere
6. In the Geometry's Transform tab:
   - **tx**: Reference `select1:chan("hand/0/index_tip:0")`
   - **ty**: Reference `select1:chan("hand/0/index_tip:1")` (invert if needed)
   - **tz**: Reference `select1:chan("hand/0/index_tip:2")`

The sphere will now follow your index finger in real-time!

---

## 4. Tips

- **Latency**: OSC over localhost (127.0.0.1) is near-instant
- **Frame rate**: The Python side runs at ~30 FPS; TouchDesigner will interpolate
- **Multiple machines**: Use `--ip <TouchDesigner-PC-IP>` to send across a network
- **Smoothing**: Add a **Lag CHOP** or **Filter CHOP** after OSC In for smoother motion
- **Scale**: Use a **Math CHOP** to remap 0–1 values to your scene's coordinate space
