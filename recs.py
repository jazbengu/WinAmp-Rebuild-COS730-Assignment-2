import json
import requests
from PyQt5.QtWidgets import QTextEdit

class Recommendations:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_recommendations(self, artist, track):
        base_url = 'http://ws.audioscrobbler.com/2.0/'
        params = {
            'method': 'track.getSimilar',
            'api_key': self.api_key,
            'artist': artist,
            'track': track,
            'format': 'json'
        }
        response = requests.get(base_url, params=params)
        return response.json()

    def display_recommendations(self, recommendations, tab_widget):
        recommendations_tab = QTextEdit()
        recommendations_tab.setReadOnly(True)
        recommendations_tab.setText(json.dumps(recommendations, indent=4))
        tab_widget.addTab(recommendations_tab, 'Recommendations')

    def fetch_recommendations(self, artist, track, tab_widget):
        # Fetch recommendations from Last.fm API
        recommendations = self.get_recommendations(artist, track)

        # Display recommendations in the UI
        self.display_recommendations(recommendations, tab_widget)
