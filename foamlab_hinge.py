#!/usr/bin/env python3
"""Foam Lab hinge bridge.

Reads the MacBook lid (hinge) angle sensor and serves The Foam Lab page on
http://localhost:8765 so the glass tilts when you move the screen.

Setup (once):   pip3 install hidapi
Run:            python3 foamlab_hinge.py
Test without a sensor:  python3 foamlab_hinge.py --fake
"""
import json
import math
import os
import sys
import threading
import time
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

PORT = 8765
HERE = os.path.dirname(os.path.abspath(__file__))
FAKE = "--fake" in sys.argv

state = {"angle": None, "error": None}


def read_sensor():
    """Poll the Apple lid angle HID sensor (vendor 0x05AC, product 0x8104)."""
    try:
        import hid  # from the "hidapi" package
    except ImportError:
        state["error"] = "Python package 'hidapi' is missing. Run: pip3 install hidapi"
        print(state["error"])
        return
    match = [
        d for d in hid.enumerate(0x05AC, 0x8104)
        if d.get("usage_page") == 0x0020 and d.get("usage") == 0x008A
    ]
    if not match:
        state["error"] = "No lid angle sensor found on this Mac."
        print(state["error"])
        return
    dev = hid.device()
    dev.open_path(match[0]["path"])
    print("Lid angle sensor found. Move the screen to tilt the glass.")
    while True:
        try:
            report = dev.get_feature_report(1, 8)
            if report and len(report) >= 3:
                state["angle"] = report[1] | (report[2] << 8)
        except Exception as exc:  # sensor hiccup: keep going
            state["error"] = f"Sensor read failed: {exc}"
        time.sleep(1 / 30)


def fake_sensor():
    print("Fake mode: the lid angle swings between 70 and 115 degrees.")
    t0 = time.time()
    while True:
        state["angle"] = round(92 + 22 * math.sin((time.time() - t0) * 0.8))
        time.sleep(1 / 30)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=HERE, **kw)

    def log_message(self, *a):
        pass

    def do_GET(self):
        if self.path.startswith("/angle"):
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            try:
                while True:
                    msg = json.dumps({"angle": state["angle"], "error": state["error"]})
                    self.wfile.write(f"data: {msg}\n\n".encode())
                    self.wfile.flush()
                    time.sleep(1 / 30)
            except (BrokenPipeError, ConnectionResetError):
                return
        if self.path in ("/", ""):
            self.path = "/index.html"
        return super().do_GET()


def main():
    threading.Thread(target=fake_sensor if FAKE else read_sensor, daemon=True).start()
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    url = f"http://localhost:{PORT}/"
    print(f"The Foam Lab is pouring at {url}  (Ctrl+C to stop)")
    if "--no-open" not in sys.argv:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nTaps closed.")


if __name__ == "__main__":
    main()
