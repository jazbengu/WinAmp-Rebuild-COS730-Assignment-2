import requests
from PyQt5.QtWidgets import QTextEdit
import json
from urllib.parse import quote

class Recommendations:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_recommendations(self, artist, track):
        base_url = 'http://ws.audioscrobbler.com/2.0/'
        params = {
            'method': 'track.getsimilar',
            'api_key': self.api_key,
            'artist': quote(artist),
            'track': quote(track),
            'format': 'json'
        }
        try:
            response = requests.get(base_url, params=params)
            print(f"API Request URL: {response.url}")  # Debugging print
            response.raise_for_status()  # Raise an exception for HTTP errors
            response_json = response.json()
            print(f"API Response: {json.dumps(response_json, indent=4)}")  # Debugging print
            return response_json
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def get_similar_artists(self, artist):
        base_url = 'http://ws.audioscrobbler.com/2.0/'
        params = {
            'method': 'artist.getsimilar',
            'api_key': self.api_key,
            'artist': quote(artist),
            'format': 'json'
        }
        try:
            response = requests.get(base_url, params=params)
            print(f"Artist Similar API Request URL: {response.url}")  # Debugging print
            response.raise_for_status()  # Raise an exception for HTTP errors
            response_json = response.json()
            print(f"Artist Similar API Response: {json.dumps(response_json, indent=4)}")  # Debugging print
            return response_json
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def display_recommendations(self, recommendations, tab_widget):
        recommendations_tab = QTextEdit()
        recommendations_tab.setReadOnly(True)

        if recommendations and 'similartracks' in recommendations and 'track' in recommendations['similartracks']:
            tracks = recommendations['similartracks']['track']
            if tracks:
                recommendations_text = ""
                for track in tracks:
                    track_name = track['name']
                    artist_name = track['artist']['name']
                    recommendations_text += f"Artist: {artist_name}\nTrack: {track_name}\n\n"
                recommendations_tab.setText(recommendations_text)
            else:
                recommendations_tab.setText("No similar tracks found.")
        else:
            recommendations_tab.setText("Error retrieving recommendations.")

        tab_widget.addTab(recommendations_tab, 'Recommendations')

    def display_artist_recommendations(self, recommendations, tab_widget):
        recommendations_tab = QTextEdit()
        recommendations_tab.setReadOnly(True)

        if recommendations and 'similarartists' in recommendations and 'artist' in recommendations['similarartists']:
            artists = recommendations['similarartists']['artist']
            if artists:
                recommendations_text = "Similar Artists:\n\n"
                for artist in artists:
                    artist_name = artist['name']
                    recommendations_text += f"Artist: {artist_name}\n\n"
                recommendations_tab.setText(recommendations_text)
            else:
                recommendations_tab.setText("No similar artists found.")
        else:
            recommendations_tab.setText("Error retrieving recommendations.")

        tab_widget.addTab(recommendations_tab, 'Artist Recommendations')

    def fetch_recommendations(self, artist, track, tab_widget):
        # Fetch recommendations from Last.fm API
        recommendations = self.get_recommendations(artist, track)

        if recommendations and 'similartracks' in recommendations and recommendations['similartracks']['track']:
            # Display recommendations in the UI
            self.display_recommendations(recommendations, tab_widget)
        else:
            # If no similar tracks found, fetch similar artists
            artist_recommendations = self.get_similar_artists(artist)
            self.display_artist_recommendations(artist_recommendations, tab_widget)
