import unittest
from unittest.mock import patch
from PyQt5.QtWidgets import QApplication
from smart_playlisting import SmartPlaylistCreator

class TestSmartPlaylistCreator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])

    def setUp(self):
        song_metadata = {
            "/path/to/song1.mp3": {"genre": "Rock", "artist": "Artist1", "tempo": 120},
            "/path/to/song2.mp3": {"genre": "Jazz", "artist": "Artist2", "tempo": 100},
            "/path/to/song3.mp3": {"genre": "Rock", "artist": "Artist1", "tempo": 130},
        }
        self.playlist_creator = SmartPlaylistCreator(songs_metadata=song_metadata)

    def test_create_smart_playlist_all(self):
        self.playlist_creator.genre_combo.setCurrentText("All")
        self.playlist_creator.artist_combo.setCurrentText("All")
        self.playlist_creator.tempo_slider.setValue(120)

        self.playlist_creator.create_smart_playlist()

        expected_playlist = [
            "/path/to/song1.mp3",
            "/path/to/song3.mp3"
        ]
        self.assertEqual(self.playlist_creator.playlist, expected_playlist)
        self.assertEqual(self.playlist_creator.playlist_view.count(), len(expected_playlist))

    def test_create_smart_playlist_genre(self):
        self.playlist_creator.genre_combo.setCurrentText("Jazz")
        self.playlist_creator.artist_combo.setCurrentText("All")
        self.playlist_creator.tempo_slider.setValue(100)

        self.playlist_creator.create_smart_playlist()

        expected_playlist = [
            "/path/to/song2.mp3"
        ]
        self.assertEqual(self.playlist_creator.playlist, expected_playlist)
        self.assertEqual(self.playlist_creator.playlist_view.count(), len(expected_playlist))

    def test_save_playlist_empty(self):
        with patch('PyQt5.QtWidgets.QMessageBox.warning') as mock_warning:
            self.playlist_creator.save_playlist()
            mock_warning.assert_called_once_with(
                self.playlist_creator, "Empty Playlist", "Please create a playlist first."
            )

    def test_save_playlist(self):
        self.playlist_creator.playlist = ["/path/to/song1.mp3", "/path/to/song3.mp3"]

        with patch('PyQt5.QtWidgets.QFileDialog.exec_', return_value=True), \
             patch('PyQt5.QtWidgets.QFileDialog.selectedFiles', return_value=["/path/to/save_playlist.m3u"]), \
             patch('builtins.open', unittest.mock.mock_open()) as mock_file, \
             patch('PyQt5.QtWidgets.QMessageBox.information') as mock_info:

            self.playlist_creator.save_playlist()

            mock_file.assert_called_once_with("/path/to/save_playlist.m3u", 'w')
            mock_file().write.assert_any_call("# Playlist\n")
            mock_file().write.assert_any_call("/path/to/song1.mp3\n")
            mock_file().write.assert_any_call("/path/to/song3.mp3\n")
            mock_info.assert_called_once_with(
                self.playlist_creator, "Playlist Saved", "Playlist has been saved."
            )

if __name__ == '__main__':
    unittest.main()
