import sys
import os
import pytest
from unittest.mock import patch, mock_open

# --- Microservice client imports ---
from microservices.recommendation_service.zeroMQClient import send_request
from microservices.random_song_service.zeroMQClient import request_random_song

# Add root to path so playlist_manager can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import playlist_manager

# ---------------- File operations ----------------

@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open,
       read_data='[{"title":"Song1","artist":"Artist1","genre":"Pop"}]')
def test_load_liked_songs(mock_file, mock_exists):
    songs = playlist_manager.load_liked_songs_for_user("user1")
    assert isinstance(songs, list)
    assert songs[0]["title"] == "Song1"


@patch("builtins.open", new_callable=mock_open)
def test_save_liked_songs(mock_file):
    test_data = [{"title": "SongX", "artist": "ArtistX", "genre": "Rock"}]
    playlist_manager.save_liked_songs_for_user("user1", test_data)
    mock_file().write.assert_called()

# ---------------- Song add/delete/lookup ----------------

@patch("playlist_manager._safe_input")
@patch("playlist_manager.find_song_data")
@patch("playlist_manager.save_liked_songs_for_user")
@patch("playlist_manager.load_liked_songs_for_user")
def test_add_song_and_confirm(mock_load, mock_save, mock_find_song, mock_input):
    username = "user1"
    mock_input.side_effect = ["Test Song", "Test Artist", "Y"]
    mock_find_song.return_value = {
        "genre": "Jazz", "year": "2020", "duration": "200000 ms"
    }
    mock_load.return_value = []

    liked_songs = []
    playlist_manager.add_song_screen(username, liked_songs)

    mock_save.assert_called_once()
    saved_songs = mock_save.call_args[0][1]
    assert saved_songs[0]["title"] == "Test Song"


@patch("playlist_manager._safe_input")
@patch("playlist_manager.save_liked_songs_for_user")
@patch("playlist_manager.load_liked_songs_for_user")
def test_delete_song_screen_confirm(mock_load, mock_save, mock_input):
    username = "user1"
    mock_input.side_effect = ["1", "Y"]
    mock_load.return_value = [{"title": "ToDelete", "artist":
        "Artist", "genre": "Rock"}]

    liked_songs = [{"title": "ToDelete", "artist": "Artist", "genre": "Rock"}]
    playlist_manager.delete_song_screen(username, liked_songs)

    mock_save.assert_called_once()
    saved_songs = mock_save.call_args[0][1]
    assert len(saved_songs) == 0


@patch("playlist_manager._safe_input")
@patch("playlist_manager.load_liked_songs_for_user")
def test_song_lookup_multiple_and_select(mock_load, mock_input):
    mock_load.return_value = [
        {"title": "Hello", "artist": "A", "genre": "Pop", "year": "2020",
         "album": "A1", "date_added": "2020-01-01", "duration": "3:30"},
        {"title": "Hello Again", "artist": "B", "genre": "Rock",
         "year": "2021", "album": "B1", "date_added": "2021-01-01",
         "duration": "4:00"}
    ]
    mock_input.side_effect = ["Hello", "1", "B", "B"]
    liked_songs = mock_load.return_value
    playlist_manager.song_lookup_screen(liked_songs)

# ---------------- Auth (Register/Login) ----------------

@patch("playlist_manager._safe_input")
def test_register_screen_success(mock_input):
    playlist_manager.users.clear()
    mock_input.side_effect = ["newuser", "password123"]
    playlist_manager.register_screen()
    assert "newuser" in playlist_manager.users


@patch("playlist_manager._safe_input")
def test_register_screen_existing_user(mock_input):
    playlist_manager.users.clear()
    playlist_manager.users["existing"] = "pass"
    mock_input.side_effect = ["existing", "newuser", "pass1234"]
    playlist_manager.register_screen()
    assert "newuser" in playlist_manager.users


