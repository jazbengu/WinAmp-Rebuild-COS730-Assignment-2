import json
import os
import numpy as np
from PyQt5.QtCore import Qt
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QLineEdit, QPushButton, QFileDialog, QMessageBox, QComboBox, QSlider, QLabel
from mutagen.easyid3 import EasyID3
from collections import Counter

class SmartPlaylistCreator(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Playlist Creator")
        self.setGeometry(100, 100, 600, 600)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Song list
        self.song_list = QListWidget()
        self.song_list.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.song_list)

        # Playlist name input
        self.playlist_name_input = QLineEdit()
        self.playlist_name_input.setPlaceholderText("Enter playlist name")
        layout.addWidget(self.playlist_name_input)

        # Playlist criteria
        self.criteria_layout = QVBoxLayout()
        layout.addLayout(self.criteria_layout)

        self.artist_combo = QComboBox()
        self.artist_combo.setPlaceholderText("Select artist")
        self.criteria_layout.addWidget(self.artist_combo)

        self.mood_combo = QComboBox()
        self.mood_combo.addItems(["Sad", "Happy", "Calm", "Energetic"])
        self.criteria_layout.addWidget(self.mood_combo)

        self.tempo_slider = QSlider(Qt.Orientation.Horizontal)
        self.tempo_slider.setMinimum(0)
        self.tempo_slider.setMaximum(200)
        self.tempo_slider.setValue(100)
        self.tempo_label = QLabel("Tempo: 100 BPM")
        self.criteria_layout.addWidget(self.tempo_label)
        self.criteria_layout.addWidget(self.tempo_slider)

        self.genre_combo = QComboBox()
        self.genre_combo.setPlaceholderText("Select genre")
        self.criteria_layout.addWidget(self.genre_combo)

        # Save location button
        self.save_location_button = QPushButton("Choose Save Location")
        self.save_location_button.clicked.connect(self.choose_save_location)
        layout.addWidget(self.save_location_button)

        # Create playlist button
        self.create_playlist_button = QPushButton("Create Playlist")
        self.create_playlist_button.clicked.connect(self.create_playlist)
        layout.addWidget(self.create_playlist_button)

        self.save_location = None
        self.song_data = []

    def choose_save_location(self):
        file_dialog = QFileDialog()
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setDefaultSuffix("json")
        file_dialog.setNameFilter("Playlist (*.json)")
        if file_dialog.exec_():
            self.save_location = file_dialog.selectedFiles()[0]
            self.save_location_button.setText(f"Save Location: {self.save_location}")

    def create_playlist(self):
        playlist_name = self.playlist_name_input.text().strip()
        if not playlist_name:
            QMessageBox.warning(self, "Invalid Name", "Please enter a valid name for the playlist.")
            return

        selected_songs = [self.song_list.item(i).text() for i in range(self.song_list.count()) if self.song_list.item(i).isSelected()]
        if not selected_songs:
            QMessageBox.warning(self, "Empty Playlist", "Please select songs for the playlist.")
            return

        if not self.save_location:
            QMessageBox.warning(self, "No Save Location", "Please choose a save location for the playlist.")
            return

        # Get user-selected criteria
        artist = self.artist_combo.currentText()
        mood = self.mood_combo.currentText().lower()
        tempo = self.tempo_slider.value()
        genre = self.genre_combo.currentText()

        smart_playlist = self.create_smart_playlist(selected_songs, artist, mood, tempo, genre)

        self.save_playlist(playlist_name, smart_playlist, self.save_location)
        QMessageBox.inform
        # Fetch song data
        self.fetch_song_data(selected_songs)

        # Filter songs based on criteria
        filtered_songs = self.filter_songs(artist, mood, tempo, genre)

        return filtered_songs


    def fetch_song_data(self, song_paths):
        self.song_data = []
        for song_path in song_paths:
            try:
                audio = EasyID3(song_path)
                title = audio.get("title", ["Unknown"])[0]
                artist = audio.get("artist", ["Unknown"])[0]
                mood = self.predict_mood(audio)
                tempo = self.predict_tempo(audio)
                genre = self.predict_genre(audio)
                self.song_data.append({
                    "path": song_path,
                    "artist": artist,
                    "title": title,
                    "mood": mood,
                    "tempo": tempo,
                    "genre": genre
                })
            except Exception:
                pass

    def filter_songs(self, artist, mood, tempo, genre):
        filtered_songs = self.song_data.copy()

        if artist:
            filtered_songs = [song for song in filtered_songs if song["artist"] == artist]
        if mood:
            filtered_songs = [song for song in filtered_songs if song["mood"] == mood]
        if tempo:
            filtered_songs = [song for song in filtered_songs if abs(song["tempo"] - tempo) <= 10]
        if genre:
            filtered_songs = [song for song in filtered_songs if song["genre"] == genre]


        return [song["path"] for song in filtered_songs]

    def predict_mood(self, audio):
        features = self.extract_audio_features(audio)
        mood_model = self.load_mood_model()
        mood_prediction = mood_model.predict([features])[0]
        return mood_prediction

    def predict_tempo(self, audio):
        features = self.extract_audio_features(audio)
        tempo_model = self.load_tempo_model()
        tempo_prediction = tempo_model.predict([features])[0]
        return tempo_prediction

    def predict_genre(self, audio):
        features = self.extract_audio_features(audio)
        genre_model = self.load_genre_model()
        genre_prediction = genre_model.predict([features])[0]
        return genre_prediction


    def load_mood_model(self):
        mood_model = RandomForestClassifier()
        mood_model.load("mood_model.pkl")
        return mood_model

    def load_tempo_model(self):
        tempo_model = RandomForestRegressor()
        tempo_model.load("tempo_model.pkl")
        return tempo_model

    def load_genre_model(self):
        genre_model = RandomForestClassifier()
        genre_model.load("genre_model.pkl")
        return genre_model

    def save_playlist(self, playlist_name, song_paths, save_location):
        playlist_data = {
            "playlist_name": playlist_name,
            "songs": song_paths
        }
        with open(save_location, 'w', encoding='utf-8') as file:
            json.dump(playlist_data, file, indent=4)


    def populate_song_list(self, song_paths):
        for song_path in song_paths:
            song_title = self.get_song_title(song_path)
            self.song_list.addItem(f"{song_title} ({song_path})")

    def get_song_title(self, song_path):
        try:
            audio = EasyID3(song_path)
            return audio["title"][0]
        except Exception:
            return os.path.splitext(os.path.basename(song_path))[0]
