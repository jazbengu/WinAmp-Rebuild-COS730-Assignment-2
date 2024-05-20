import json
import sys
import os
import pygame
from pygame import mixer
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QUrl, QTime, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QTextEdit, QFileDialog, QSlider, QMenuBar, QAction, QDialog, QTabWidget
from PyQt5.QtMultimedia import QMediaContent, QMediaPlaylist
from mutagen.easyid3 import EasyID3
import librosa
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from recs import Recommendations
from smart_playlisting import SmartPlaylistDialog
from lyrics import fetch_lyrics


class WinampClone(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Winamp Clone")
        self.setGeometry(100, 100, 800, 600)
        mixer.init()  # Initialize Pygame mixer
        self.playlist_view = QListWidget()
        self.current_song_label = QLabel()
        self.play_button = QPushButton("Play")
        self.pause_button = QPushButton("Pause")
        self.stop_button = QPushButton("Stop")
        self.previous_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setValue(50)  # Example initial volume
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setRange(0, 0)
        self.current_time_label = QLabel("00:00")
        self.total_time_label = QLabel("00:00")
        self.playlist = []  # Store playlist as a list of file paths
        self.current_song_index = -1  # Index of the currently playing song
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        control_layout = QHBoxLayout()
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.pause_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addWidget(self.previous_button)
        control_layout.addWidget(self.next_button)
        time_layout = QHBoxLayout()
        time_layout.addWidget(self.current_time_label)
        time_layout.addWidget(self.progress_slider)
        time_layout.addWidget(self.total_time_label)
        layout = QVBoxLayout()
        layout.addWidget(self.playlist_view)
        layout.addWidget(self.current_song_label)
        layout.addLayout(control_layout)
        layout.addLayout(time_layout)
        layout.addWidget(self.volume_slider)
        central_widget.setLayout(layout)
        self.create_menu()
        self.init_connections()

        # Create tab widget
        self.tabs = QTabWidget()
        self.lyrics_tab = QTextEdit()
        self.lyrics_tab.setReadOnly(True)
        self.lyrics_tab.setMinimumHeight(100)
        self.recommendations_tab = QTextEdit()
        self.recommendations_tab.setReadOnly(True)
        self.recommendations_tab.setMinimumHeight(100)
        self.tabs.addTab(self.lyrics_tab, "Lyrics")
        self.tabs.addTab(self.recommendations_tab, "Recommendations")
        layout.addWidget(self.tabs)

    def create_menu(self):
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")

        fetch_lyrics_action = QAction("Fetch Lyrics", self)
        fetch_lyrics_action.triggered.connect(self.fetch_lyrics)
        file_menu.addAction(fetch_lyrics_action)

        recommend_action = QAction("Recommend", self)
        recommend_action.triggered.connect(self.recommend)
        file_menu.addAction(recommend_action)

        add_music_action = QAction("Add Music", self)
        add_music_action.triggered.connect(self.add_music_dialog)
        file_menu.addAction(add_music_action)

        # Playlisting menu
        playlisting_menu = menu_bar.addMenu("Playlisting")

        create_smart_playlist_action = QAction("Create Smart Playlist", self)
        create_smart_playlist_action.triggered.connect(self.create_smart_playlist)
        playlisting_menu.addAction(create_smart_playlist_action)

        load_playlist_action = QAction("Load Playlist", self)
        load_playlist_action.triggered.connect(self.load_playlist)
        playlisting_menu.addAction(load_playlist_action)

        save_playlist_action = QAction("Save Playlist", self)
        save_playlist_action.triggered.connect(self.save_playlist)
        playlisting_menu.addAction(save_playlist_action)

    def init_connections(self):
        self.play_button.clicked.connect(self.play)
        self.pause_button.clicked.connect(self.pause)
        self.stop_button.clicked.connect(self.stop)
        self.previous_button.clicked.connect(self.play_previous)
        self.next_button.clicked.connect(self.play_next)
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.playlist_view.doubleClicked.connect(self.play_selected_song)

    def play(self):
        if not pygame.mixer.music.get_busy() and self.current_song_index != -1:
            pygame.mixer.music.load(self.playlist[self.current_song_index])
            pygame.mixer.music.play()

    def pause(self):
        pygame.mixer.music.pause()

    def stop(self):
        pygame.mixer.music.stop()

    def set_volume(self, volume):
        pygame.mixer.music.set_volume(volume / 100)

    def create_smart_playlist(self):
        dialog = SmartPlaylistDialog()
        if dialog.exec_() == QDialog.Accepted:
            playlist_name = dialog.playlist_name_edit.text()
            criteria = {
                "tempo": dialog.tempo_checkbox.isChecked(),
                "mood": dialog.mood_checkbox.isChecked(),
                "artist": dialog.artist_checkbox.isChecked(),
                "genre": dialog.genre_checkbox.isChecked()
            }
            save_dir = QFileDialog.getExistingDirectory(self, 'Select Directory to Save Playlist')
            if save_dir:
                self.generate_playlist(playlist_name, criteria, save_dir)

    def generate_playlist(self, playlist_name, criteria, save_dir):
        playlist_tracks = []
        music_folder = '/path/to/your/music/folder'  # Update this path to your music folder
        for root, dirs, files in os.walk(music_folder):
            for file in files:
                if file.endswith('.mp3'):
                    file_path = os.path.join(root, file)
                    print(f"Checking file: {file_path}")  # Debugging line
                    if self.check_criteria(file_path, criteria):
                        playlist_tracks.append(file_path)
                        if len(playlist_tracks) >= 20:
                            break
            if len(playlist_tracks) >= 20:
                break

        if playlist_tracks:
            playlist_file_path = os.path.join(save_dir, f"{playlist_name}.m3u")
            with open(playlist_file_path, 'w') as playlist_file:
                for track in playlist_tracks:
                    playlist_file.write(track + '\n')
            print(f"Playlist created: {playlist_file_path}")
        else:
            print("No tracks matched the criteria.")

    def check_criteria(self, file_path, criteria):
        try:
            y, sr = librosa.load(file_path, sr=None)
            tempo = librosa.beat.tempo(y=y, sr=sr)[0]
            audio = EasyID3(file_path)
            artist = audio.get("artist", ["Unknown Artist"])[0]
            genre = audio.get("genre", ["Unknown Genre"])[0]

            print(f"File: {file_path}, Tempo: {tempo}, Artist: {artist}, Genre: {genre}")  # Debugging line

            if criteria["tempo"] and not (tempo >= 100 and tempo <= 150):  # Example tempo range
                return False
            if criteria["artist"] and artist.lower() != "specific artist".lower():
                return False
            if criteria["genre"] and genre.lower() != "specific genre".lower():
                return False
            if criteria["mood"] and not self.check_mood(y):
                return False

            return True
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            return False

    def check_mood(self, y):
        # Simulate a mood analysis
        # Implement your mood analysis logic here or replace it with an actual API call
        return True

    def add_music_dialog(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.DirectoryOnly)
        file_dialog.setOption(QFileDialog.ShowDirsOnly, True)
        if file_dialog.exec_():
            directories = file_dialog.selectedFiles()
            for directory in directories:
                self.add_music_from_directory(directory)

    def add_music_from_directory(self, directory):
        music_extensions = ('.mp3', '.wav', '.m4a', '.wma', '.flac', '.aac')
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(music_extensions):
                    self.playlist.append(os.path.join(root, file))
                    self.playlist_view.addItem(os.path.join(root, file))

    def update_song_label(self):
        if pygame.mixer.music.get_busy():
            current_song_path = self.playlist[self.current_song_index]
            try:
                audio = EasyID3(current_song_path)
                song_name = audio.get("title", ["Unknown Title"])[0]
                artist_name = audio.get("artist", ["Unknown Artist"])[0]
                print(song_name, artist_name)
                self.current_song_label.setText(f"Now Playing: {song_name} - {artist_name}")
            except Exception as e:
                print(f"Error reading metadata: {e}")
                self.current_song_label.setText(f"Now Playing: {os.path.basename(current_song_path)}")

    def play_previous(self):
        if self.current_song_index > 0:
            self.current_song_index -= 1
            self.play()

    def play_next(self):
        if self.current_song_index < len(self.playlist) - 1:
            self.current_song_index += 1
            self.play()

    def load_playlist(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("Playlist (*.m3u)")
        if file_dialog.exec_():
            playlist_files = file_dialog.selectedFiles()
            for playlist_file in playlist_files:
                with open(playlist_file, 'r') as file:
                    for line in file:
                        if line.strip():
                            self.playlist.append(line.strip())
                            self.playlist_view.addItem(line.strip())

    def save_playlist(self):
        file_dialog = QFileDialog()
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setDefaultSuffix("m3u")
        file_dialog.setNameFilter("Playlist (*.m3u)")
        if file_dialog.exec_():
            save_path = file_dialog.selectedFiles()[0]
            with open(save_path, 'w') as file:
                for song_path in self.playlist:
                    file.write(song_path + '\n')

    def fetch_lyrics(self):
        index = self.playlist_view.currentRow()
        if index >= 0:
            song_path = self.playlist[index]
            try:
                audio = EasyID3(song_path)
                song_name = audio["title"][0]
                artist_name = audio.get("artist", ["Unknown"])[0]
            except Exception as e:
                print(f"Error reading metadata: {e}")
                song_name = os.path.splitext(os.path.basename(song_path))[0]
                artist_name = "Unknown"
            lyrics = fetch_lyrics(song_name, artist_name)
            self.lyrics_tab.setPlainText(lyrics)

    def recommend(self):
        if self.current_song_index != -1:
            current_song_path = self.playlist[self.current_song_index]
            try:
                audio = EasyID3(current_song_path)
                artist_name = audio.get("artist", ["Unknown Artist"])[0]
                song_name = audio.get("title", ["Unknown Title"])[0]
            except Exception as e:
                print(f"Error reading metadata: {e}")
                artist_name = "Unknown Artist"
                song_name = "Unknown Title"

            print(f"Artist: {artist_name}, Track: {song_name}")  # Debugging print

            recommendations = Recommendations('f2681cc2f1d85058b663546766ad0c82')
            recommendations.fetch_recommendations(artist_name, song_name, self.tabs)

    def play_selected_song(self):
        index = self.playlist_view.currentRow()
        if index >= 0:
            self.current_song_index = index
            self.play()


def main():
    app = QApplication(sys.argv)
    winamp = WinampClone()
    winamp.setStyleSheet(open("style.qss").read())
    winamp.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()