@patch("playlist_manager._safe_input")
def test_login_screen_success(mock_input):
    playlist_manager.users["user1"] = "secret"
    mock_input.side_effect = ["user1", "secret"]
    username = playlist_manager.login_screen()
    assert username == "user1"


@patch("playlist_manager._safe_input")
def test_login_screen_fail_then_back(mock_input):
    playlist_manager.users["user1"] = "secret"
    mock_input.side_effect = ["user1", "wrong", "B"]
    username = playlist_manager.login_screen()
    assert username is None

# ---------------- Logout/Quit Confirmations ----------------

@patch("playlist_manager._safe_input")
def test_confirm_logout_screen_yes(mock_input):
    mock_input.side_effect = ["Y"]
    assert playlist_manager.confirm_logout_screen() is True


@patch("playlist_manager._safe_input")
def test_confirm_logout_screen_no(mock_input):
    mock_input.side_effect = ["N"]
    assert playlist_manager.confirm_logout_screen() is False


@patch("playlist_manager._safe_input")
def test_confirm_quit_screen_yes(mock_input):
    mock_input.side_effect = ["Y"]
    assert playlist_manager.confirm_quit_screen() is True


@patch("playlist_manager._safe_input")
def test_confirm_quit_screen_no(mock_input):
    mock_input.side_effect = ["N"]
    assert playlist_manager.confirm_quit_screen() is False

# ---------------- Recommendation Logic (Mocked send_request) ----------------

@patch("playlist_manager.send_request")
def test_get_recommendations_by_artist(mock_send):
    mock_send.return_value = {"recommendations": [{"title": "Rec1",
                                                   "artist": "Artist1",
                                                   "genre": "Pop"}]}
    recs = playlist_manager.get_recommendations_by_artist("Artist1")
    assert len(recs) == 1
    assert recs[0]["artist"] == "Artist1"


@patch("playlist_manager.send_request")
def test_get_recommendations_by_genre(mock_send):
    mock_send.return_value = {"recommendations": [{"title": "Rec2",
                                                   "artist": "Artist2",
                                                   "genre": "Pop"}]}
    recs = playlist_manager.get_recommendations_by_genre("Pop")
    assert len(recs) == 1
    assert recs[0]["genre"] == "Pop"

# ---------------- Integration Tests (Live Servers Required) ----------------
# These require all microservice servers to be running before executing.

@pytest.mark.integration
def test_live_recommendation_by_genre():
    payload = {"type": "recommend_by_genre", "genre": "rock"}
    response = send_request(payload)
    assert isinstance(response, dict)
    assert "recommendations" in response
    assert isinstance(response["recommendations"], list)

@pytest.mark.integration
def test_live_recommendation_by_artist():
    payload = {"type": "recommend_by_artist", "artist": "The Weeknd"}
    response = send_request(payload)
    assert isinstance(response, dict)
    assert "recommendations" in response
    assert isinstance(response["recommendations"], list)

@pytest.mark.integration
def test_live_recommendation_popular():
    payload = {"type": "recommend_popular"}
    response = send_request(payload)
    assert isinstance(response, dict)
    assert "recommendations" in response
    assert isinstance(response["recommendations"], list)

@pytest.mark.integration
def test_live_random_song_service():
    response = request_random_song()
    assert isinstance(response, dict)
    assert "title" in response
    assert "artist" in response

@pytest.mark.integration
def test_live_song_by_year_service():
    from microservices.song_by_year_service.zeroMQClient import send_year_request
    response = send_year_request(2010)
    assert isinstance(response, dict)
    assert "songs" in response
    assert isinstance(response["songs"], list)


@pytest.mark.integration
def test_live_total_duration_service():
    from microservices.total_duration_service.zeroMQClient import send_duration_request
    response = send_duration_request("user_integration_does_not_need_file")
    assert isinstance(response, dict)
    # Server returns these keys even if there’s no liked_songs file
    assert "total_seconds" in response
    assert "readable" in response
    assert "count_songs" in response
    assert "skipped" in response







