import unittest
from unittest.mock import patch, MagicMock
import sys
import os

from PyQt5.QtWidgets import QApplication
from main import WinampClone, PlaylistCreator


class TestWinampClone(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)

    def setUp(self):
        self.winamp = WinampClone()

    def test_add_music_from_directory(self):
        # Mock os.walk to simulate adding music files from a directory
        mock_walk = [
            ('/music', ('subdir',), ('song1.mp3', 'song2.mp3')),
            ('/music/subdir', (), ('song3.mp3',)),
        ]
        with patch('os.walk', return_value=mock_walk):
            self.winamp.add_music_from_directory('/music')
            self.assertEqual(len(self.winamp.playlist), 3)
            self.assertIn('/music/song1.mp3', self.winamp.playlist)
            self.assertIn('/music/song2.mp3', self.winamp.playlist)
            self.assertIn('/music/subdir/song3.mp3', self.winamp.playlist)

    def test_play(self):
        # Mock pygame.mixer.music.load and play
        with patch('pygame.mixer.music.load') as mock_load, \
                patch('pygame.mixer.music.play') as mock_play, \
                patch.object(self.winamp, 'update_song_label'), \
                patch.object(self.winamp, 'update_duration'), \
                patch('pygame.mixer.music.get_length', return_value=240):
            self.winamp.playlist = ['/music/song1.mp3']
            self.winamp.current_song_index = 0
            self.winamp.play()
            mock_load.assert_called_once_with('/music/song1.mp3')
            mock_play.assert_called_once()

    def test_pause(self):
        with patch('pygame.mixer.music.pause') as mock_pause:
            self.winamp.pause()
            mock_pause.assert_called_once()

    def test_stop(self):
        with patch('pygame.mixer.music.stop') as mock_stop:
            self.winamp.stop()
            mock_stop.assert_called_once()

    def test_create_playlist(self):
        dialog = PlaylistCreator()
        mock_song_list = ['/music/song1.mp3', '/music/song2.mp3']
        dialog.populate_song_list(mock_song_list)
        dialog.playlist_name_input.setText("My Playlist")
        dialog.song_list.selectAll()

        with patch('PyQt5.QtWidgets.QFileDialog.exec_', return_value=True), \
                patch('PyQt5.QtWidgets.QFileDialog.selectedFiles', return_value=["/music/MyPlaylist.m3u"]), \
                patch('builtins.open', unittest.mock.mock_open()) as mock_file, \
                patch('PyQt5.QtWidgets.QMessageBox.information'):
            dialog.save_location = "/music/MyPlaylist.m3u"
            dialog.create_playlist()
            mock_file().write.assert_any_call("# Playlist: My Playlist\n")
            mock_file().write.assert_any_call("/music/song1.mp3 # song1\n")
            mock_file().write.assert_any_call("/music/song2.mp3 # song2\n")


if __name__ == '__main__':
    unittest.main()
