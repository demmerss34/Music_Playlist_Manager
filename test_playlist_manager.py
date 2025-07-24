import sys
import os
sys.path.append(r"C:\Users\steph\CS361\CS361 Music Playlist Manager Main Program")
import unittest
from unittest.mock import patch
import playlist_manager as playlist
# Import your CLI app file, aliasing it to 'playlist' for convenience.


class TestPlaylistManager(unittest.TestCase):
    """
    Automated tests for the CLI Music Playlist Manager.
    We mock user input so tests run without manual typing.
    """

    # --------------------------------------------------------------------------
    # Registration Tests
    # --------------------------------------------------------------------------
    @patch('playlist_manager._safe_input', side_effect=[
        'user',      # username entered
        'password',  # password entered
    ])
    def test_register_screen(self, mock_input):
        """
        Test registering a new user with 'user' / 'password'.
        """
        playlist.users.clear()  # Ensure no users exist.
        playlist.register_screen()
        # Check that the user was added to the dictionary.
        self.assertIn('user', playlist.users)
        self.assertEqual(playlist.users['user'], 'password')

    # --------------------------------------------------------------------------
    # Login Tests
    # --------------------------------------------------------------------------
    @patch('playlist_manager._safe_input', side_effect=[
        'user',      # username entered
        'password',  # password entered
    ])
    def test_login_screen(self, mock_input):
        """
        Test logging in with a valid username and password.
        """
        # Add the user directly to simulate registration.
        playlist.users['user'] = 'password'
        result = playlist.login_screen()
        self.assertEqual(result, 'user')  # login_screen should return username.

    # --------------------------------------------------------------------------
    # Add Song Tests
    # --------------------------------------------------------------------------
    @patch('playlist_manager._safe_input', side_effect=[
        # Adding a new song:
        'My Song',    # Title
        'My Artist',  # Artist
        '1',          # Choose first genre ("Rock")
        'Y',          # Confirm adding
    ])
    def test_add_song_screen(self, mock_input):
        """
        Test adding a song to liked_songs.
        """
        playlist.liked_songs.clear()  # Start with no songs.
        playlist.add_song_screen()
        self.assertEqual(len(playlist.liked_songs), 1)
        song = playlist.liked_songs[0]
        self.assertEqual(song['title'], 'My Song')
        self.assertEqual(song['artist'], 'My Artist')
        self.assertEqual(song['genre'], 'Rock')

    # --------------------------------------------------------------------------
    # Song Lookup Tests
    # --------------------------------------------------------------------------
    @patch('playlist_manager._safe_input', side_effect=[
        'My Song',  # Search query
        'B',        # Back out after search
    ])
    def test_song_lookup_screen(self, mock_input):
        """
        Test searching for a song title.
        """
        playlist.liked_songs.clear()
        playlist.liked_songs.append({
            "title": "My Song",
            "artist": "My Artist",
            "genre": "Rock",
            "year": "Unknown",
            "album": "Unknown",
            "date_added": "2025-07-22",
            "duration": "Unknown"
        })
        # We just check that this doesn't throw errors with a valid search.
        playlist.song_lookup_screen()
        # No assert needed, but we know lookup didn't fail.

    # --------------------------------------------------------------------------
    # Delete Song Tests
    # --------------------------------------------------------------------------
    @patch('playlist_manager._safe_input', side_effect=[
        '1',  # Select first song to delete
        'Y',  # Confirm delete
    ])
    def test_delete_song_screen(self, mock_input):
        """
        Test deleting a song from liked_songs.
        """
        playlist.liked_songs.clear()
        playlist.liked_songs.append({
            "title": "Song To Delete",
            "artist": "Artist",
            "genre": "Pop",
            "year": "Unknown",
            "album": "Unknown",
            "date_added": "2025-07-22",
            "duration": "Unknown"
        })
        playlist.delete_song_screen()
        self.assertEqual(len(playlist.liked_songs), 0)


# --------------------------------------------------------------------------
# Test Runner
# --------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
