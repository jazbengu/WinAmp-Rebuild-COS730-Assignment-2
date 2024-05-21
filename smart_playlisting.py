import os
import mutagen
from mutagen.easyid3 import EasyID3
from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QComboBox, QSlider, QPushButton, QFileDialog, QMessageBox, QListWidget
)
from PyQt5.QtCore import Qt

class SmartPlaylistCreator(QMainWindow):
    def __init__(self, parent=None, songs_metadata=None):
        super().__init__(parent)
        self.setWindowTitle("Smart Playlist Creator")
        self.setGeometry(100, 100, 600, 400)

        self.song_metadata = songs_metadata if songs_metadata else {}
        self.playlist = []

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # Genre selection
        self.genre_combo = QComboBox()
        self.genre_combo.addItem("All")
        self.genre_combo.addItems(set(metadata['genre'] for metadata in self.song_metadata.values()))
        layout.addWidget(self.genre_combo)

        # Tempo selection
        self.tempo_slider = QSlider(Qt.Horizontal)
        self.tempo_slider.setRange(0, 200)
        self.tempo_slider.setValue(100)
        layout.addWidget(self.tempo_slider)

        # Artist selection
        self.artist_combo = QComboBox()
        self.artist_combo.addItem("All")
        self.artist_combo.addItems(set(metadata['artist'] for metadata in self.song_metadata.values()))
        layout.addWidget(self.artist_combo)

        # Create playlist button
        self.create_playlist_button = QPushButton("Create Playlist")
        self.create_playlist_button.clicked.connect(self.create_smart_playlist)
        layout.addWidget(self.create_playlist_button)

        # Playlist view
        self.playlist_view = QListWidget()
        layout.addWidget(self.playlist_view)

        # Save playlist button
        self.save_playlist_button = QPushButton("Save Playlist")
        self.save_playlist_button.clicked.connect(self.save_playlist)
        layout.addWidget(self.save_playlist_button)

    def create_smart_playlist(self):
        selected_genre = self.genre_combo.currentText()
        selected_tempo = self.tempo_slider.value()
        selected_artist = self.artist_combo.currentText()

        self.playlist = [
            song_path
            for song_path, metadata in self.song_metadata.items()
            if (selected_genre == "All" or metadata["genre"] == selected_genre)
            and (selected_artist == "All" or metadata["artist"] == selected_artist)
            and abs(metadata["tempo"] - selected_tempo) <= 10
        ]

        self.playlist_view.clear()
        for song_path in self.playlist:
            self.playlist_view.addItem(os.path.basename(song_path))

    def save_playlist(self):
        if not self.playlist:
            QMessageBox.warning(self, "Empty Playlist", "Please create a playlist first.")
            return

        file_dialog = QFileDialog()
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setDefaultSuffix("m3u")
        file_dialog.setNameFilter("Playlist (*.m3u)")
        if file_dialog.exec_():
            save_path = file_dialog.selectedFiles()[0]
            with open(save_path, 'w') as file:
                file.write(f"# Playlist\n")
                for song_path in self.playlist:
                    file.write(song_path + '\n')
            QMessageBox.information(self, "Playlist Saved", "Playlist has been saved.")
