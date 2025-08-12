import pandas as pd

# Load and clean Spotify one million songs dataset
df = pd.read_csv('../../data/spotify_data.csv')
df_cleaned = df.dropna()

# Extract features of interest for recommendations
df_features = df_cleaned[
    ['artist_name',
    'track_name',
    'genre',
    'popularity',
    'tempo',
    'danceability',
    'energy']].copy()


def get_more_songs_by_artist(artist_name, max_results=5):
    """
    Return up to `max_results` songs by the same artist.
    Only matches exact artist names (case-insensitive).
    """
    matches = df_features[df_features['artist_name'].str.lower() == artist_name.lower()]

    if matches.empty:
        print(f"No songs found for artist '{artist_name}'")
        return {"recommendations": []}

    recommendations = {"recommendations": []}

    for _, row in matches.head(max_results).iterrows():
        rec = {
            "title": row['track_name'],
            "artist": row['artist_name'],
            "genre": row['genre'],
            "popularity": int(row['popularity'])
        }
        recommendations["recommendations"].append(rec)

    return recommendations


def get_top_popular_songs(n=5):
    """
    Return the top N most popular songs.
    """
    top_songs = df_features.sort_values(by="popularity", ascending=False).head(n)

    recommendations = {"recommendations": []}
    for _, row in top_songs.iterrows():
        recommendations["recommendations"].append({
            "title": row['track_name'],
            "artist": row['artist_name'],
            "genre": row['genre'],
            "popularity": int(row['popularity'])
        })
    return recommendations