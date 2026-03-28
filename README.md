# 🖐️ Real-Time Hand Tracking Visualization using MediaPipe & TouchDesigner
Elevate your vision experience with real-time hand tracking, gesture-driven OSC streaming, and a cinematic authenticated dashboard. Powered by **MediaPipe**, **OpenCV**, and **Flask**.

![Liquid Intelligence](https://img.shields.io/badge/Status-Premium-gold?style=for-the-badge)
![MediaPipe](https://img.shields.io/badge/AI-MediaPipe-blue?style=for-the-badge)
![Flask](https://img.shields.io/badge/Web-Flask-lightgrey?style=for-the-badge)

---

## ✨ Features

- **21-Landmark Precision**: Multi-hand tracking with 99% accuracy via Google MediaPipe.
- **Cinematic Access Portal**: A premium, Three.js-powered login/register experience featuring a refractive animated "Jelly" ball background.
- **Secure Authentication**: OTP-based email verification, bcrypt password hashing, and session-gated dashboard access.
- **Optimized Video Pipeline**: Pre-encoded JPEG streaming for high FPS (30+) and ultra-low latency.
- **OSC Integration**: Seamlessly stream hand coordinates to **TouchDesigner**, **Ableton**, or **Unity**.

---

## 🔒 Security First

This project is built with security in mind. 
- **Environment Variables**: Sensitive data (Email credentials, Secret Keys) are stored in `.env`.
- **Git Protection**: A `.gitignore` is included to ensure your private `.env` and `users.xlsx` database are **never** committed to GitHub.

---

## 📦 Quick Start

### 1. Installation
```powershell
# Clone the repository
git clone https://github.com/Srishylam-code/hand-track-intelligence.git
cd "C programming"

# Setup virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file in the root directory:
```env
MAIL_USER=your-email@gmail.com
MAIL_PASSWORD=your-app-password
SECRET_KEY=generate-a-random-long-string
```

### 3. Usage
```powershell
# Run the intelligence engine
python main.py
```

Access the portal at `http://localhost:5000`.

---

## 📁 Project Architecture

- `main.py`: The central engine (Web Server + AI Tracking Loop).
- `hand_tracker.py`: Specialized MediaPipe hand detection wrapper.
- `hud_visualizer.py`: Resolution-aware HUD with real-time analytics.
- `auth_app.py`: Scalable authentication logic (Login/Signup/OTP).
- `templates/`: Premium glassmorphic HTML/CSS/JS frontend.

---

## 📄 License
This project is open-source. Created for creators, designers, and vision engineers.

