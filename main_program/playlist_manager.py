"""Music Playlist Manager (Sprint 1)"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, List
from dataset_service.song_service import find_song_data
from recommendation_client import send_request

APP_DATA_FILE = "app_data.json"

# ------------------------------------------------------------------------------
# Persistent Storage In JSON
# ------------------------------------------------------------------------------
def load_liked_songs() -> List[Dict[str, str]]:
    """Load liked songs from file, or return empty list if file missing."""
    if os.path.exists(APP_DATA_FILE):
        with open(APP_DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_liked_songs(data):
    """Save liked songs to file for persistence."""
    with open(APP_DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# Load from disk initially
liked_songs: List[Dict[str, str]] = load_liked_songs()

# ------------------------------------------------------------------------------
# User Account and Genre Setup
# ------------------------------------------------------------------------------
users = {}
# Starter Genres
genres = ["Rock", "Pop", "Jazz", "Hip-Hop", "Classical"]

# ------------------------------------------------------------------------------
# Input Helper
# ------------------------------------------------------------------------------

def _safe_input(prompt: str) -> str:
    """Wrapper for input() for testing suite."""
    return input(prompt)


# ------------------------------------------------------------------------------
# Recommendation Features/Screen For Sending To Microservice A
# ------------------------------------------------------------------------------
def get_recommendations_by_artist(artist: str):
    """Request recommendations for songs by same artist (not already liked)."""
    titles_in_playlist = {song["title"] for song in liked_songs}
    payload = {
        "type": "recommend_by_artist",
        "auth_key": os.getenv("AUTH_KEY"),
        "artist": artist,
        "exclude_titles": list(titles_in_playlist)
    }
    response = send_request(payload)
    return response.get("result", [])

def get_recommendations_by_genre(genre: str):
    """Request recommendations in same genre (not already liked)."""
    titles_in_playlist = {song["title"] for song in liked_songs}
    payload = {
        "type": "recommend_by_genre",
        "auth_key": os.getenv("AUTH_KEY"),
        "genre": genre,
        "exclude_titles": list(titles_in_playlist)
    }
    response = send_request(payload)
    return response.get("result", [])

def get_popular_recommendations():
    """Request 3 overall popular songs (not already liked)."""
    titles_in_playlist = {song["title"] for song in liked_songs}
    payload = {
        "type": "recommend_popular",
        "auth_key": os.getenv("AUTH_KEY"),
        "exclude_titles": list(titles_in_playlist)
    }
    response = send_request(payload)
    return response.get("result", [])

def recommendation_screen():
    """
    Main screen to show all 3 recommendation types for sending to the
    microservice and allows user to add any of the received songs.
    """
    print("\n=== Song Recommendations ===")
    print("[1] Recommend More Songs by Same Artist")
    print("[2] Recommend Songs in Same Genre")
    print("[3] Recommend Popular Songs")
    print("[B] Back")

    choice = _safe_input("Select an option: ").strip().upper()
    if choice == "B":
        return
    elif choice in {"1", "2"}:
        song_title = _safe_input("Pick a song from your playlist to "
                                 "base it on: ").strip()
        match = next(
            (
                s for s in liked_songs
                if s["title"].lower() == song_title.lower()
            ),
            None
        )
        if not match:
            print("Song not found in your playlist.\n")
            return
        if choice == "1":
            recs = get_recommendations_by_artist(match["artist"])
        else:
            recs = get_recommendations_by_genre(match["genre"])
    elif choice == "3":
        recs = get_popular_recommendations()
    else:
        print("Invalid input.\n")
        return

    if not recs:
        print("No recommendations found.")
        return

    print("\nRecommended Songs:")
    for i, song in enumerate(recs, 1):
        print(f"{i}. {song['title']} - {song['artist']} ({song['genre']})")

    add_choice = _safe_input("Add one to liked? Enter number "
                             "or [N] to skip: ").strip().upper()
    if add_choice == "N":
        return
    if add_choice.isdigit():
        idx = int(add_choice) - 1
        if 0 <= idx < len(recs):
            liked_songs.append({
                "title": recs[idx]["title"],
                "artist": recs[idx]["artist"],
                "genre": recs[idx]["genre"],
                "year": recs[idx].get("year", "Unknown"),
                "date_added": datetime.now().strftime("%Y-%m-%d"),
                "duration": recs[idx].get("duration", "Unknown"),
            })
            save_liked_songs(liked_songs)
            print("Song added to your playlist.\n")
        else:
            print("Invalid selection.\n")
    else:
        print("Invalid input.\n")


# ------------------------------------------------------------------------------
# Screens Implemented For The Music Playlist CLI
# ------------------------------------------------------------------------------

def welcome_screen():
    """
    Welcome screen for user to either log in or register for
    an account.
    """
    print("=== Welcome to CLI Music Playlist Manager ===")
    print(
        "Organize your favorite music, create playlists by genre, and save your"
        " preferences securely.\n")
    while True:
        if users:
            print("[1] Login")
        else:
            print("[1] Login (No accounts yet - Please register first)")
        print("[2] Register")
        print("[Q] Quit")

        choice = _safe_input("Select an option: ").strip().upper()

        if choice == "1":
            if users:
                return login_screen()
            else:
                print("No accounts found. Please register first.\n")
        elif choice == "2":
            register_screen()
        elif choice == "Q":
            sys.exit("Goodbye!")
        else:
            print("Invalid input. Please enter [1], [2], or [Q].\n")


def register_screen():
    """Account registration for new user to sign up with."""
    print("\n=== Register a New Account ===")
    while True:
        username = _safe_input("Enter a username (or [B] Back): ").strip()
        if username.upper() == "B":
            return
        if not username:
            print("Username cannot be empty.\n")
            continue
        if username in users:
            print("Username already exists. Try another.\n")
            continue

        password = _safe_input("Enter a password (min 6 chars): ").strip()
        if len(password) < 6:
            print("Password too short.\n")
            continue

        users[username] = password
        print(f"Account '{username}' registered successfully! "
              f"You can now log in.\n")
        return


def login_screen():
    """Handles user login (loops until success)."""
    while True:
        print("\n=== Login ===")
        print("Enter your credentials, or:")
        print("[B] Back to Welcome")
        print("[R] Go to Register")

        username = _safe_input("Username: ").strip()
        if username.upper() == "B":
            return None  # Go back to welcome
        if username.upper() == "R":
            register_screen()
            continue  # After registration, return to log in screen

        password = _safe_input("Password: ").strip()
        if password.upper() == "B":
            return None
        if password.upper() == "R":
            register_screen()
            continue

        if username in users and users[username] == password:
            print("\nLogin successful!\n")
            return username
        else:
            print("Invalid credentials. Try again or press [B] to go back.\n")


def home_screen(username):
    """
    Home menu after login. User can choose from a list of navigation
    options or quit the program.
    """
    while True:
        print("=== Home Menu ===")
        print(f"Welcome, {username}!")
        print("[1] Add a Song")
        print("[2] View Playlist by Genre")
        print("[3] Lookup Song")
        print("[4] Delete a Song")
        print("[5] Get Song Recommendations")
        print("[6] Logout")
        print("[Q] Quit Program\n")

        choice = _safe_input("Select an option: ").strip().upper()
        if choice == "1":
            add_song_screen()
        elif choice == "2":
            view_playlist_by_genre_screen()
        elif choice == "3":
            song_lookup_screen()
        elif choice == "4":
            delete_song_screen()
        elif choice == "5":
            recommendation_screen()
        elif choice == "6":
            if confirm_logout_screen():
                return
        elif choice == "Q":
            if confirm_quit_screen():
                sys.exit("Goodbye!")
        else:
            print("Invalid option.\n")


def add_song_screen():
    """Prompt user for song title, artist, and genre for song to be added."""
    while True:
        print("\n=== Add a Song ===")
        title = _safe_input("Enter song title (or [B] Back): ").strip()
        if title.upper() == "B":
            print("Cancelled add song.\n")
            return
        if not title:
            print("Title cannot be empty.\n")
            continue

        artist = _safe_input("Enter artist name (or [B] Back): ").strip()
        if artist.upper() == "B":
            print("Cancelled add song.\n")
            return
        if not artist:
            print("Artist cannot be empty.\n")
            continue

        # Go to confirm add song screen if inputs are valid
        confirm_add_song_screen(title, artist)
        return  # after confirmation (add or cancel) return to Home


def confirm_add_song_screen(title, artist):
    """
    Confirmation screen before adding a song to genre playlist. Pulls data from
    our dataset to fill in genre, release year, and duration in milliseconds.
    """
    song_data = find_song_data(title, artist)

    year = song_data["year"] if song_data and song_data.get(
        "year") else "Unknown"
    duration = song_data["duration"] if song_data and song_data.get(
        "duration") else "Unknown"
    genre = song_data["genre"] if song_data and song_data.get(
        "genre") else "Unknown"

    while True:
        print("\nYou entered:")
        print(f"Title:  {title}")
        print(f"Artist: {artist}")
        print(f"Genre:  {genre}")
        print(f"Year:     {year}")
        print(f"Duration: {duration}")

        print("\nIf you confirm, this song will be added to your Liked Songs "
              f"and appear in the '{genre}' playlist. If any info is wrong, "
              "choose [R] to reenter info.")
        choice = _safe_input("Add this song? ([Y] = Yes, [N] = No, "
                             "[R] = Reenter info): ").strip().upper()
        if choice == "Y":
            liked_songs.append({
                "title": title,
                "artist": artist,
                "genre": genre,
                "year": year,
                "date_added": datetime.now().strftime("%Y-%m-%d"),
                "duration": duration,
            })
            save_liked_songs(liked_songs)
            print(f"'{title}' added to your liked songs.\n")
            return
        elif choice == "N":
            print("Song addition cancelled.\n")
            return
        elif choice == "R":
            # Re-enter full add song sequence
            add_song_screen()
            return
        else:
            print("Please enter [Y], [N], or [R].\n")


def view_playlist_by_genre_screen():
    """List genres for user to select from to view its playlist."""
    while True:
        print("\n=== View Playlist by Genre ===")
        print("Tip: Enter the number of the genre to see its songs, "
              "or [B] to return to Home.\n")
        for i, g in enumerate(genres, 1):
            print(f"{i}. {g}")
        genre_choice = _safe_input("Select genre number "
                                   "(or [B] Back): ").strip().upper()
        if genre_choice == "B":
            return
        if not genre_choice.isdigit():
            print("Invalid selection.\n")
            continue
        idx = int(genre_choice) - 1
        if 0 <= idx < len(genres):
            display_genre_playlist_screen(genres[idx])
        else:
            print("Invalid selection.\n")


def display_genre_playlist_screen(genre):
    """Display songs for a specific genre."""
    while True:
        print(f"\n=== {genre} Playlist ===")
        songs = [s for s in liked_songs if s["genre"] == genre]

        if not songs:
            print(f"No songs in {genre} playlist.")
            cmd = _safe_input("Press [B] Back: ").strip().upper()
            if cmd == "B":
                return
            else:
                print("Invalid input.\n")
                continue

        for i, song in enumerate(songs, 1):
            print(f"{i}. {song['title']} - {song['artist']} [I] for info")

        choice = _safe_input("Select song number + I (e.g., '1 I'), "
                             "or [B] Back: ").strip().upper()
        if choice == "B":
            return
        if choice:
            parts = choice.split()
            if len(parts) == 2 and parts[1] == "I" and parts[0].isdigit():
                idx = int(parts[0]) - 1
                if 0 <= idx < len(songs):
                    song_info_screen(songs[idx])
                else:
                    print("Invalid song number.\n")
            else:
                print("Invalid input.\n")


def song_lookup_screen():
    """Allow user to search for songs info by title."""
    while True:
        print("\n=== Song Lookup ===")
        query = _safe_input("Enter song title to search "
                            "(or [B] Back): ").strip()
        if query.upper() == "B":
            return
        if not query:
            print("Please enter a song title or [B] to go back.\n")
            continue
        q_lower = query.lower()
        matches = [
            song
            for song in liked_songs
            if q_lower in song["title"].lower()
        ]

        if not matches:
            print(f"No songs found matching '{query}'.")
            again = _safe_input("Try another search? "
                                "([Y] = Yes, [N] = No): ").strip().upper()
            if again == "N":
                return
            elif again == "Y":
                continue
            else:
                print("Input not recognized; returning to song lookup.\n")
                continue

        if len(matches) == 1:
            song_info_screen(matches[0])
            continue

        print(f"\nFound {len(matches)} songs matching '{query}':")
        for i, song in enumerate(matches, 1):
            print(f"{i}. {song['title']} - {song['artist']}")

        while True:
            choice = _safe_input("Select song number for details, "
                                 "or [B] Back: ").strip().upper()
            if choice == "B":
                break  # Go back to song lookup
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(matches):
                    song_info_screen(matches[idx])
                    break
                else:
                    print("Invalid selection.\n")
            else:
                print("Invalid input.\n")


def delete_song_screen():
    """List all liked songs and let the user choose one to delete."""
    while True:
        print("\n=== Delete a Song ===")
        if not liked_songs:
            print("You have no liked songs to delete.")
            cmd = _safe_input("Press [B] Back: ").strip().upper()
            if cmd == "B":
                return
            else:
                print("Invalid input.\n")
                continue

        for i, song in enumerate(liked_songs, 1):
            print(f"{i}. {song['title']} - {song['artist']} ({song['genre']})")

        choice = _safe_input("Select song number to delete, "
                             "or [B] Back: ").strip().upper()
        if choice == "B":
            return
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(liked_songs):
                confirm_delete_song_screen(idx)
                return
            else:
                print("Invalid selection.\n")
        else:
            print("Invalid input.\n")


def confirm_delete_song_screen(song_index: int):
    """Confirm deletion of a song and warn about the cost of doing so."""
    if not (0 <= song_index < len(liked_songs)):
        print("Error: Invalid song selection.\n")
        return

    song = liked_songs[song_index]
    title = song.get("title", "Unknown")
    artist = song.get("artist", "Unknown")
    genre = song.get("genre", "Unknown")

    print("\nYou selected to delete:")
    print(f"Title:  {title}")
    print(f"Artist: {artist}")
    print(f"Genre:  {genre}")
    print(
        "\nWARNING: Deleting this song will permanently remove it from your "
        "Liked Songs and from all playlist in this session.")
    print("If you delete it by mistake, you'll need to re-add it manually.\n")

    while True:
        choice = _safe_input(
            "Delete this song? ([Y] = Yes, [N] = No): ").strip().upper()
        if choice == "Y":
            removed = liked_songs.pop(song_index)
            save_liked_songs(liked_songs)
            print(
                f"'{removed['title']}' was deleted from your music "
                f"collection.\n")
            return
        elif choice == "N":
            print("Song deletion cancelled.\n")
            return
        else:
            print("Please enter [Y] or [N].\n")


def song_info_screen(song):
    """Display the song details."""
    while True:
        print("\n=== Song Info ===")
        print(f"Title: {song['title']}")
        print(f"Artist: {song['artist']}")
        print(f"Genre: {song['genre']}")
        print(f"Year: {song['year']}")
        print(f"Album: {song['album']}")
        print(f"Date Added: {song['date_added']}")
        print(f"Duration: {song['duration']}")
        cmd = _safe_input("Press [B] Back: ").strip().upper()
        if cmd == "B":
            return
        else:
            print("Invalid input.\n")


def confirm_logout_screen():
    """Confirm logout action."""
    while True:
        print("\nLogging out will return you to the Login screen.")
        choice = _safe_input("Are you sure you want to logout? "
                             "[Y] = Yes, [N] = No ").strip().upper()
        if choice == "Y":
            print("Logging out...\n")
            return True
        elif choice == "N":
            print("Logout cancelled.\n")
            return False
        else:
            print("Please enter [Y] or [N].\n")


def confirm_quit_screen():
    """Confirm quitting the entire program."""
    while True:
        print("\nQuitting will exit the program. "
              "All in-memory data will be lost.")
        choice = _safe_input("Are you sure you want to quit and log out? "
                             "[Y] = Yes, [N] = No ").strip().upper()
        if choice == "Y":
            return True
        elif choice == "N":
            return False
        else:
            print("Please enter Y or N.\n")


# ------------------------------------------------------------------------------
# Main Entry Point
# ------------------------------------------------------------------------------

def main():
    while True:
        username = welcome_screen()
        home_screen(username)


if __name__ == "__main__":
    main()

