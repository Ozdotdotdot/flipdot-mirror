import time

from flask import Flask, jsonify, render_template, request

from . import media, shaders
from .device import HEIGHT, WIDTH, device
from .playback import MAX_FPS, MIN_FPS, playback

app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html", width=WIDTH, height=HEIGHT)


@app.get("/api/state")
def state():
    return jsonify(
        {
            "width": WIDTH,
            "height": HEIGHT,
            "grid": device.grid,
            "connected": device.connected,
            "port": device.port,
            "last_status": device.last_status,
            "playback": playback.status(),
            "time": time.time(),
        }
    )


@app.get("/api/ports")
def ports():
    return jsonify(device.list_ports())


@app.post("/api/connect")
def connect():
    body = request.get_json(force=True)
    try:
        device.connect(body["port"], int(body.get("baud", 115200)))
        return jsonify({"ok": True})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.post("/api/disconnect")
def disconnect():
    device.disconnect()
    return jsonify({"ok": True})


@app.get("/api/shaders")
def list_shaders():
    return jsonify([{"key": k, "name": v[0]} for k, v in shaders.SHADERS.items()])


@app.post("/api/shader")
def run_shader():
    body = request.get_json(force=True)
    try:
        playback.play_shader(body["key"], body.get("fps"))
        return jsonify({"ok": True})
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.post("/api/stop")
def stop():
    playback.stop()
    return jsonify({"ok": True})


@app.post("/api/fps")
def set_fps():
    body = request.get_json(force=True)
    playback.fps = max(MIN_FPS, min(MAX_FPS, float(body["fps"])))
    return jsonify({"ok": True, "fps": playback.fps})


@app.post("/api/upload")
def upload():
    file = request.files.get("file")
    if file is None:
        return jsonify({"ok": False, "error": "no file"}), 400
    data = file.read()
    try:
        frames, fps = media.convert_upload(data, file.filename or "upload")
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    if not frames:
        return jsonify({"ok": False, "error": "no frames decoded"}), 400
    playback.play_media(frames, file.filename or "upload", fps)
    return jsonify({"ok": True, "frames": len(frames), "fps": playback.fps})


@app.post("/api/frame")
def manual_frame():
    body = request.get_json(force=True)
    grid = body["grid"]
    if len(grid) != HEIGHT or any(len(row) != WIDTH for row in grid):
        return jsonify({"ok": False, "error": "grid size mismatch"}), 400
    playback.stop()
    device.send_grid(grid)
    return jsonify({"ok": True})


@app.post("/api/toggle")
def toggle_dot():
    body = request.get_json(force=True)
    x, y = int(body["x"]), int(body["y"])
    if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
        return jsonify({"ok": False, "error": "out of range"}), 400
    playback.stop()
    grid = [row[:] for row in device.grid]
    grid[y][x] = not grid[y][x]
    device.send_grid(grid)
    return jsonify({"ok": True, "grid": grid})


@app.post("/api/fill")
def fill():
    body = request.get_json(force=True)
    value = bool(body.get("value", False))
    playback.stop()
    grid = [[value] * WIDTH for _ in range(HEIGHT)]
    device.send_grid(grid)
    return jsonify({"ok": True})


def main():
    app.run(host="0.0.0.0", port=8091, threaded=True)


if __name__ == "__main__":
    main()
