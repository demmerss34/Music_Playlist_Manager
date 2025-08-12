"""Music Playlist Manager"""

import sys
import os
import json
from datetime import datetime
from dataset_service.song_service import find_song_data
from microservices.recommendation_service.zeroMQClient import send_request
from microservices.random_song_service.zeroMQClient import request_random_song
from microservices.song_by_year_service.zeroMQClient import send_year_request
from microservices.total_duration_service.zeroMQClient import (
    send_duration_request
)


APP_DATA_FILE = "app_data.json"

# ----------------------------------------------------------------------
# Liked Songs Storage
# ----------------------------------------------------------------------
def load_liked_songs_for_user(username):
    filepath = os.path.join("liked_songs", f"{username}.json")
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return []


def save_liked_songs_for_user(username, songs):
    directory = "liked_songs"
    if not os.path.exists(directory):
        os.makedirs(directory)

    filepath = os.path.join("liked_songs", f"{username}.json")

    # Convert all data to built-in Python types
    def convert(item):
        if isinstance(item, dict):
            return {k: convert(v) for k, v in item.items()}
        elif isinstance(item, list):
            return [convert(i) for i in item]
        elif hasattr(item, "item"):  # handles numpy types
            return item.item()
        else:
            return item

    with open(filepath, "w") as f:
        json.dump(convert(songs), f, indent=2)


# ----------------------------------------------------------------------
# User Account and Genre Setup
# ----------------------------------------------------------------------
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(data):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=2)

users = load_users()

genres = []

def _safe_input(prompt: str) -> str:
    """Wrapper for input() for testing suite."""
    return input(prompt)


# ----------------------------------------------------------------------
# Recommendation Features/Screen For Sending To Microservice A
# ----------------------------------------------------------------------
def get_recommendations_by_artist(artist: str):
    """Request recommendations for songs by same artist."""
    payload = {
        "type": "recommend_by_artist",
        "artist": artist
    }
    response = send_request(payload)
    return response.get("recommendations", [])


def get_recommendations_by_genre(genre: str):
    """Request song recommendations in same genre."""
    payload = {
        "type": "recommend_by_genre",
        "genre": genre
    }
    response = send_request(payload)
    return response.get("recommendations", [])


def recommendation_screen(username, liked_songs):
    """
    Main screen to show all 3 recommendation types for sending to the
    microservice and allows user to add any of the received songs.
    """
    print("\n=== Song Recommendations ===")
    print("[1] Recommend More Songs by Artist")
    print("[2] Recommend Songs by Genre")
    print("[3] Recommend Popular Songs")
    print("[B] Back")

    choice = _safe_input("Select an option: ").strip().upper()
    if choice == "B":
        return

    if choice == "1":
        artist = _safe_input("Enter the artist name: ").strip()

        if not artist:
            print("Artist name cannot be empty.\n")
            return

        recs = get_recommendations_by_artist(artist)
    elif choice == "2":
        if not genres:
            print("No genres available yet. Add songs first.\n")
            return

        print("\nAvailable genres:")

        for g in genres:
            print(f"- {g}")

        genre_input = _safe_input("Enter a genre from the "
                                  "list above: ").strip()

        if genre_input not in genres:
            print("Genre not recognized or not in your playlist.\n")
            return

        recs = get_recommendations_by_genre(genre_input)
    elif choice == "3":
        recs = send_request({"type": "recommend_popular"}).get(
            "recommendations", [])
    else:
        print("Invalid input.\n")
        return

    if not recs:
        print("No recommendations found.\n")
        return

    print("\nRecommended Songs:")

    for i, song in enumerate(recs, 1):
        print(f"{i}. {song['title']} - {song['artist']} ({song['genre']})")

    add_choice = _safe_input(
        "Add one or more songs to liked? Enter number(s) separated by "
        "commas or [N] to skip: ").strip().upper()

    if add_choice == "N":
        return

    indices_to_add = []

    if add_choice:
        parts = [x.strip() for x in add_choice.split(",")]
        for part in parts:
            if part.isdigit():
                idx = int(part) - 1
                if 0 <= idx < len(recs):
                    indices_to_add.append(idx)
                else:
                    print(f"Ignoring invalid selection: {part}")
            else:
                print(f"Ignoring invalid input: {part}")

    if not indices_to_add:
        print("No valid song selections made.\n")
        return

    for idx in indices_to_add:
        song = recs[idx]

        # Prevent adding duplicates
        already_liked = any(
            s["title"].lower() == song["title"].lower() and
            s["artist"].lower() == song["artist"].lower()
            for s in liked_songs
        )

        if already_liked:
            print(
                f"'{song['title']}' by {song['artist']} is "
                f"already in your liked songs. Skipping.\n")
            continue

        song_data = find_song_data(song["title"], song["artist"])
        year = song_data["year"] if song_data and song_data.get(
            "year") else "Unknown"
        duration = song_data["duration"] if song_data and song_data.get(
            "duration") else "Unknown"
        liked_songs.append({
            "title": song["title"],
            "artist": song["artist"],
            "genre": song["genre"],
            "year": year,
            "date_added": datetime.now().strftime("%Y-%m-%d"),
            "duration": duration
        })

        if song["genre"] not in genres and song["genre"] != "Unknown":
            genres.append(song["genre"])

    save_liked_songs_for_user(username, liked_songs)
    print(f"{len(indices_to_add)} song(s) added to your playlist.\n")


