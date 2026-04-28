# Real-Time Hand Tracking Visualization

Real-time hand tracking dashboard powered by MediaPipe, OpenCV, Flask, and OSC.

## Features

- Track up to two hands with 21 landmarks each.
- Stream live camera frames into the web dashboard.
- Send OSC landmark data to TouchDesigner or other OSC receivers.
- Show a local preview window with HUD overlays and live FPS.

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Open `http://localhost:5000`.

## Project Files

- `main.py`: Flask dashboard and tracking loop.
- `hand_tracker.py`: MediaPipe hand landmark detection.
- `hud_visualizer.py`: HUD drawing and analytics overlay.
- `osc_sender.py`: OSC output for hand data.
- `templates/index.html`: Main dashboard UI.
