import requests
from bs4 import BeautifulSoup

def fetch_lyrics(song_name, artist_name):
    # Construct search query
    query = f"{song_name} {artist_name} lyrics"
    search_url = f"https://www.google.com/search?q={query}"

    response = requests.get(search_url)

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the div containing the lyrics
    lyrics_div = soup.find('div', class_='BNeawe tAd8D AP7Wnd')

    if lyrics_div:
        lyrics = lyrics_div.get_text('\n')  # Get the text with newlines
        return lyrics
    else:
        return "Lyrics not found"
