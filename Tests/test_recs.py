import unittest
from unittest.mock import patch, MagicMock
from myapp.recs import Recommendations
import requests
from PyQt5.QtWidgets import QApplication, QTabWidget, QTextEdit

class TestRecommendations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])

    def setUp(self):
        self.api_key = 'test_api_key'
        self.recommendations = Recommendations(self.api_key)

    @patch('recs.requests.get')
    def test_get_recommendations_success(self, mock_get):
        mock_response = MagicMock()
        expected_json = {
            "similartracks": {
                "track": [
                    {
                        "name": "Test Track",
                        "artist": {"name": "Test Artist"}
                    }
                ]
            }
        }
        mock_response.json.return_value = expected_json
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        artist = 'Test Artist'
        track = 'Test Track'
        result = self.recommendations.get_recommendations(artist, track)

        self.assertEqual(result, expected_json)
        mock_get.assert_called_once()

    @patch('recs.requests.get')
    def test_get_recommendations_failure(self, mock_get):
        mock_get.side_effect = requests.RequestException("Request failed")

        artist = 'Invalid Artist'
        track = 'Invalid Track'
        result = self.recommendations.get_recommendations(artist, track)

        self.assertIsNone(result)
        mock_get.assert_called_once()

    @patch('recs.requests.get')
    def test_get_similar_artists_success(self, mock_get):
        mock_response = MagicMock()
        expected_json = {
            "similarartists": {
                "artist": [
                    {"name": "Similar Artist"}
                ]
            }
        }
        mock_response.json.return_value = expected_json
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        artist = 'Test Artist'
        result = self.recommendations.get_similar_artists(artist)

        self.assertEqual(result, expected_json)
        mock_get.assert_called_once()

    @patch('recs.requests.get')
    def test_get_similar_artists_failure(self, mock_get):
        mock_get.side_effect = requests.RequestException("Request failed")

        artist = 'Invalid Artist'
        result = self.recommendations.get_similar_artists(artist)

        self.assertIsNone(result)
        mock_get.assert_called_once()

    def test_display_recommendations(self):
        recommendations = {
            "similartracks": {
                "track": [
                    {"name": "Test Track", "artist": {"name": "Test Artist"}}
                ]
            }
        }
        tab_widget = QTabWidget()
        self.recommendations.display_recommendations(recommendations, tab_widget)

        self.assertEqual(tab_widget.count(), 1)
        self.assertEqual(tab_widget.tabText(0), 'Recommendations')

        text_edit = tab_widget.widget(0)
        self.assertIsInstance(text_edit, QTextEdit)
        self.assertEqual(text_edit.toPlainText(), 'Artist: Test Artist\nTrack: Test Track\n\n')

    def test_display_recommendations_no_tracks(self):
        recommendations = {"similartracks": {"track": []}}
        tab_widget = QTabWidget()
        self.recommendations.display_recommendations(recommendations, tab_widget)

        self.assertEqual(tab_widget.count(), 1)
        self.assertEqual(tab_widget.tabText(0), 'Recommendations')

        text_edit = tab_widget.widget(0)
        self.assertIsInstance(text_edit, QTextEdit)
        self.assertEqual(text_edit.toPlainText(), 'No similar tracks found.')

    def test_display_artist_recommendations(self):
        recommendations = {
            "similarartists": {
                "artist": [
                    {"name": "Similar Artist"}
                ]
            }
        }
        tab_widget = QTabWidget()
        self.recommendations.display_artist_recommendations(recommendations, tab_widget)

        self.assertEqual(tab_widget.count(), 1)
        self.assertEqual(tab_widget.tabText(0), 'Artist Recommendations')

        text_edit = tab_widget.widget(0)
        self.assertIsInstance(text_edit, QTextEdit)
        self.assertEqual(text_edit.toPlainText(), 'Similar Artists:\n\nArtist: Similar Artist\n\n')

    def test_display_artist_recommendations_no_artists(self):
        recommendations = {"similarartists": {"artist": []}}
        tab_widget = QTabWidget()
        self.recommendations.display_artist_recommendations(recommendations, tab_widget)

        self.assertEqual(tab_widget.count(), 1)
        self.assertEqual(tab_widget.tabText(0), 'Artist Recommendations')

        text_edit = tab_widget.widget(0)
        self.assertIsInstance(text_edit, QTextEdit)
        self.assertEqual(text_edit.toPlainText(), 'No similar artists found.')

if __name__ == '__main__':
    unittest.main()
