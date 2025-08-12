# Music Playlist Manager

A distributed microservice-based Python project that manages music playlists 
and serves recommendations using a dataset of Spotify songs.

## Project Structure

```
.
├── data/
│   └── spotify_data.csv              # Large dataset (tracked with Git LFS)
├── main_program/
│   ├── playlist_manager.py           # Core playlist management
│   └── test_playlist_manager.py      # Unit tests for playlist functionality
├── dataset_service/
│   └── song_service.py               # Handles loading and basic data operations
├── microservices/
│   ├── random_song_service/          # Returns random songs
│   ├── song_by_year_service/         # Returns songs from a given year
│   ├── total_duration_service/       # Computes duration of liked playlists
│   └── recommendation_service/       # Recommends songs by genre, artist, popularity
├── requirements.txt                  # Project dependencies
├── .gitignore                        # Ignore rules
├── .gitattributes                    # Git LFS config
└── README.md                         # This file
```

## How to Run

Each microservice is independently runnable using its server/client scripts:

```
python zeroMQServer.py  # Run inside the target microservice folder
python zeroMQClient.py  # Run client to send requests
```

## Dependencies

Install all dependencies with:

```
pip install -r requirements.txt
```

> Note: The large dataset file `spotify_data.csv` is tracked via Git LFS
> and not committed directly to the repository. Ensure you have Git LFS installed:

```
git lfs install
git lfs pull
```

## Microservices

| Microservice                | Port   | Description                              |
|----------------------------|--------|------------------------------------------|
| random_song_service        | 5556   | Returns a random song                    |
| song_by_year_service       | 5557   | Returns a song from a specific year      |
| total_duration_service     | 5558   | Computes total playlist duration         |
| recommendation_service     | 5555   | Recommends songs by artist, genre, etc.  |

## Notes

- `liked_songs/` stores user-specific song selections
- `users.json` stores user login data (ignored by Git)
- Only `data/spotify_data.csv` is tracked via LFS; other local dataset copies are ignored

## Author

- Stephan Demmers 








