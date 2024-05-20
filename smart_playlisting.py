import os
import numpy as np
import librosa
from PyQt5.QtWidgets import QFileDialog, QPushButton, QVBoxLayout, QDialog, QLineEdit, QLabel, QMessageBox
from sklearn.metrics.pairwise import cosine_similarity

class SmartPlaylistDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Smart Playlist")
        self.setGeometry(200, 200, 400, 200)
        self.criteria = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.playlist_name_label = QLabel("Playlist Name:")
        layout.addWidget(self.playlist_name_label)

        self.playlist_name_input = QLineEdit()
        layout.addWidget(self.playlist_name_input)

        self.save_button = QPushButton("Save Playlist")
        self.save_button.clicked.connect(self.save_playlist)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def extract_features(self, file_path):
        try:
            y, sr = librosa.load(file_path)
            features = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            mean_features = np.mean(features, axis=1)
            return mean_features
        except Exception as e:
            print(f"Error extracting features from {file_path}: {e}")
            return None

    def find_similar_songs(self, base_features, music_folder, num_songs=15):
        song_features = []
        song_paths = []

        for root, _, files in os.walk(music_folder):
            for file in files:
                if file.endswith('.mp3'):
                    file_path = os.path.join(root, file)
                    features = self.extract_features(file_path)
                    if features:
                        song_features.append(features)
                        song_paths.append(file_path)

        if not song_features:
            return []

        song_features = np.array(song_features)
        similarities = cosine_similarity([base_features], song_features)[0]
        similar_indices = similarities.argsort()[-num_songs:][::-1]

        similar_songs = [song_paths[i] for i in similar_indices]
        return similar_songs

    def create_smart_playlist(self, seed_song_path, music_folder, save_path):
        base_features = self.extract_features(seed_song_path)
        if not base_features:
            print("Error: Failed to extract features from the seed song.")
            return

        similar_songs = self.find_similar_songs(base_features, music_folder)
        if similar_songs:
            with open(save_path, 'w') as f:
                for song in similar_songs:
                    f.write(f"{song}\n")
            QMessageBox.information(self, "Success", f"Playlist saved to {save_path}")
        else:
            QMessageBox.warning(self, "Warning", "No similar songs found.")

    def save_playlist(self):
        playlist_name = self.playlist_name_input.text().strip()
        if not playlist_name:
            QMessageBox.warning(self, "Warning", "Please enter a playlist name.")
            return

        music_folder = QFileDialog.getExistingDirectory(self, "Select Music Folder")
        if not music_folder:
            return

        seed_song_path, _ = QFileDialog.getOpenFileName(self, "Select Seed Song", "", "Audio Files (*.mp3)")
        if not seed_song_path:
            return

        save_path, _ = QFileDialog.getSaveFileName(self, "Save Playlist", playlist_name, "Playlist Files (*.m3u)")
        if not save_path:
            return

        self.create_smart_playlist(seed_song_path, music_folder, save_path)
