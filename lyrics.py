import requests
import lyricsgenius
def fetch_lyrics(artist, song):
    # Create a LyricsGenius object with your Genius API access token
    genius = lyricsgenius.Genius('o2HZ6LDQo8zYrgn-6m3d8QkhbXY5QANj1IYWAw6LPbusV1Xzg5rcWSYIk1bnPKPL')
    song = genius.search_song(song, artist)
    # Print the lyrics
    return song.lyrics



