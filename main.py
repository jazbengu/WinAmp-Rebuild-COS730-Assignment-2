import sys
import os
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, \
    QPushButton, QListWidget, QTextEdit, QFileDialog, QSlider, QMenuBar, QAction
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from mutagen.easyid3 import EasyID3
from smart_playlisting import generate_playlist, save_playlist
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

        layout = QVBoxLayout()
        layout.addWidget(self.playlist_view)
        layout.addWidget(self.current_song_label)
        layout.addLayout(control_layout)
        layout.addWidget(self.volume_slider)
        layout.addWidget(self.lyrics_display)

        central_widget.setLayout(layout)

        self.create_menu()

        self.init_connections()

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

        load_playlist_action = QAction("Load Playlist", self)
        load_playlist_action.triggered.connect(self.load_playlist)
        playlisting_menu.addAction(load_playlist_action)

        save_playlist_action = QAction("Save Playlist", self)
        save_playlist_action.triggered.connect(self.save_playlist)
        playlisting_menu.addAction(save_playlist_action)



    def init_connections(self):
        self.media_player.stateChanged.connect(self.update_song_label)
        self.media_player.positionChanged.connect(self.update_lyrics)
        self.play_button.clicked.connect(self.media_player.play)
        self.pause_button.clicked.connect(self.media_player.pause)
        self.stop_button.clicked.connect(self.media_player.stop)
        self.previous_button.clicked.connect(self.play_previous)
        self.next_button.clicked.connect(self.play_next)
        self.volume_slider.valueChanged.connect(self.media_player.setVolume)
        self.playlist_view.doubleClicked.connect(self.play_selected_song)

    def add_music_dialog(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.DirectoryOnly)
        file_dialog.setOption(QFileDialog.ShowDirsOnly, True)
        if file_dialog.exec_():
            directories = file_dialog.selectedFiles()
            for directory in directories:
                self.add_music_from_directory(directory)

    def add_music_from_directory(self, directory):
        music_extensions = ('.mp3', '.wav')
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(music_extensions):
                    self.playlist_view.addItem(os.path.join(root, file))

    def update_song_label(self, state):
        if state == QMediaPlayer.PlayingState:
            current_song_path = self.media_player.currentMedia().canonicalUrl().toLocalFile()
            try:
                audio = EasyID3(current_song_path)
                song_name = audio.get("title", ["Unknown Title"])[0]
                artist_name = audio.get("artist", ["Unknown Artist"])[0]
                self.current_song_label.setText(f"Now Playing: {song_name} - {artist_name}")
            except Exception as e:
                print(f"Error reading metadata: {e}")
                self.current_song_label.setText(f"Now Playing: {os.path.basename(current_song_path)}")
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
                artist_name = audio.get("artist", ["Unknown"])[0]
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
