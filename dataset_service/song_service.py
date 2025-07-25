import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "spotify_data.csv")

df = pd.read_csv(DATA_PATH)


def find_song_data(title: str, artist: str) -> dict:
    """
    Search for a song by title and artist (case-insensitive).
    Returns a dict with song info or None if not found.
    """
    filtered = df[
        (df["track_name"].str.lower() == title.lower()) &
        (df["artist_name"].str.lower() == artist.lower())
        ]

    if filtered.empty:
        return None

    row = filtered.iloc[0]
    return {
        "title": row["track_name"],
        "artist": row["artist_name"],
        "genre": row.get("genre", "Unknown"),
        "year": row.get("year", "Unknown"),
        "duration": f"{row.get('duration_ms', 'Unknown')} ms"
    }

