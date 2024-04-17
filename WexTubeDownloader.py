import os
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QLabel, QMessageBox, QFileDialog
from PyQt6.QtGui import QColor, QLinearGradient, QIcon, QPixmap
from PyQt6.QtCore import Qt, QSettings, QTimer

from pytube import YouTube

class YouTubeDownloader(QWidget):
    def __init__(self):
        super().__init__()

        # Create directories for error logs and saved paths
        if not os.path.exists("errors"):
            os.makedirs("errors")
        if not os.path.exists("saves"):
            os.makedirs("saves")

        # Set up the main window
        self.setWindowTitle("YouTube Video Downloader")
        self.setGeometry(100, 100, 600, 400)
        self.setWindowIcon(QIcon('mini-logo.png'))

        # Set background gradient color
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(60, 60, 60))  # Siyaha yakın gri
        gradient.setColorAt(0.5, QColor(30, 30, 30))  # Siyah
        gradient.setColorAt(1, QColor(60, 60, 60))  # Siyaha yakın gri
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setBrush(self.backgroundRole(), gradient)
        self.setPalette(p)

        # Logo
        self.logo_label = QLabel(self)
        self.logo_label.setGeometry(0, 0, 600, 150)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pixmap = QPixmap("logo.png")
        self.logo_label.setPixmap(pixmap.scaledToWidth(250))

        # Input box for YouTube link
        self.link_input = QLineEdit(self)
        self.link_input.setGeometry(50, 150, 400, 30)
        self.link_input.setStyleSheet("background-color: rgba(255, 255, 255, 0.5); border-radius: 5px;")
        self.link_input.setPlaceholderText("Enter YouTube link to download video")

        # Download buttons
        self.download_button = QPushButton("Download", self)
        self.download_button.setGeometry(470, 150, 100, 30)
        self.download_button.setStyleSheet("background-color: rgb(100, 150, 255); border: 2px solid rgb(50, 100, 200); border-radius: 5px;")
        self.download_button.clicked.connect(self.download_video)

        self.download_mp3_button = QPushButton("Download MP3", self)
        self.download_mp3_button.setGeometry(470, 200, 100, 30)
        self.download_mp3_button.setStyleSheet("background-color: rgb(100, 150, 255); border: 2px solid rgb(50, 100, 200); border-radius: 5px;")
        self.download_mp3_button.clicked.connect(self.download_video_as_mp3)

        # Select save path button
        self.select_path_button = QPushButton("Select Save Path", self)
        self.select_path_button.setGeometry(50, 350, 150, 30)
        self.select_path_button.setStyleSheet("background-color: rgb(100, 150, 255); border: 2px solid rgb(50, 100, 200); border-radius: 5px;")
        self.select_path_button.clicked.connect(self.select_save_path)

        # Display current save path
        self.save_path_label = QLabel("Save Path: ", self)
        self.save_path_label.setGeometry(50, 300, 500, 30)
        self.save_path_label.setStyleSheet("background-color: rgba(255, 255, 255, 0.5); border-radius: 5px;")

        # Load save path from settings
        self.settings = QSettings("YouTubeDownloader", "Settings")
        saved_path = self.settings.value("save_path")
        if saved_path:
            self.save_path_label.setText("Save Path: " + saved_path)

        # Error/status label
        self.status_label = QLabel("", self)
        self.status_label.setGeometry(10, 380, 300, 20)
        self.status_label.setStyleSheet("color: red; font-size: 10pt;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

    def download_video(self):
        link = self.link_input.text()
        save_path_text = self.save_path_label.text()
        if ":" in save_path_text:
            SAVE_PATH = save_path_text.split(": ")[1]
        else:
            QMessageBox.warning(self, "Warning", "Please select a save path.")
            self.select_save_path()
            return

        try:
            yt = YouTube(link)
            video_stream = yt.streams.filter(file_extension='mp4', progressive=True).first()

            video_stream.download(output_path=SAVE_PATH)
            self.save_path_label.setText("Save Path: " + SAVE_PATH)

            # Save path in settings
            self.settings.setValue("save_path", SAVE_PATH)
            self.show_status_message("Video downloaded successfully.")
        except Exception as e:
            error_log = open("errors/error_log.txt", "a")
            error_log.write(str(e) + "\n")
            error_log.close()
            self.show_status_message("Error downloading video")

    def download_video_as_mp3(self):
        link = self.link_input.text()
        save_path_text = self.save_path_label.text()
        if ":" in save_path_text:
            SAVE_PATH = save_path_text.split(": ")[1]
        else:
            QMessageBox.warning(self, "Warning", "Please select a save path.")
            self.select_save_path()
            return

        try:
            yt = YouTube(link)
            audio_stream = yt.streams.filter(only_audio=True).first()

            audio_stream.download(output_path=SAVE_PATH, filename_prefix='audio_')
            self.save_path_label.setText("Save Path: " + SAVE_PATH)

            # Save path in settings
            self.settings.setValue("save_path", SAVE_PATH)
            self.show_status_message("Audio downloaded successfully.")
        except Exception as e:
            error_log = open("errors/error_log.txt", "a")
            error_log.write(str(e) + "\n")
            error_log.close()
            self.show_status_message("Error downloading audio")

    def select_save_path(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Save Path")
        if folder_path:
            self.save_path_label.setText("Save Path: " + folder_path)
            self.settings.setValue("save_path", folder_path)
            with open("saves/save_paths.txt", "a", encoding="utf-8") as save_path_file:
                save_path_file.write(folder_path + "\n")
        else:
            QMessageBox.critical(self, "Error", "No save path selected.")

    def show_status_message(self, message):
        self.status_label.setText(message)
        self.status_label.adjustSize()
        self.status_label.show()
        QTimer.singleShot(3000, self.hide_status_message)

    def hide_status_message(self):
        self.status_label.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YouTubeDownloader()
    window.show()
    sys.exit(app.exec())
