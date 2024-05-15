import re

import lyricsgenius


def fetch_lyrics(artist, song):
    # Create a LyricsGenius object with your Genius API access token
    genius = lyricsgenius.Genius('o2HZ6LDQo8zYrgn-6m3d8QkhbXY5QANj1IYWAw6LPbusV1Xzg5rcWSYIk1bnPKPL')
    song = genius.search_song(song, artist)

    # Extract only the lyrics and remove additional text using regular expressions
    lyrics = song.lyrics

    # Remove text from 'Contributors' to 'Lyrics'
    lyrics = re.sub(r'\d+ Contributors.*?Lyrics', '', lyrics, flags=re.DOTALL)

    # Remove text from 'Embed' to the end
    lyrics = re.sub(r'Embed.*$', '', lyrics, flags=re.DOTALL)

    # Strip any leading or trailing whitespace
    lyrics = lyrics.strip()

    return lyrics
