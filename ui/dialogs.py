from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel
)
from PyQt6.QtCore import pyqtSignal


class HistoryDialog(QDialog):
    navigate_to = pyqtSignal(str)

    def __init__(self, history_manager, parent=None):
        super().__init__(parent)
        self.history_manager = history_manager
        self.setWindowTitle("Browsing History")
        self.setMinimumSize(500, 400)
        self._setup_ui()
        self._load_items()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        header = QHBoxLayout()
        header.addWidget(QLabel("Recent History"))
        header.addStretch()

        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.clicked.connect(self._clear_history)
        header.addWidget(self.clear_btn)

        layout.addLayout(header)

        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self._on_item_clicked)
        layout.addWidget(self.list_widget)

    def _load_items(self):
        self.list_widget.clear()
        visits = self.history_manager.get_recent_visits()
        for url, title, timestamp in visits:
            display = f"{title or 'Untitled'}\n{url}"
            item = QListWidgetItem(display)
            item.setData(256, url)  # Qt.ItemDataRole.UserRole = 256
            self.list_widget.addItem(item)

    def _on_item_clicked(self, item):
        url = item.data(256)
        if url:
            self.navigate_to.emit(url)
            self.accept()

    def _clear_history(self):
        self.history_manager.clear_history()
        self.list_widget.clear()


class BookmarksDialog(QDialog):
    navigate_to = pyqtSignal(str)

    def __init__(self, bookmark_manager, parent=None):
        super().__init__(parent)
        self.bookmark_manager = bookmark_manager
        self.setWindowTitle("Bookmarks")
        self.setMinimumSize(500, 400)
        self._setup_ui()
        self._load_items()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        header = QHBoxLayout()
        header.addWidget(QLabel("Saved Bookmarks"))
        header.addStretch()

        self.remove_btn = QPushButton("Remove Selected")
        self.remove_btn.clicked.connect(self._remove_selected)
        header.addWidget(self.remove_btn)

        layout.addLayout(header)

        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self._on_item_clicked)
        layout.addWidget(self.list_widget)

    def _load_items(self):
        self.list_widget.clear()
        bookmarks = self.bookmark_manager.get_bookmarks()
        for url, title, timestamp in bookmarks:
            display = f"{title or 'Untitled'}\n{url}"
            item = QListWidgetItem(display)
            item.setData(256, url)  # Qt.ItemDataRole.UserRole = 256
            self.list_widget.addItem(item)

    def _on_item_clicked(self, item):
        url = item.data(256)
        if url:
            self.navigate_to.emit(url)
            self.accept()

    def _remove_selected(self):
        current = self.list_widget.currentItem()
        if current:
            url = current.data(256)
            self.bookmark_manager.remove_bookmark(url)
            self._load_items()
