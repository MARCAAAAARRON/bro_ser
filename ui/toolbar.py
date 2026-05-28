import os
from PyQt6.QtWidgets import QToolBar, QPushButton, QLineEdit
from PyQt6.QtGui import QIcon, QMovie
from PyQt6.QtCore import QSize, pyqtSignal

class BroSerToolBar(QToolBar):
    navigate_requested = pyqtSignal(str)
    back_requested = pyqtSignal()
    forward_requested = pyqtSignal()
    reload_requested = pyqtSignal()
    home_requested = pyqtSignal()
    bookmark_requested = pyqtSignal()
    show_history_requested = pyqtSignal()
    show_bookmarks_requested = pyqtSignal()
    show_downloads_requested = pyqtSignal()
    show_settings_requested = pyqtSignal()
    show_devtools_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(False)
        
        # Get path for assets folder
        current_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(os.path.dirname(current_dir), 'assets')
        
        # Back Button
        self.back_btn = QPushButton()
        self.back_btn.setIcon(QIcon(os.path.join(assets_dir, "icons8-left-48.ico")))
        self.back_btn.clicked.connect(self.back_requested.emit)
        self.back_btn.setIconSize(QSize(20, 20))
        self.addWidget(self.back_btn)

        # Forward Button
        self.forward_btn = QPushButton()
        self.forward_btn.setIcon(QIcon(os.path.join(assets_dir, "icons8-right-48.ico")))
        self.forward_btn.clicked.connect(self.forward_requested.emit)
        self.forward_btn.setIconSize(QSize(20, 20))
        self.addWidget(self.forward_btn)

        # Reload Button
        self.reload_btn = QPushButton()
        self.reload_btn.setIcon(QIcon(os.path.join(assets_dir, "icons8-rotate-48.ico")))
        self.reload_btn.clicked.connect(self.reload_requested.emit)
        self.reload_btn.setIconSize(QSize(20, 20))
        self.addWidget(self.reload_btn)

        # Home Button
        self.home_btn = QPushButton()
        self.home_btn.setIcon(QIcon(os.path.join(assets_dir, "icons8-homepage-48.ico")))
        self.home_btn.clicked.connect(self.home_requested.emit)
        self.home_btn.setIconSize(QSize(20, 20))
        self.addWidget(self.home_btn)

        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.setObjectName("urlBar")
        self.url_bar.returnPressed.connect(self.on_return_pressed)
        self.addWidget(self.url_bar)

        # Bookmark Button
        self.bookmark_btn = QPushButton()
        self.bookmark_btn.setIcon(QIcon(os.path.join(assets_dir, "icons8-star-50.ico")))
        self.bookmark_btn.setObjectName("bookmarkBtn")
        self.bookmark_btn.clicked.connect(self.bookmark_requested.emit)
        self.addWidget(self.bookmark_btn)

        # History Button
        self.history_btn = QPushButton()
        self.history_btn.setIcon(QIcon(os.path.join(assets_dir, "icons8-clock-48.ico")))
        self.history_btn.setObjectName("historyBtn")
        self.history_btn.clicked.connect(self.show_history_requested.emit)
        self.addWidget(self.history_btn)

        # Bookmarks List Button
        self.bookmarks_btn = QPushButton()
        self.bookmarks_btn.setIcon(QIcon(os.path.join(assets_dir, "icons8-bookmark-48.ico")))
        self.bookmarks_btn.setObjectName("bookmarksBtn")
        self.bookmarks_btn.clicked.connect(self.show_bookmarks_requested.emit)
        self.addWidget(self.bookmarks_btn)

        # Downloads Button
        self.downloads_btn = QPushButton()
        self.downloads_btn.setObjectName("downloadsBtn")
        self.downloads_btn.setIcon(QIcon(os.path.join(assets_dir, "icons8-download.gif")))
        self.downloads_btn.setIconSize(QSize(20, 20))
        self.downloads_btn.clicked.connect(self.show_downloads_requested.emit)
        self.addWidget(self.downloads_btn)

        # Setup QMovie for download animation
        self.download_movie = QMovie(os.path.join(assets_dir, "icons8-download.gif"))
        self.download_movie.frameChanged.connect(self.update_download_icon)

        # Settings Button
        self.settings_btn = QPushButton()
        self.settings_btn.setIcon(QIcon(os.path.join(assets_dir, "icons8-setting-48.ico")))
        self.settings_btn.setObjectName("settingsBtn")
        self.settings_btn.clicked.connect(self.show_settings_requested.emit)
        self.addWidget(self.settings_btn)

        # DevTools Button
        self.devtools_btn = QPushButton()
        self.devtools_btn.setIcon(QIcon(os.path.join(assets_dir, "icons8-tools-48.ico")))
        self.devtools_btn.setObjectName("devtoolsBtn")
        self.devtools_btn.clicked.connect(self.show_devtools_requested.emit)
        self.addWidget(self.devtools_btn)

    def on_return_pressed(self):
        url = self.url_bar.text()
        if not url.startswith("http"):
            url = "https://" + url
        self.navigate_requested.emit(url)

    def update_url(self, url: str):
        self.url_bar.setText(url)

    def start_download_animation(self):
        if self.download_movie:
            self.download_movie.start()

    def stop_download_animation(self):
        if self.download_movie:
            self.download_movie.stop()
            # Reset to static first frame
            assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
            self.downloads_btn.setIcon(QIcon(os.path.join(assets_dir, "icons8-download.gif")))

    def update_download_icon(self, frame_number):
        if self.download_movie:
            pixmap = self.download_movie.currentPixmap()
            self.downloads_btn.setIcon(QIcon(pixmap))
