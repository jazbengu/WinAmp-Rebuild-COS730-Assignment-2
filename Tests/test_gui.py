import unittest
import sys
from PyQt5.QtWidgets import QApplication
from main import WinampClone, PlaylistCreator


class TestWinampIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)

    @classmethod
    def tearDownClass(cls):
        sys.exit()

    def test_playlist_creation_and_playback(self):
        # Create the WinampClone instance
        winamp = WinampClone()

        # Add some music to the playlist
        winamp.add_music_from_directory("C:/Users/zozoj/Music")

        # Simulate user interaction: Create a playlist
        winamp.create_playlist_dialog()
        playlist_creator_dialog = winamp.playlist_creator_dialog
        playlist_creator_dialog.playlist_name_input.setText("Test Playlist")
        playlist_creator_dialog.save_location = "C:/Users/zozoj/Music/test_playlist.json"
        playlist_creator_dialog.create_playlist()

        # Load the created playlist
        winamp.load_playlist()

        # Play the first song in the playlist
        winamp.play()

        # Verify that the current song label is updated
        self.assertEqual(winamp.current_song_label.text(), "Now Playing: Nectar - BM ft Jay Park")

        # Stop the playback
        winamp.stop()

        # Add more assertions as needed to test other functionalities


if __name__ == '__main__':
    unittest.main()
