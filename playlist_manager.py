"""Music Playlist Manager (Sprint 1)"""

import sys
from datetime import datetime
from typing import Dict, List

# ------------------------------------------------------------------------------
# Initialize Lists And Dicts For Password/Playlist Storage
# ------------------------------------------------------------------------------
# Placeholder for username and password storage
users = {}
# List of dicts: {title, artist, genre, year, album, date_added, duration}
liked_songs: List[Dict[str, str]] = []
# Starter Genres
genres = ["Rock", "Pop", "Jazz", "Hip-Hop", "Classical"]


# ------------------------------------------------------------------------------
# Utility Helpers For Future Testing
# ------------------------------------------------------------------------------

def _safe_input(prompt: str) -> str:
    """Wrapper for input() for testing suite."""
    return input(prompt)


# ------------------------------------------------------------------------------
# Screens Currently Implemented For The Music Playlist CLI
# ------------------------------------------------------------------------------

def welcome_screen():
    """
    Welcome screen for user to either log in or register for
    an account.
    """
    print("=== Welcome to CLI Music Playlist Manager ===")
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
        print("[5] Logout")
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
            if confirm_logout_screen():
                return  # Go back to log in
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

        # Genre selection loop
        while True:
            print("\nAvailable genres:")
            for i, g in enumerate(genres, 1):
                print(f"{i}. {g}")
            print("[N] Add a new genre")
            genre_choice = _safe_input("Select genre number, or [N] for new "
                                       "genre, or [B] Back: ").strip()

            if genre_choice.upper() == "B":
                print("Cancelled add song.\n")
                return
            elif genre_choice.upper() == "N":
                # Add a new genre manually
                new_genre = _safe_input(
                    "Enter new genre name (or [B] Back): ").strip()
                if new_genre.upper() == "B":
                    continue  # Go back to genre selection
                if not new_genre:
                    print("Genre name cannot be empty.\n")
                    continue
                if new_genre in genres:
                    print(f"Genre '{new_genre}' already exists.\n")
                    continue
                genres.append(new_genre)
                genre = new_genre
                break
            elif genre_choice.isdigit():
                idx = int(genre_choice) - 1
                if 0 <= idx < len(genres):
                    genre = genres[idx]
                    break
                else:
                    print("Invalid genre selection.\n")
            else:
                print("Invalid input. Please enter a number, [N], or [B].\n")

        # Go to confirm add song screen if inputs are valid
        confirm_add_song_screen(title, artist, genre)
        return  # after confirmation (add or cancel) return to Home


def confirm_add_song_screen(title, artist, genre):
    """Confirmation screen before adding a song to 'liked'."""
    while True:
        print("\nYou entered:")
        print(f"Title:  {title}")
        print(f"Artist: {artist}")
        print(f"Genre:  {genre}")
        print("\nIf you confirm, this song will be added to your Liked Songs "
              f"and appear in the '{genre}' playlist. If the genre is wrong, "
              "choose [R] to reenter info.")
        choice = _safe_input("Add this song? ([Y] = Yes, [N] = No, "
                             "[R] = Reenter info): ").strip().upper()
        if choice == "Y":
            liked_songs.append({
                "title": title,
                "artist": artist,
                "genre": genre,
                "year": "Unknown",
                "album": "Unknown",
                "date_added": datetime.now().strftime("%Y-%m-%d"),
                "duration": "Unknown",
            })
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

