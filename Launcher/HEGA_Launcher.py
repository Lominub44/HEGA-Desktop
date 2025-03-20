import sys
import os
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QMessageBox
from PyQt6.QtGui import QPixmap, QFont, QImage, QIcon
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PIL import Image

media_player = None
video_widget = None
audio_output = None

def start_game():
    if sys.platform == 'win32':
        os.system("game.exe")
    else:
        QMessageBox.critical(window, "Error", "Unsupported platform!")

def exit_launcher():
    QApplication.quit()

def play_credits():
    global media_player, video_widget, audio_output
    
    video_widget = QVideoWidget()
    video_widget.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
    video_widget.showFullScreen()
    
    media_player = QMediaPlayer()
    audio_output = QAudioOutput(media_player)
    audio_output.setVolume(1.0)
    media_player.setAudioOutput(audio_output)
    media_player.setVideoOutput(video_widget)
    
    media_player.setSource(QUrl.fromLocalFile(os.path.join(os.getcwd(), "credits.mp4")))
    media_player.play()
    
    exit_label = QLabel("Press ESC to exit", video_widget) # does not work at the moment, idk why.
    exit_label.setStyleSheet("color: white; font-size: 20px; background-color: rgba(0, 0, 0, 150); padding: 5px; border-radius: 5px;")
    exit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    exit_label.setGeometry(video_widget.width() - 200, 20, 180, 40)
    exit_label.show()
    
    def close_credits():
        media_player.stop()
        video_widget.close()
    
    def handle_media_status_changed(status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            close_credits()
    
    media_player.mediaStatusChanged.connect(handle_media_status_changed)
    
    def keyPressEvent(event):
        if event.key() == Qt.Key.Key_Escape:
            close_credits()
    
    video_widget.keyPressEvent = keyPressEvent

app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("HEGA Launcher")
window.setFixedSize(1280, 720)

try:
    background_image = Image.open(os.path.join(os.getcwd(), "assets/star_wars_background.png"))
    background_image = background_image.resize((1280, 720), Image.Resampling.LANCZOS).convert("RGB")
    qimage = QImage(background_image.tobytes(), background_image.width, background_image.height, background_image.width * 3, QImage.Format.Format_RGB888)
    background_photo = QPixmap.fromImage(qimage)
except Exception as e:
    QMessageBox.critical(window, "Error", f"Background image not found: {e}")
    sys.exit(1)

background_label = QLabel(window)
background_label.setPixmap(background_photo)
background_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
background_label.setGeometry(0, 0, 1280, 720)

try:
    logo_image = QPixmap(os.path.join(os.getcwd(), "assets/he_logo_0.png"))
    logo_image = logo_image.scaled(800, 400, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
except Exception as e:
    QMessageBox.critical(window, "Error", f"Logo image not found: {e}")
    sys.exit(1)

logo_label = QLabel(window)
logo_label.setPixmap(logo_image)
logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
logo_label.setGeometry(0, -40, 1280, 400)

app.setWindowIcon(QIcon(os.path.join(os.getcwd(), "assets/favicon.ico")))

layout = QVBoxLayout()

start_button = QPushButton("Start Game", window)
start_button.setFont(QFont("Helvetica", 24))
start_button.setFixedSize(300, 60)
start_button.clicked.connect(start_game)

credits_button = QPushButton("Credits", window)
credits_button.setFont(QFont("Helvetica", 24))
credits_button.setFixedSize(300, 60)
credits_button.clicked.connect(play_credits)

exit_button = QPushButton("Exit", window)
exit_button.setFont(QFont("Helvetica", 24))
exit_button.setFixedSize(300, 60)
exit_button.clicked.connect(exit_launcher)

button_layout = QVBoxLayout()
button_layout.addStretch(1)
button_layout.addWidget(start_button, alignment=Qt.AlignmentFlag.AlignCenter)
button_layout.addSpacing(30)
button_layout.addWidget(credits_button, alignment=Qt.AlignmentFlag.AlignCenter)
button_layout.addSpacing(30)
button_layout.addWidget(exit_button, alignment=Qt.AlignmentFlag.AlignCenter)

layout.addLayout(button_layout)
layout.setAlignment(Qt.AlignmentFlag.AlignBottom)
window.setLayout(layout)

window.show()
sys.exit(app.exec())