# ----------------------------------------------------------------------
# Screens Implemented For The Music Playlist CLI
# ----------------------------------------------------------------------

def welcome_screen():
    """
    Welcome screen for user to either log in or register for
    an account.
    """
    print("=== Welcome to CLI Music Playlist Manager ===")
    print(
        "Organize your favorite music, create playlists by genre, and "
        "save your preferences securely.\n")

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
        save_users(users)

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
            return None  # Go back to welcome screen

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
    liked_songs = load_liked_songs_for_user(username)

    while True:
        print("=== Home Menu ===")
        print(f"Welcome, {username}!")
        print("[1] Add a Song")
        print("[2] View Playlist by Genre")
        print("[3] Lookup Song")
        print("[4] Delete a Song")
        print("[5] Get Song Recommendations")
        print("[6] Add a Random Song")
        print("[7] Add Song by Year")
        print("[8] Show Total Playlist Duration")
        print("[9] Logout")

        print("[Q] Quit Program\n")

        choice = _safe_input("Select an option: ").strip().upper()
        if choice == "1":
            add_song_screen(username, liked_songs)
        elif choice == "2":
            view_playlist_by_genre_screen(liked_songs)
        elif choice == "3":
            song_lookup_screen(liked_songs)
        elif choice == "4":
            delete_song_screen(username, liked_songs)
        elif choice == "5":
            recommendation_screen(username, liked_songs)
        elif choice == "6":
            add_random_song_screen(username, liked_songs)
        elif choice == "7":
            add_song_by_year_screen(username, liked_songs)
        elif choice == "8":
            total_duration_screen(username)
        elif choice == "9":
            if confirm_logout_screen():
                return
        elif choice == "Q":
            if confirm_quit_screen():
                sys.exit("Goodbye!")
        else:
            print("Invalid option.\n")


def add_song_screen(username, liked_songs):
    """Prompt user for song title and artist for song to be added."""
    while True:
        print("\n=== Add a Song ===")
        title = _safe_input("Enter a song title from 2000 to 2023 "
                            "(or [B] Back): ").strip()

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
        confirm_add_song_screen(title, artist, username, liked_songs)
        return


def confirm_add_song_screen(title, artist, username, liked_songs):
    """
    Confirmation screen before adding a song to genre playlist. Pulls
    data from our dataset to fill in genre, release year, and duration
    in milliseconds.
    """
    global genres
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

            # Add genre if not already in list
            if genre not in genres and genre != "Unknown":
                genres.append(genre)

            save_liked_songs_for_user(username, liked_songs)
            print(f"'{title}' added to your liked songs.\n")
            return
        elif choice == "N":
            print("Song addition cancelled.\n")
            return
        elif choice == "R":
            # Re-enter full add song sequence
            return
        else:
            print("Please enter [Y], [N], or [R].\n")


