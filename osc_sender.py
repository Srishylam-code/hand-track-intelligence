"""
osc_sender.py — OSC message sender for hand landmark data.

Transmits hand landmark coordinates to TouchDesigner (or any OSC receiver)
over UDP using the python-osc library.
"""

from pythonosc import udp_client


class OSCSender:
    """Sends hand landmark data as OSC messages over UDP."""

    def __init__(self, ip: str = "127.0.0.1", port: int = 9000):
        """
        Args:
            ip: Target IP address (default: localhost).
            port: Target UDP port (default: 9000).
        """
        self.ip = ip
        self.port = port
        self.client = udp_client.SimpleUDPClient(ip, port)
        print(f"[OSC] Sender initialized -> {ip}:{port}")

    def send_hand_count(self, count: int):
        """Send the number of detected hands."""
        self.client.send_message("/hand/count", count)

    def send_landmarks(self, hand_id: int, landmarks: list):
        """
        Send all 21 landmarks for a single hand.

        Args:
            hand_id: Hand index (0 or 1).
            landmarks: List of 21 landmark dicts with keys: id, name, x, y, z.
        """
        # Send detection status
        self.client.send_message(f"/hand/{hand_id}/detected", 1)

        for lm in landmarks:
            address = f"/hand/{hand_id}/landmark/{lm['id']}"
            self.client.send_message(address, [lm["x"], lm["y"], lm["z"]])

        # Also send key landmarks as named shortcuts for convenience
        self._send_named_shortcuts(hand_id, landmarks)

    def send_hand_not_detected(self, hand_id: int):
        """Notify that a hand is no longer detected."""
        self.client.send_message(f"/hand/{hand_id}/detected", 0)

    def _send_named_shortcuts(self, hand_id: int, landmarks: list):
        """
        Send convenient named OSC addresses for commonly used landmarks.

        This makes it easier to map in TouchDesigner without memorizing IDs.
        """
        key_landmarks = {
            "wrist": 0,
            "thumb_tip": 4,
            "index_tip": 8,
            "middle_tip": 12,
            "ring_tip": 16,
            "pinky_tip": 20,
        }

        for name, idx in key_landmarks.items():
            lm = landmarks[idx]
            self.client.send_message(
                f"/hand/{hand_id}/{name}",
                [lm["x"], lm["y"], lm["z"]],
            )

    def send_all(self, all_hands: list, max_hands: int = 2):
        """
        Send all hand data in a single call.

        Args:
            all_hands: List of hands from HandTracker.process().
            max_hands: Maximum expected hands (sends not-detected for missing).
        """
        self.send_hand_count(len(all_hands))

        for hand_id in range(max_hands):
            if hand_id < len(all_hands):
                self.send_landmarks(hand_id, all_hands[hand_id])
            else:
                self.send_hand_not_detected(hand_id)

    def close(self):
        """Clean up (no-op for UDP, but keeps interface consistent)."""
        print("[OSC] Sender closed.")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
