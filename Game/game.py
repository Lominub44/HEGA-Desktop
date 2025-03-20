import sys
from PyQt5.QtCore import QUrl, QTimer, Qt
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QToolBar, QAction, QMessageBox, QLabel
from PyQt5.QtWebEngineWidgets import QWebEngineView

class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hidden Empire – Main Menu")
        self.setWindowIcon(QIcon("assets/favicon.ico"))
        self.resize(800, 600)

        background = QLabel(self)
        pixmap = QPixmap("assets/star_wars_background.png")
        scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        background.setPixmap(scaled_pixmap)
        background.setGeometry(0, 0, self.width(), self.height())
        background.setStyleSheet("border: none;")
        background.lower()

        layout = QVBoxLayout()
        layout.addStretch(1)

        self.login_button = QPushButton("Log in")
        self.login_button.setFont(QFont("Helvetica", 24))
        self.login_button.setFixedSize(300, 60)
        self.login_button.clicked.connect(self.open_login)
        layout.addWidget(self.login_button, alignment=Qt.AlignCenter)

        layout.addSpacing(30)

        self.register_button = QPushButton("Register")
        self.register_button.setFont(QFont("Helvetica", 24))
        self.register_button.setFixedSize(300, 60)
        self.register_button.clicked.connect(self.open_register)
        layout.addWidget(self.register_button, alignment=Qt.AlignCenter)

        layout.addStretch(1)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
    
    def open_login(self):
        self.load_game("https://www.hiddenempire.de/en/")
    
    def open_register(self):
        self.load_game("https://www.hiddenempire.de/en/playnow/register/")
    
    def load_game(self, url):
        self.browser = GameBrowser(url)
        self.browser.show()
        self.close()

class GameBrowser(QMainWindow):
    def __init__(self, url):
        super().__init__()
        self.setWindowTitle("Hidden Empire – Galaxy Adventures")
        self.setWindowIcon(QIcon("assets/favicon.ico"))
        self.resize(800, 600)
        
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(url))
        self.setCentralWidget(self.browser)
        
        self.showMaximized()
        
        self.navbar = QToolBar()
        self.addToolBar(self.navbar)
        
        self.reload_action = QAction('Reload', self)
        self.reload_action.triggered.connect(self.browser.reload)
        self.navbar.addAction(self.reload_action)
        
        self.exit_action = QAction('Exit', self)
        self.exit_action.triggered.connect(self.on_exit)
        self.navbar.addAction(self.exit_action)
        
        self.browser.urlChanged.connect(self.on_url_changed)
    
    def on_url_changed(self, url):
        self.current_domain = url.host()
    
    def on_exit(self):
        if hasattr(self, 'current_domain') and self.current_domain == "jedha.hiddenempire.de":
            reply = QMessageBox.question(self, 'Exit Confirmation',
                                         'Are you sure you want to exit while on jedha.hiddenempire.de? You will be logged out.',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.browser.page().runJavaScript("""
                    var logoutButton = document.getElementById('gamelogout');
                    if (logoutButton) {
                        logoutButton.click();
                    }
                """)
                QTimer.singleShot(1000, self.close)
        else:
            self.close()

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("assets/favicon.ico"))
    menu = MainMenu()
    menu.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
