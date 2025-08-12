"""
ZeroMQ Server — Random Song Microservice (port 5556)
Returns one random song from spotify_data.csv
"""

import os
import sys
import pandas as pd
import zmq

PORT = 5556
DATA_FILE = os.path.join(os.path.dirname(__file__), "spotify_data.csv")


def _load_dataframe(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"CSV not found at: {path}")

    df = pd.read_csv(path)

    # Keep only columns we care about; be robust to different names
    def pick_col(possible):
        for c in possible:
            if c in df.columns:
                return c
        return None

    col_track = pick_col(["track_name", "title", "name"])
    col_artist = pick_col(["artist_name", "artist"])
    col_genre = pick_col(["genre"])
    col_year = pick_col(["year", "release_year"])
    col_duration = pick_col(["duration", "duration_ms"])
    col_popularity = pick_col(["popularity"])

    needed = [col_track, col_artist, col_genre]
    if any(c is None for c in needed):
        raise ValueError(
            "CSV missing required columns. Need at least track_name/title, "
            "artist_name/artist, and genre."
        )

    cols = [c for c in [col_track, col_artist, col_genre, col_year,
                        col_duration, col_popularity] if c]
    df = df[cols].dropna(subset=[col_track, col_artist, col_genre])

    # Rename to a consistent internal schema
    renames = {}
    renames[col_track] = "track_name"
    renames[col_artist] = "artist_name"
    renames[col_genre] = "genre"
    if col_year: renames[col_year] = "year"
    if col_duration: renames[col_duration] = "duration"
    if col_popularity: renames[col_popularity] = "popularity"

    return df.rename(columns=renames)


def _int_or_none(val):
    try:
        if pd.isna(val):
            return None
    except Exception:
        pass
    # pandas/numpy scalar -> python
    if hasattr(val, "item"):
        val = val.item()
    # Heuristic: duration may be in ms; keep as int
    try:
        return int(val)
    except Exception:
        return None


def _str_or_unknown(val):
    try:
        if pd.isna(val):
            return "Unknown"
    except Exception:
        pass
    if hasattr(val, "item"):
        val = val.item()
    return str(val) if val is not None else "Unknown"


def main():
    # Load data upfront; crash early if it’s missing
    try:
        df = _load_dataframe(DATA_FILE)
    except Exception as e:
        print(f"Failed to load dataset: {e}")
        sys.exit(1)

    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://*:{PORT}")
    print(f"Starting Random Song Microservice on port {PORT}...")

    try:
        while True:
            try:
                req = socket.recv_json()
                print(f"Received request: {req}")

                if req.get("type") != "random_song":
                    socket.send_json({"error": "Invalid request type"})
                    continue

                # Sample one random row
                row = df.sample(1).iloc[0]

                song = {
                    "title": _str_or_unknown(row.get("track_name")),
                    "artist": _str_or_unknown(row.get("artist_name")),
                    "genre": _str_or_unknown(row.get("genre")),
                    # optional fields
                    "year": _int_or_none(row.get("year")),
                    "duration": _int_or_none(row.get("duration")),
                    "popularity": _int_or_none(row.get("popularity")),
                }

                socket.send_json({"song": song})

            except Exception as e:
                # never crash the loop; always respond
                socket.send_json({"error": str(e)})

    except KeyboardInterrupt:
        print("\nShutting down random song server...")

    finally:
        socket.close(0)
        context.term()
        print("Server stopped.")


if __name__ == "__main__":
    main()

