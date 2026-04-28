"""
main.py - Flask backend optimized for Render.com

This version serves the Hand Tracking dashboard directly without authentication
and uses client-side (browser) MediaPipe for hand tracking to remain 
compatible with cloud environments.
"""

import os
from flask import Flask, jsonify, render_template

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "handtrack-vision-2026-direct")
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0


@app.after_request
def add_no_cache_headers(response):
    """Force browsers to fetch the latest HTML/JS/CSS during local iteration."""
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# --- Routes ---
@app.route("/")
def index():
    """Main dashboard entrypoint (No Login)."""
    return render_template("index.html")

@app.route("/health")
def health():
    """Render.com deployment health check."""
    return jsonify(status="ok", deployment="render")

@app.route("/runtime-status")
def runtime_status():
    """Reports the current system status to the frontend."""
    return jsonify(
        status="ok",
        mode="client-side-tracking",
        message="Web-based Hand Tracking is active. No login required."
    )

def main():
    # Use PORT from environment (default to 5000)
    port = int(os.environ.get("PORT", "5000"))
    
    print("=" * 55, flush=True)
    print(f"  HandTrack Intelligence — Port {port}", flush=True)
    print("  Mode: Direct Access (No Login Required)", flush=True)
    print("  Tracking: Client-Side (MediaPipe JS)", flush=True)
    print("=" * 55, flush=True)
    
    app.run(host="0.0.0.0", port=port, debug=False)

if __name__ == "__main__":
    main()
