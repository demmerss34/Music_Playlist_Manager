"""
ZeroMQ Server — Song By Year (Microservice C)
Listens on tcp://*:5557 and returns ONE random song for a requested year.
"""

import zmq
import pandas as pd

PORT = 5557
CSV_PATH = "spotify_data.csv"

# ---- Helpers to ensure JSON-safe types ----
def _to_py(val):
    # Handle pandas/np NA
    try:
        if pd.isna(val):
            return None
    except Exception:
        pass
    # Convert numpy scalars to Python
    if hasattr(val, "item"):
        return val.item()
    # Plain python types pass through
    return val

def _str_or_unknown(val):
    v = _to_py(val)
    if v is None:
        return "Unknown"
    return str(v)

def _int_or_none(val):
    v = _to_py(val)
    if v is None:
        return None
    try:
        return int(v)
    except Exception:
        return None

# ---- Load data once ----
df = pd.read_csv(CSV_PATH)
df = df.dropna(subset=["artist_name", "track_name", "genre", "year"])
# Optional: ensure year numeric
df["year"] = pd.to_numeric(df["year"], errors="coerce")

def pick_one_song_by_year(year: int) -> dict | None:
    subset = df[df["year"] == year]
    if subset.empty:
        return None
    row = subset.sample(1).iloc[0]
    # Build a JSON-safe dict
    return {
        "title": _str_or_unknown(row.get("track_name")),
        "artist": _str_or_unknown(row.get("artist_name")),
        "genre": _str_or_unknown(row.get("genre")),
        "year": _int_or_none(row.get("year")),
        "duration": _int_or_none(row.get("duration")),
        "popularity": _int_or_none(row.get("popularity")),
    }

def main():
    context = zmq.Context()
    sock = context.socket(zmq.REP)
    sock.bind(f"tcp://*:{PORT}")
    print(f"Song-by-Year Server listening on port {PORT}... (Ctrl+C to stop)")

    try:
        while True:
            try:
                req = sock.recv_json()
                if req.get("type") != "get_song_by_year":
                    sock.send_json({"error": "Invalid request type"})
                    continue

                year = req.get("year")
                # Be tolerant: if client sent numpy/int-like, coerce
                try:
                    year = int(year)
                except Exception:
                    sock.send_json({"error": "Invalid 'year' value"})
                    continue

                song = pick_one_song_by_year(year)
                if song is None:
                    sock.send_json({"songs": []})
                else:
                    # Wrap in list for compatibility with your handler
                    sock.send_json({"songs": [song]})

            except Exception as e:
                # If anything slips through, return an error rather than crash
                sock.send_json({"error": str(e)})

    except KeyboardInterrupt:
        print("\nServer stopping...")
    finally:
        sock.close(0)
        context.term()
        print("Server stopped.")

if __name__ == "__main__":
    main()

