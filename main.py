import json
import random
import sys
import os

import mutagen
import pygame
from pygame import mixer
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QUrl, QTime, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, \
    QListWidget, QTextEdit, QFileDialog, QSlider, QMenuBar, QAction, QDialog, QTabWidget, QLineEdit, QMessageBox, \
    QDialogButtonBox, QAbstractItemView, QProgressBar
from PyQt5.QtMultimedia import QMediaContent, QMediaPlaylist
from mutagen.easyid3 import EasyID3
import librosa
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from recs import Recommendations
from smart_playlisting import SmartPlaylistCreator
from lyrics import fetch_lyrics

class PlaylistCreator(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Playlist Creator")
        self.setGeometry(100, 100, 600, 400)

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

        # Save location button
        self.save_location_button = QPushButton("Choose Save Location")
        self.save_location_button.clicked.connect(self.choose_save_location)
        layout.addWidget(self.save_location_button)

        # Create playlist button
        self.create_playlist_button = QPushButton("Create Playlist")
        self.create_playlist_button.clicked.connect(self.create_playlist)
        layout.addWidget(self.create_playlist_button)

        self.save_location = None

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

        self.save_playlist(playlist_name, selected_songs, self.save_location)
        QMessageBox.information(self, "Playlist Created", "Playlist has been created and saved.")

    def save_playlist(self, playlist_name, song_paths, save_location):
        playlist_data = {
            "playlist_name": playlist_name,
            "songs": song_paths
        }
        with open(save_location, 'w', encoding='utf-8') as file:
            json.dump(playlist_data, file, indent=4)

    def get_song_title(self, song_path):
        try:
            audio = EasyID3(song_path)
            return audio["title"][0]
        except Exception:
            return os.path.splitext(os.path.basename(song_path))[0]

    def populate_song_list(self, song_paths):
        for song_path in song_paths:
            song_title = self.get_song_title(song_path)
            self.song_list.addItem(f"{song_title} ({song_path})")



class WinampClone(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Winamp Music Player")
        self.setGeometry(100, 100, 800, 600)
        mixer.init()  # Initialize Pygame mixer
        self.search_box = QLineEdit()
        self.playlist_view = QListWidget()
        self.current_song_label = QLabel()
        self.play_button = QPushButton("Play")
        self.pause_button = QPushButton("Pause")
        self.stop_button = QPushButton("Stop")
        self.previous_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setValue(50)
        self.current_time_label = QLabel("00:00")
        self.total_time_label = QLabel("00:00")
        self.playlist = []
        self.current_song_index = -1
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
        self.current_song_label = QLabel()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        time_layout = QHBoxLayout()
        time_layout.addWidget(self.current_time_label)
        time_layout.addWidget(self.total_time_label)
        layout = QVBoxLayout()
        layout.addWidget(self.playlist_view)
        layout.addWidget(self.current_song_label)
        layout.addWidget(self.progress_bar)
        layout.addLayout(control_layout)
        layout.addLayout(time_layout)
        layout.addWidget(self.volume_slider)
        central_widget.setLayout(layout)
        self.create_menu()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search...")
        self.search_box.textChanged.connect(self.search_library)
        layout.addWidget(self.search_box)
        self.init_connections()


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


        playlisting_menu = menu_bar.addMenu("Playlisting")

        create_playlist_action = QAction("Create Playlist", self)
        create_playlist_action.triggered.connect(self.create_playlist_dialog)
        playlisting_menu.addAction(create_playlist_action)

        load_playlist_action = QAction("Load Playlist", self)
        load_playlist_action.triggered.connect(self.load_playlist)
        playlisting_menu.addAction(load_playlist_action)

        smart_playlist_action = QAction("Smart Playlist", self)
        smart_playlist_action.triggered.connect(self.create_smart_playlist_dialog)
        playlisting_menu.addAction(smart_playlist_action)


    def init_connections(self):
        self.play_button.clicked.connect(self.play)
        self.pause_button.clicked.connect(self.pause)
        self.stop_button.clicked.connect(self.stop)
        self.previous_button.clicked.connect(self.play_previous)
        self.next_button.clicked.connect(self.play_next)
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.playlist_view.doubleClicked.connect(self.play_selected_song)

    def play(self):
        if self.current_song_index != -1 and self.current_song_index < len(self.playlist):
            current_song_path = self.playlist[self.current_song_index]
            try:
                pygame.mixer.music.load(current_song_path)
                pygame.mixer.music.play()
                self.update_song_label()
                sound = pygame.mixer.Sound(current_song_path)
                track_length = sound.get_length()


                self.timer.start(1000)
                self.update_duration(track_length)
            except Exception as e:
                print(f"Error playing song: {e}")
        else:
            print("No song selected to play.")

    def pause(self):
        pygame.mixer.music.pause()

    def stop(self):
        pygame.mixer.music.stop()

    def set_volume(self, volume):
        pygame.mixer.music.set_volume(volume / 100)

    def update_duration(self, duration):
        duration_seconds = duration // 1000
        duration_minutes = duration_seconds // 60
        duration_seconds_remaining = duration_seconds % 60
        self.total_time_label.setText(f"{duration_minutes:02d}:{duration_seconds_remaining:02d}")

    def update_position(self, position):
        position_time = QTime(0, (position / 60000) % 60, (position / 1000) % 60)


    def create_playlist_dialog(self):
        self.playlist_creator_dialog = PlaylistCreator()
        self.playlist_creator_dialog.populate_song_list(self.playlist)
        self.playlist_creator_dialog.exec_()

    def filter_music_library(self, criteria):
        filtered_tracks = []
        for track in self.playlist:
            if self.check_criteria(track, criteria):
                filtered_tracks.append(track)
        return filtered_tracks

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

    def create_smart_playlist_dialog(self):
        smart_playlist_creator = SmartPlaylistCreator()
        smart_playlist_creator.exec_()


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
                    song_path = os.path.join(root, file)
                    self.playlist.append(song_path)
                    self.playlist_view.addItem(song_path)
                    self.update_library_metadata(song_path)

    def update_library_metadata(self, song_path):
        try:
            audio = mutagen.File(song_path)
            artist = audio.get("artist", ["Unknown Artist"])[0]
            title = audio.get("title", ["Unknown Title"])[0]
            genre = audio.get("genre", ["Unknown Genre"])[0]
        except Exception as e:
            print(f"Error reading metadata: {e}")

    def update_song_label(self):
        if pygame.mixer.music.get_busy():
            current_song_path = self.playlist[self.current_song_index]
            try:
                audio = EasyID3(current_song_path)
                if audio is not None:
                    song_name = audio.get("title", ["Unknown Title"])[0]
                    artist_name = audio.get("artist", ["Unknown Artist"])[0]
                    print(artist_name, song_name)
                    self.current_song_label.setText(f"Now Playing: {song_name} - {artist_name}")
                else:
                    self.current_song_label.setText(f"Now Playing: {os.path.basename(current_song_path)}")
            except Exception as e:
                print(f"Error reading metadata: {e}")
                self.current_song_label.setText(f"Now Playing: {os.path.basename(current_song_path)}")

    def play_previous(self):
        if self.current_song_index > 0:
            self.current_song_index -= 1
            self.play()
            self.update_song_label()

    def play_next(self):
        if self.current_song_index < len(self.playlist) - 1:
            self.current_song_index += 1
            self.play()
            self.update_song_label()

    def load_playlist(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("Playlist Files (*.json)")
        if file_dialog.exec_():
            selected_file = file_dialog.selectedFiles()[0]
            with open(selected_file, 'r', encoding='utf-8') as file:
                playlist_data = json.load(file)
                self.playlist = playlist_data['songs']
                self.populate_playlist_view()


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
            if hasattr(self, 'search_results') and self.search_results:
                # Use the original index from the search results
                self.current_song_index = self.search_indices[index]
            else:
                # Use the index directly from the full playlist
                self.current_song_index = index
            self.play()

    def search_library(self):
        query = self.search_box.text().lower()
        self.search_results = []
        self.search_indices = []

        if query:
            for index, song_path in enumerate(self.playlist):
                try:
                    audio = EasyID3(song_path)
                    title = audio.get("title", ["Unknown Title"])[0].lower()
                    artist = audio.get("artist", ["Unknown Artist"])[0].lower()
                    album = audio.get("album", ["Unknown Album"])[0].lower()
                    genre = audio.get("genre", ["Unknown Genre"])[0].lower()
                    year = audio.get("date", ["Unknown Year"])[0].lower()
                    if query in title or query in artist or query in album or query in genre or query in year:
                        self.search_results.append(song_path)
                        self.search_indices.append(index)
                except Exception as e:
                    print(f"Error reading metadata: {e}")


            self.playlist_view.clear()


            for song_path in self.search_results:
                self.playlist_view.addItem(song_path)
        else:
            self.display_full_library()

    def display_full_library(self):
        if hasattr(self, 'search_results'):
            self.search_results.clear()
            self.search_indices.clear()

        self.playlist_view.clear()

        for song_path in self.playlist:
            self.playlist_view.addItem(song_path)


def main():
    app = QApplication(sys.argv)
    winamp = WinampClone()
    winamp.setStyleSheet(open("style.qss").read())
    winamp.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()


