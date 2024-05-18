from PyQt5.QtWidgets import QDialog, QVBoxLayout, QCheckBox, QLineEdit, QPushButton, QLabel, QFileDialog


class SmartPlaylistDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Create Smart Playlist")
        self.setGeometry(100, 100, 300, 200)

        self.layout = QVBoxLayout()

        self.playlist_name_label = QLabel("Playlist Name:")
        self.playlist_name_edit = QLineEdit()

        self.tempo_checkbox = QCheckBox("Tempo")
        self.mood_checkbox = QCheckBox("Mood")
        self.artist_checkbox = QCheckBox("Artist")
        self.genre_checkbox = QCheckBox("Genre")

        self.create_button = QPushButton("Create")
        self.create_button.clicked.connect(self.create_playlist)

        self.layout.addWidget(self.playlist_name_label)
        self.layout.addWidget(self.playlist_name_edit)
        self.layout.addWidget(self.tempo_checkbox)
        self.layout.addWidget(self.mood_checkbox)
        self.layout.addWidget(self.artist_checkbox)
        self.layout.addWidget(self.genre_checkbox)
        self.layout.addWidget(self.create_button)

        self.setLayout(self.layout)

    def create_playlist(self):
        self.accept()
