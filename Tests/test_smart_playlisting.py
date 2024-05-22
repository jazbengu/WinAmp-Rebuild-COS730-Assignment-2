import unittest
from unittest.mock import MagicMock, patch
from smart_playlisting import SmartPlaylistCreator

class TestSmartPlaylistCreator(unittest.TestCase):

    def setUp(self):
        self.playlist_creator = SmartPlaylistCreator()

    def test_choose_save_location(self):
        with patch('smart_playlisting.QFileDialog') as mock_file_dialog:
            mock_file_dialog.exec_.return_value = True
            mock_file_dialog.selectedFiles.return_value = ['/path/to/save_location.json']

            self.playlist_creator.choose_save_location()

            self.assertEqual(self.playlist_creator.save_location, '/path/to/save_location.json')
            self.assertEqual(self.playlist_creator.save_location_button.text(), 'Save Location: /path/to/save_location.json')

    def test_create_playlist_invalid_name(self):
        self.playlist_creator.playlist_name_input.setText('')
        with patch.object(self.playlist_creator, 'create_smart_playlist'):
            with patch('smart_playlisting.QMessageBox.warning') as mock_warning:
                self.playlist_creator.create_playlist()
                mock_warning.assert_called_once_with(self.playlist_creator, "Invalid Name", "Please enter a valid name for the playlist.")

    def test_create_playlist_empty_selection(self):
        self.playlist_creator.song_list.count = MagicMock(return_value=0)
        with patch.object(self.playlist_creator, 'create_smart_playlist'):
            with patch('smart_playlisting.QMessageBox.warning') as mock_warning:
                self.playlist_creator.create_playlist()
                mock_warning.assert_called_once_with(self.playlist_creator, "Empty Playlist", "Please select songs for the playlist.")

    def test_create_playlist_no_save_location(self):
        self.playlist_creator.song_list.count = MagicMock(return_value=2)  # Mocking two selected songs
        with patch.object(self.playlist_creator, 'create_smart_playlist'):
            with patch('smart_playlisting.QMessageBox.warning') as mock_warning:
                self.playlist_creator.create_playlist()
                mock_warning.assert_called_once_with(self.playlist_creator, "No Save Location", "Please choose a save location for the playlist.")


if __name__ == '__main__':
    unittest.main()
