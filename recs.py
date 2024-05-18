import requests
import json
from PyQt5.QtWidgets import QTextEdit

class Recommendations:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})

    def get_access_token(self):
        auth_url = f'https://accounts.spotify.com/api/token'
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        response = self.session.post(auth_url, json=data)
        return response.json()['access_token']

    def get_recommendations(self, track_id):
        access_token = self.get_access_token()
        base_url = 'https://api.spotify.com/v1/recommendations'
        headers = {'Authorization': f'Bearer {access_token}'}
        params = {
            'seed_tracks': track_id,
            'limit': 10
        }
        response = self.session.get(base_url, headers=headers, params=params)
        return response.json()

    def display_recommendations(self, recommendations, lyrics_tab):
        recommendations_tab = QTextEdit()
        recommendations_tab.setReadOnly(True)
        recommendations_tab.setText(json.dumps(recommendations, indent=4))
        lyrics_tab.addTab(recommendations_tab, 'Recommendations')

    def fetch_recommendations(self, current_song_path):
        track_id = current_song_path.split('/')[-1].split('.')[0]
        recommendations = self.get_recommendations(track_id)
        self.display_recommendations(recommendations, lyrics_tab)