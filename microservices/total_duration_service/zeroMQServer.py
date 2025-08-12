"""
ZeroMQ Server — Total Playlist Duration (Microservice D)
Listens on tcp://*:5558 and returns the total duration for a user's liked songs.
"""

import json
import re
from pathlib import Path
import zmq

PORT = 5558


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]

def liked_songs_path(username: str) -> Path:
    # OLD: return project_root() / "liked_songs" / f"{username}.json"
    return project_root() / "main_program" / "liked_songs" / f"{username}.json"


_duration_re_ms = re.compile(r"^\s*(\d+)\s*ms\s*$", re.IGNORECASE)
_duration_re_colon = re.compile(r"^\s*(\d{1,2}):(\d{2})(?::(\d{2}))?\s*$")


def parse_duration_to_seconds(value) -> int | None:
    """
    Parse common duration formats into total seconds.
    Returns None if the value is missing or cannot be parsed.

    Supported:
      - "242667 ms"  -> 242.667s
      - "3:30"       -> 210s
      - "01:02:03"   -> 3723s
      - 242667       -> assume milliseconds (>= 1000) else seconds
      - "210"        -> assume seconds
    """
    if value is None:
        return None

    # If it's already numeric
    if isinstance(value, (int, float)):
        # Heuristic: large numbers are probably milliseconds
        if value >= 1000:
            return int(round(value / 1000))
        return int(value)

    if not isinstance(value, str):
        return None

    s = value.strip()
    if not s or s.lower() == "unknown":
        return None

    # "123456 ms"
    m = _duration_re_ms.match(s)
    if m:
        ms = int(m.group(1))
        return ms // 1000

    # "mm:ss" or "hh:mm:ss"
    m = _duration_re_colon.match(s)
    if m:
        hh = m.group(3)
        if hh is not None:
            parts = s.split(":")
            parts = [int(p) for p in parts]
            if len(parts) == 3:
                h, m_, sec = parts
                return h * 3600 + m_ * 60 + sec
        mm = int(m.group(1))
        ss = int(m.group(2))
        return mm * 60 + ss

    # Plain integer string — assume seconds
    if s.isdigit():
        val = int(s)
        return val

    return None


def humanize_seconds(total: int) -> str:
    if total <= 0:
        return "0 sec"
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    parts = []
    if h:
        parts.append(f"{h} hr" + ("s" if h != 1 else ""))
    if m:
        parts.append(f"{m} min" + ("s" if m != 1 else ""))
    if s or not parts:
        parts.append(f"{s} sec" + ("s" if s != 1 else ""))
    return " ".join(parts)


def compute_total_duration(username: str) -> dict:
    """
    Load liked songs for the user and compute total duration.
    Returns a dict ready to send via JSON.
    """
    path = liked_songs_path(username)
    if not path.exists():
        return {
            "total_seconds": 0,
            "readable": "0 sec",
            "count_songs": 0,
            "skipped": 0,
            "note": f"No liked songs file for user '{username}'."
        }

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"error": f"Failed to read liked songs: {e}"}

    if not isinstance(data, list):
        return {"error": "Malformed liked songs file (expected a list)."}

    total_seconds = 0
    skipped = 0
    counted = 0

    for song in data:
        if not isinstance(song, dict):
            skipped += 1
            continue
        dur = song.get("duration")
        secs = parse_duration_to_seconds(dur)
        if secs is None:
            skipped += 1
            continue
        total_seconds += secs
        counted += 1

    return {
        "total_seconds": total_seconds,
        "readable": humanize_seconds(total_seconds),
        "count_songs": counted,
        "skipped": skipped,
    }


def main():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://*:{PORT}")
    print(f"Total Duration Server listening on port {PORT}... (Ctrl+C to stop)")

    try:
        while True:
            try:
                req = socket.recv_json()
                print(f"Received request: {req}")  # Debugging line

                if req.get("type") != "get_total_duration":
                    socket.send_json({"error": "Invalid request type"})
                    continue

                username = req.get("username", "").strip()
                if not username:
                    socket.send_json({"error": "Missing 'username'"})
                    continue

                result = compute_total_duration(username)
                socket.send_json(result)

            except Exception as e:
                # Never crash the loop on bad input — report error
                socket.send_json({"error": str(e)})

    except KeyboardInterrupt:
        print("\nShutting down server...")

    finally:
        socket.close(0)
        context.term()
        print("Server stopped.")


if __name__ == "__main__":
    main()