def add_random_song_screen(username, liked_songs):
    """
    Fetches a random song from the microservice and allows the
    user to confirm adding it.
    """
    print("\n=== Add a Random Song ===")

    song = request_random_song()
    if not song:
        print("Could not retrieve a random song.\n")
        return

    print("\nRandom Song Retrieved:")
    print(f"Title:  {song['title']}")
    print(f"Artist: {song['artist']}")
    print(f"Genre:  {song['genre']}")
    print(f"Year:   {song.get('year', 'Unknown')}")
    print(f"Duration: {song.get('duration', 'Unknown')}")

    confirm = _safe_input("\nAdd this song to your "
                          "playlist? (Y/N): ").strip().upper()

    if confirm != "Y":
        print("Cancelled.\n")
        return

    # Prevent duplicates
    already_liked = any(
        s["title"].lower() == song["title"].lower() and
        s["artist"].lower() == song["artist"].lower()
        for s in liked_songs
    )

    if already_liked:
        print("This song is already in your playlist. Skipping.\n")
        return

    liked_songs.append({
        "title": song["title"],
        "artist": song["artist"],
        "genre": song["genre"],
        "year": song.get("year", "Unknown"),
        "date_added": datetime.now().strftime("%Y-%m-%d"),
        "duration": song.get("duration", "Unknown")
    })

    if song["genre"] not in genres and song["genre"] != "Unknown":
        genres.append(song["genre"])

    save_liked_songs_for_user(username, liked_songs)
    print(f"'{song['title']}' added to your liked songs!\n")


def add_song_by_year_screen(username, liked_songs):
    """Fetch a single song from a given year between 2000 and 2023."""
    year_str = _safe_input("Enter a year (e.g., 2000–2023) "
                           "or [B] Back: ").strip().upper()

    if year_str == "B":
        return

    if not year_str.isdigit():
        print("Please enter a valid numeric year.\n")
        return

    year = int(year_str)

    if year < 2000 or year > 2023:
        print("Year out of range.\n")
        return

    try:
        response = send_year_request(year)
        songs = response.get("songs", [])
    except TimeoutError as e:
        print(f"Year song service timed out: {e}\n")
        return

    if not songs:
        print("No songs found for that year.\n")
        return

    song = songs[0]

    # Prevent duplicates
    if any(s["title"].lower() == song["title"].lower()
           and s["artist"].lower() == song["artist"].lower()
           for s in liked_songs):
        print(f"'{song['title']}' by {song['artist']} "
              f"is already in liked songs.\n")
        return

    # Fill year/duration via dataset lookup if missing
    song_data = find_song_data(song["title"], song["artist"])
    year_resolved = (song_data.get("year")
                     if song_data and song_data.get("year")
                     else song.get("year", "Unknown"))
    duration_resolved = (song_data.get("duration")
                         if song_data and song_data.get("duration")
                         else song.get("duration", "Unknown"))
    genre_resolved = (song.get("genre") if song.get("genre")
                      else (song_data.get("genre")
                            if song_data else "Unknown"))

    liked_songs.append({
        "title": song["title"],
        "artist": song["artist"],
        "genre": genre_resolved,
        "year": year_resolved,
        "date_added": datetime.now().strftime("%Y-%m-%d"),
        "duration": duration_resolved,
    })

    if genre_resolved not in genres and genre_resolved != "Unknown":
        genres.append(genre_resolved)

    save_liked_songs_for_user(username, liked_songs)
    print(f"Added song from {year}: {song['title']} - "
          f"{song['artist']} ({genre_resolved})\n")


def total_duration_screen(username):
    """
    Get the total duration of the user's playlist by requesting it
    from Microservice D.
    """
    try:
        response = send_duration_request(username)

        if "error" in response:
            print(f"Error: {response['error']}")
            return

        # Get the response data for the total duration and format it
        total_duration = response.get("readable", "Unknown")
        total_ms = response.get("total_seconds", 0) * 1000
        count_songs = response.get("count_songs", 0)
        skipped = response.get("skipped", 0)

        print("\n=== Total Playlist Duration ===")
        print(f"Total duration: {total_duration} ({total_ms:,} ms)")
        print(f"Total songs: {count_songs}")
        print(f"Songs skipped (invalid duration): {skipped}\n")

    except Exception as e:
        print(f"Failed to get total playlist duration: {str(e)}")


def view_playlist_by_genre_screen(liked_songs):
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
            display_genre_playlist_screen(genres[idx], liked_songs)
        else:
            print("Invalid selection.\n")


def display_genre_playlist_screen(genre, liked_songs):
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


def song_lookup_screen(liked_songs):
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


def delete_song_screen(username, liked_songs):
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
                confirm_delete_song_screen(idx, liked_songs, username)
                return
            else:
                print("Invalid selection.\n")
        else:
            print("Invalid input.\n")


def confirm_delete_song_screen(song_index: int, liked_songs: list,
                               username: str):
    """Confirm deletion of a song and warn about the cost."""
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
            save_liked_songs_for_user(username, liked_songs)
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


# ----------------------------------------------------------------------
# Main Entry Point
# ----------------------------------------------------------------------

def main():
    while True:
        username = welcome_screen()
        home_screen(username)


if __name__ == "__main__":
    main()

