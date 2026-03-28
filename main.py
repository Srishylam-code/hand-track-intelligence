"""
main.py - Flask backend for Render-friendly deployment.

This entrypoint avoids local webcam, GUI, and preview features so it can run
in headless cloud environments such as Render.
"""

import os

from flask import Flask, jsonify, render_template


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify(status="ok")


@app.route("/runtime-status")
def runtime_status():
    return jsonify(
        status="ok",
        mode="backend-only",
        webcam_supported=False,
        preview_supported=False,
        message=(
            "Render deployment mode disables local camera access, OpenCV GUI "
            "preview, and live webcam tracking on the server."
        ),
    )


def main():
    port = int(os.environ.get("PORT", "5000"))
    print("=" * 55, flush=True)
    print(f"  Flask backend ready on port {port}", flush=True)
    print("  Render mode: webcam + GUI features disabled", flush=True)
    print("=" * 55, flush=True)
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()
