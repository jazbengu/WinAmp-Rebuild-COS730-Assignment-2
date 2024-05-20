import unittest
import tempfile
import numpy as np
from unittest.mock import patch, MagicMock
from PyQt5.QtWidgets import QApplication, QLineEdit

from smart_playlisting import SmartPlaylistDialog


class TestSmartPlaylistDialog(unittest.TestCase):
    def setUp(self):
        self.dialog = SmartPlaylistDialog()

    def test_extract_features(self):
        # Provide a test audio file for the unit test
        test_file = "C:/Users/zozoj/Downloads/Valentine (Live at The Symphony).mp3"
        # Generate dummy features for testing
        mock_features = np.random.rand(13)
        # Mock librosa.load to return dummy features
        with patch("librosa.load", return_value=(mock_features, 22050)):
            features = self.dialog.extract_features(test_file)
            self.assertTrue(np.array_equal(features, mock_features))

    @patch("os.walk")
    def test_find_similar_songs(self, mock_walk):
        # Mock os.walk to return a list of files
        mock_walk.return_value = [("/music_folder", [], ["song1.mp3", "song2.mp3"])]
        # Mock extract_features to return dummy features
        self.dialog.extract_features = MagicMock(return_value=np.random.rand(13))
        base_features = np.random.rand(13)
        similar_songs = self.dialog.find_similar_songs(base_features, "/music_folder")
        self.assertEqual(len(similar_songs), 2)

    @patch("PyQt5.QtWidgets.QFileDialog.getExistingDirectory")
    @patch("PyQt5.QtWidgets.QFileDialog.getOpenFileName")
    @patch("PyQt5.QtWidgets.QFileDialog.getSaveFileName")
    def test_save_playlist(self, mock_getExistingDirectory, mock_getOpenFileName, mock_getSaveFileName):
        mock_getExistingDirectory.return_value = "/music_folder"
        mock_getOpenFileName.return_value = ("seed_song.mp3", "")
        mock_getSaveFileName.return_value = ("playlist.m3u", "")
        self.dialog.create_smart_playlist = MagicMock()
        self.dialog.save_playlist()
        self.dialog.create_smart_playlist.assert_called_once_with("seed_song.mp3", "/music_folder", "playlist.m3u")

if __name__ == "__main__":
    unittest.main()
