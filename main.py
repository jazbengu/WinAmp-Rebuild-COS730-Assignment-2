import sys
import os
import requests
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, \
    QPushButton, QListWidget, QTextEdit, QFileDialog, QSlider
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from bs4 import BeautifulSoup
from mutagen.easyid3 import EasyID3

from lyrics import fetch_lyrics


class WinampClone(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Winamp Clone")
        self.setGeometry(100, 100, 800, 600)

        self.media_player = QMediaPlayer()
        self.media_player.setVolume(50)

        self.playlist_view = QListWidget()
        self.current_song_label = QLabel()
        self.lyrics_display = QTextEdit()
        self.lyrics_display.setReadOnly(True)
        self.lyrics_display.setMinimumHeight(100)

        self.play_button = QPushButton("Play")
        self.pause_button = QPushButton("Pause")
        self.stop_button = QPushButton("Stop")
        self.previous_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")
        self.load_playlist_button = QPushButton("Load Playlist")
        self.save_playlist_button = QPushButton("Save Playlist")
        self.fetch_lyrics_button = QPushButton("Fetch Lyrics")
        self.recommend_button = QPushButton("Recommend")

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setValue(50)  # Example initial volume

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

        playlist_control_layout = QVBoxLayout()
        playlist_control_layout.addWidget(self.load_playlist_button)
        playlist_control_layout.addWidget(self.save_playlist_button)

        lyrics_control_layout = QVBoxLayout()
        lyrics_control_layout.addWidget(self.fetch_lyrics_button)
        lyrics_control_layout.addWidget(self.recommend_button)

        control_layout.addLayout(playlist_control_layout)
        control_layout.addLayout(lyrics_control_layout)

        layout = QVBoxLayout()
        layout.addWidget(self.playlist_view)
        layout.addWidget(self.current_song_label)
        layout.addLayout(control_layout)
        layout.addWidget(self.volume_slider)
        layout.addWidget(self.lyrics_display)

        central_widget.setLayout(layout)

        self.add_music_button = QPushButton("Add Music")
        self.add_music_button.setIcon(QIcon("+"))  # You can replace "add_music_icon.png" with your icon path

        # Add the button to the layout
        control_layout.addWidget(self.add_music_button)

        self.init_connections()
    def init_connections(self):
        self.media_player.stateChanged.connect(self.update_song_label)
        self.media_player.positionChanged.connect(self.update_lyrics)
        self.play_button.clicked.connect(self.media_player.play)
        self.pause_button.clicked.connect(self.media_player.pause)
        self.stop_button.clicked.connect(self.media_player.stop)
        self.previous_button.clicked.connect(self.play_previous)
        self.next_button.clicked.connect(self.play_next)
        self.load_playlist_button.clicked.connect(self.load_playlist)
        self.save_playlist_button.clicked.connect(self.save_playlist)
        self.fetch_lyrics_button.clicked.connect(self.fetch_lyrics)
        self.recommend_button.clicked.connect(self.recommend)
        self.volume_slider.valueChanged.connect(self.media_player.setVolume)
        self.playlist_view.doubleClicked.connect(self.play_selected_song)
        self.add_music_button.clicked.connect(self.add_music_dialog)

    def add_music_dialog(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("Music Files (*.mp3 *.wav)")
        if file_dialog.exec_():
            music_files = file_dialog.selectedFiles()
            for music_file in music_files:
                self.playlist_view.addItem(music_file)

    def update_song_label(self, state):
        if state == QMediaPlayer.PlayingState:
            self.current_song_label.setText(
                "Now Playing: " + os.path.basename(self.media_player.currentMedia().canonicalUrl().path()))
        else:
            self.current_song_label.setText("")

    def update_lyrics(self, position):
        # Update lyrics display here
        pass

    def play_previous(self):
        # Play previous song
        current_index = self.playlist_view.currentRow()
        if current_index > 0:
            self.playlist_view.setCurrentRow(current_index - 1)
            self.play_selected_song()

    def play_next(self):
        # Play next song
        current_index = self.playlist_view.currentRow()
        if current_index < self.playlist_view.count() - 1:
            self.playlist_view.setCurrentRow(current_index + 1)
            self.play_selected_song()

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
                            self.playlist_view.addItem(line.strip())

    def save_playlist(self):
        file_dialog = QFileDialog()
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setDefaultSuffix("m3u")
        file_dialog.setNameFilter("Playlist (*.m3u)")
        if file_dialog.exec_():
            save_path = file_dialog.selectedFiles()[0]
            with open(save_path, 'w') as file:
                for i in range(self.playlist_view.count()):
                    file.write(self.playlist_view.item(i).text() + '\n')

    def fetch_lyrics(self):
        # Fetch lyrics for current song
        index = self.playlist_view.currentRow()
        if index >= 0:
            song_path = self.playlist_view.currentItem().text()

            # Extract song name and artist from metadata
            try:
                audio = EasyID3(song_path)
                song_name = audio["title"][0]
                artist_name = audio["artist"][0]
            except Exception as e:
                print(f"Error reading metadata: {e}")
                song_name = os.path.splitext(os.path.basename(song_path))[0]
                artist_name = "Unknown"

            lyrics = fetch_lyrics(song_name, artist_name)
            self.lyrics_display.setPlainText(lyrics)

    def recommend(self):
        # Recommend songs
        pass

    def play_selected_song(self):
        index = self.playlist_view.currentRow()
        if index >= 0:
            song_path = self.playlist_view.currentItem().text()
            media = QMediaContent(QUrl.fromLocalFile(song_path))
            self.media_player.setMedia(media)
            self.media_player.play()


def main():
    app = QApplication(sys.argv)
    winamp = WinampClone()
    winamp.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
