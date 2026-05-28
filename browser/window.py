import os
import json
import logging
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtWebEngineCore import QWebEngineProfile
from PyQt6.QtGui import QKeySequence, QShortcut, QIcon
from PyQt6.QtCore import QTimer

from ui.toolbar import BroSerToolBar
from ui.dialogs import HistoryDialog, BookmarksDialog
from ui.download_dialog import DownloadDialog
from ui.settings_dialog import SettingsDialog
from ui.devtools import DevToolsWindow
from browser.tabs import BroSerTabWidget
from browser.history import BookmarkManager
from browser.downloads import DownloadManager
from browser.config import ConfigManager
from browser.adblocker import AdBlockInterceptor

logger = logging.getLogger("BroSer.MainWindow")

class BroSerWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Bro-ser")
        # Resolve window icon absolutely to prevent loading failures when packaged under PyInstaller
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(root_dir, 'assets', 'bro_ser.ico')
        self.setWindowIcon(QIcon(icon_path))
        
        # Config Manager
        self.config = ConfigManager()

        # Limit cache sizes on the default profile to prevent runway disk growth (100MB max)
        default_profile = QWebEngineProfile.defaultProfile()
        default_profile.setHttpCacheMaximumSize(100 * 1024 * 1024)
        logger.info("Default WebEngineProfile cache limit set to 100MB.")

        # Ad Blocker Interceptor (setup on default profile immediately)
        self.adblocker = AdBlockInterceptor(self.config, self)
        default_profile.setUrlRequestInterceptor(self.adblocker)

        # Bookmark & Download Managers
        self.bookmark_manager = BookmarkManager()
        self.download_manager = DownloadManager(self)

        # Setup Tab Widget (passing adblocker for private profiles)
        self.tabs = BroSerTabWidget(self.adblocker, self)
        self.setCentralWidget(self.tabs)
        
        # Setup Toolbar (injected into tabs layout, not QMainWindow toolbar area)
        self.toolbar = BroSerToolBar(self)
        self.tabs.set_toolbar(self.toolbar)

        # Session path
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.session_path = os.path.join(root_dir, 'config', 'session.json')

        # Setup debounced session auto-save timer (1000ms delay to throttle disk I/O)
        self.session_save_timer = QTimer(self)
        self.session_save_timer.setSingleShot(True)
        self.session_save_timer.setInterval(1000)
        self.session_save_timer.timeout.connect(self._write_session_to_disk)

        # Connect signals from toolbar to tabs
        self.toolbar.navigate_requested.connect(self.tabs.navigate)
        self.toolbar.back_requested.connect(self.tabs.back)
        self.toolbar.forward_requested.connect(self.tabs.forward)
        self.toolbar.reload_requested.connect(self.tabs.reload)
        self.toolbar.home_requested.connect(self.go_home)

        # Connect bookmark/history/downloads/settings/devtools signals
        self.toolbar.bookmark_requested.connect(self.add_bookmark)
        self.toolbar.show_history_requested.connect(self.show_history)
        self.toolbar.show_bookmarks_requested.connect(self.show_bookmarks)
        self.toolbar.show_downloads_requested.connect(self.show_downloads)
        self.toolbar.show_settings_requested.connect(self.show_settings)
        self.toolbar.show_devtools_requested.connect(self.show_devtools)

        # F12 Hotkey for DevTools
        self.devtools_shortcut = QShortcut(QKeySequence("F12"), self)
        self.devtools_shortcut.activated.connect(self.show_devtools)

        # Connect QWebEngineProfile download request to manager
        default_profile.downloadRequested.connect(
            self.download_manager.handle_download
        )

        # Connect download manager signals to toolbar for animated state indicators
        self.download_manager.download_added.connect(self._on_download_started)
        self.download_manager.download_finished.connect(self._on_download_finished)

        # Connect signals from tabs to toolbar/window
        self.tabs.active_url_changed.connect(self.toolbar.update_url)
        self.tabs.active_title_changed.connect(self.update_title)
        
        # Debounce session save in real-time on tab rearrangements, closures, navigations
        self.tabs.tab_state_changed.connect(self.save_session)

        # Open restored session or default homepage
        restored = self.restore_session()
        if not restored:
            homepage = self.config.get("homepage")
            is_private = self.config.get("private_mode_by_default")
            self.tabs.add_new_tab(homepage, is_private=is_private)

    def update_title(self, title):
        self.setWindowTitle(f"{title} - Bro-ser")

    def go_home(self):
        self.tabs.navigate(self.config.get("homepage"))

    def add_bookmark(self):
        browser = self.tabs.current_browser()
        if browser:
            url = browser.url().toString()
            title = browser.title() or ""
            added = self.bookmark_manager.add_bookmark(url, title)
            if added:
                self.toolbar.bookmark_btn.setText("⭐")
            else:
                # Already bookmarked, remove it (toggle behavior)
                self.bookmark_manager.remove_bookmark(url)
                self.toolbar.bookmark_btn.setText("☆")
        self.save_session()

    def show_history(self):
        dialog = HistoryDialog(self.tabs.history_manager, self)
        dialog.navigate_to.connect(self.tabs.navigate)
        dialog.exec()

    def show_bookmarks(self):
        dialog = BookmarksDialog(self.bookmark_manager, self)
        dialog.navigate_to.connect(self.tabs.navigate)
        dialog.exec()

    def show_downloads(self):
        dialog = DownloadDialog(self.download_manager, self)
        dialog.exec()

    def show_settings(self):
        dialog = SettingsDialog(self.config, self.tabs.history_manager, self)
        dialog.exec()

    def show_devtools(self):
        browser = self.tabs.current_browser()
        if browser:
            self.devtools_win = DevToolsWindow(browser, self)
            self.devtools_win.show()

    def save_session(self):
        """Starts/restarts the debounce timer for session saving."""
        self.session_save_timer.start()

    def _write_session_to_disk(self):
        """Physical tab list serialize to session.json triggered after 1s of stillness."""
        session_data = []
        for i in range(self.tabs.count()):
            browser = self.tabs.widget(i)
            if browser:
                url = browser.url().toString()
                # Only save active browse states, skip empty setups
                if url and url != "about:blank":
                    session_data.append({
                        "url": url,
                        "is_private": getattr(browser, 'is_private', False)
                    })
        try:
            with open(self.session_path, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=4)
            logger.info("Session serialized and auto-saved to disk.")
        except Exception as e:
            logger.error(f"Failed to save session state to disk: {e}", exc_info=True)

    def restore_session(self):
        if os.path.exists(self.session_path):
            try:
                with open(self.session_path, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                if session_data:
                    for tab in session_data:
                        self.tabs.add_new_tab(tab["url"], is_private=tab["is_private"])
                    logger.info(f"Restored previous session containing {len(session_data)} tabs.")
                    return True
            except Exception as e:
                logger.error(f"Failed to restore previous session details: {e}", exc_info=True)
        return False

    def _on_download_started(self, item):
        self.toolbar.start_download_animation()

    def _on_download_finished(self, item):
        # Check if there are still any active downloading items
        active = any(d.status == "downloading" for d in self.download_manager.active_downloads)
        if not active:
            self.toolbar.stop_download_animation()