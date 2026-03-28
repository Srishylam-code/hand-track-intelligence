"""
main.py - Hand Tracking Dashboard (single Flask server, port 5000)

  - Opening http://localhost:5000 shows the main dashboard.
  - Live hand tracking frames are streamed into the browser UI.
"""

import argparse
import sys
import threading
import time
import webbrowser

import cv2
from flask import Flask, Response, jsonify, render_template, request

from hand_tracker import HandTracker
from hud_visualizer import HUDVisualizer
from osc_sender import OSCSender


app = Flask(__name__)

output_bytes = None
frame_lock = threading.Lock()
camera_cmd = None


@app.route("/")
def index():
    return render_template("index.html")


def generate_frames():
    global output_bytes
    while True:
        with frame_lock:
            encoded_image = output_bytes

        if encoded_image is None:
            time.sleep(0.01)
            continue

        yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + encoded_image + b"\r\n"


@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/set_camera", methods=["POST"])
def set_camera():
    global camera_cmd
    data = request.get_json(silent=True) or {}
    source = data.get("source", "0")
    camera_cmd = int(source) if str(source).isdigit() else source
    return jsonify({"status": "success", "source": str(camera_cmd)})


def start_flask():
    import logging

    log = logging.getLogger("werkzeug")
    log.setLevel(logging.ERROR)
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)


def parse_args():
    parser = argparse.ArgumentParser(description="Real-time hand tracking with OSC output")
    parser.add_argument("--ip", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9000)
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--max-hands", type=int, default=2, choices=[1, 2])
    parser.add_argument("--detection-confidence", type=float, default=0.7)
    parser.add_argument("--tracking-confidence", type=float, default=0.5)
    parser.add_argument("--no-preview", action="store_true")
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    return parser.parse_args()


def main():
    args = parse_args()

    tracker = HandTracker(
        max_num_hands=args.max_hands,
        min_detection_confidence=args.detection_confidence,
        min_tracking_confidence=args.tracking_confidence,
    )
    sender = OSCSender(ip=args.ip, port=args.port)
    hud = HUDVisualizer()

    print("[INFO] Camera will start on standby (waiting for UI)...", flush=True)
    cap = None
    is_camera_running = False
    current_camera_src = args.camera

    print("=" * 55)
    print("  HandTrack dashboard ready at http://127.0.0.1:5000/")
    print("=" * 55)
    print(f"  Camera   : {args.camera} ({args.width}x{args.height})")
    print(f"  OSC      : {args.ip}:{args.port}")
    print(f"  Preview  : {'ON' if not args.no_preview else 'OFF'}")
    print("=" * 55)
    print("  Press 'q' to quit")
    print("=" * 55)

    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()

    threading.Timer(1.5, lambda: webbrowser.open("http://127.0.0.1:5000/")).start()

    window_name = "Hand Tracking -> TouchDesigner"
    if not args.no_preview:
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, args.width, args.height)

    prev_time = time.time()
    frame_count = 0
    global camera_cmd, output_bytes
    output_bytes = None

    try:
        while True:
            if camera_cmd is not None:
                print(f"\n[INFO] Camera Command: {camera_cmd}", flush=True)
                if camera_cmd == "stop":
                    if cap is not None:
                        cap.release()
                    cap = None
                    is_camera_running = False
                    with frame_lock:
                        output_bytes = None
                elif camera_cmd == "start":
                    if cap is not None:
                        cap.release()
                    if sys.platform == "win32" and isinstance(current_camera_src, int):
                        cap = cv2.VideoCapture(current_camera_src, cv2.CAP_DSHOW)
                    else:
                        cap = cv2.VideoCapture(current_camera_src)
                    if cap and cap.isOpened():
                        cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
                        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
                        is_camera_running = True
                else:
                    current_camera_src = camera_cmd
                    if is_camera_running:
                        if cap is not None:
                            cap.release()
                        if sys.platform == "win32" and isinstance(current_camera_src, int):
                            cap = cv2.VideoCapture(current_camera_src, cv2.CAP_DSHOW)
                        else:
                            cap = cv2.VideoCapture(current_camera_src)
                        if cap and cap.isOpened():
                            cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
                            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
                camera_cmd = None

            if not is_camera_running or cap is None:
                time.sleep(0.1)
                continue

            ret, frame = cap.read()
            if not ret:
                time.sleep(0.01)
                continue

            frame = cv2.flip(frame, 1)
            hands = tracker.process(frame)
            sender.send_all(hands, max_hands=args.max_hands)

            current_time = time.time()
            elapsed = current_time - prev_time
            fps_val = frame_count / elapsed if elapsed > 0 else 0
            frame = hud.draw(frame, hands, fps=fps_val)
            frame_count += 1

            if elapsed >= 1.0:
                fps = frame_count / elapsed
                frame_count = 0
                prev_time = current_time
                hand_info = f"{len(hands)} hand(s)" if hands else "No hands"
                print(f"\r  FPS: {fps:.1f} | {hand_info}        ", end="", flush=True)

            success, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if success:
                with frame_lock:
                    output_bytes = buffer.tobytes()

            if not args.no_preview:
                cv2.imshow(window_name, frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("\n[INFO] Quit requested.")
                break

    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user.")
    finally:
        print("[INFO] Shutting down...")
        if cap is not None:
            cap.release()
        cv2.destroyAllWindows()
        tracker.close()
        sender.close()
        print("[INFO] Done.")


if __name__ == "__main__":
    main()
