import unittest
from unittest.mock import patch, MagicMock

from lyrics import fetch_lyrics
class TestFetchLyrics(unittest.TestCase):
    @patch('lyrics.lyricsgenius.Genius')
    def test_fetch_lyrics_success(self, MockGenius):
        # Setup
        mock_genius_instance = MockGenius.return_value
        mock_song = MagicMock()
        mock_song.lyrics = "Test lyrics"
        mock_genius_instance.search_song.return_value = mock_song

        # Test
        artist = "Eminem"
        song = "Lose Yourself"
        lyrics = fetch_lyrics(artist, song)

        # Assertions
        MockGenius.assert_called_once_with('o2HZ6LDQo8zYrgn-6m3d8QkhbXY5QANj1IYWAw6LPbusV1Xzg5rcWSYIk1bnPKPL')
        mock_genius_instance.search_song.assert_called_once_with(artist, song)
        self.assertEqual(lyrics, "Test lyrics")

    @patch('lyrics.lyricsgenius.Genius')
    def test_fetch_lyrics_failure(self, MockGenius):
        # Setup
        mock_genius_instance = MockGenius.return_value
        mock_genius_instance.search_song.return_value = None

        # Test
        artist = "Invalid Artist"
        song = "Invalid Song"
        lyrics = fetch_lyrics(artist, song)

        # Assertions
        MockGenius.assert_called_once_with('o2HZ6LDQo8zYrgn-6m3d8QkhbXY5QANj1IYWAw6LPbusV1Xzg5rcWSYIk1bnPKPL')
        mock_genius_instance.search_song.assert_called_once_with(artist, song)
        self.assertEqual(lyrics, 'Not Found')


if __name__ == '__main__':
    unittest.main()
