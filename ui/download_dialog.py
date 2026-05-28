import os
import subprocess
import platform

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QProgressBar, QWidget
)
from PyQt6.QtCore import Qt


class DownloadItemWidget(QWidget):
    """Custom widget for a single download entry in the list."""
    def __init__(self, download_item, parent=None):
        super().__init__(parent)
        self.download_item = download_item
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        self.setMinimumHeight(95)
        
        # Top row: filename + status
        top_row = QHBoxLayout()
        self.filename_label = QLabel(download_item.filename)
        self.filename_label.setObjectName("downloadFilename")
        top_row.addWidget(self.filename_label)
        top_row.addStretch()
        
        self.status_label = QLabel(download_item.status.capitalize())
        self.status_label.setObjectName("downloadStatus")
        top_row.addWidget(self.status_label)
        layout.addLayout(top_row)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)
        
        # Bottom row: size info + buttons
        bottom_row = QHBoxLayout()
        self.size_label = QLabel("")
        self.size_label.setObjectName("downloadSize")
        bottom_row.addWidget(self.size_label)
        bottom_row.addStretch()
        
        self.open_btn = QPushButton("Open File")
        self.open_btn.setVisible(False)
        self.open_btn.clicked.connect(self._open_file)
        bottom_row.addWidget(self.open_btn)
        
        self.folder_btn = QPushButton("Open Folder")
        self.folder_btn.setVisible(False)
        self.folder_btn.clicked.connect(self._open_folder)
        bottom_row.addWidget(self.folder_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self._cancel_download)
        bottom_row.addWidget(self.cancel_btn)
        
        layout.addLayout(bottom_row)
        
        self.update_progress()

    def update_progress(self):
        item = self.download_item
        if item.total_bytes > 0:
            percent = int((item.received_bytes / item.total_bytes) * 100)
            self.progress_bar.setValue(percent)
            self.size_label.setText(
                f"{self._format_size(item.received_bytes)} / {self._format_size(item.total_bytes)}"
            )
        elif item.received_bytes > 0:
            self.progress_bar.setMaximum(0)  # Indeterminate
            self.size_label.setText(f"{self._format_size(item.received_bytes)}")
        
        self.status_label.setText(item.status.capitalize())
        
        if item.status in ("completed", "failed", "cancelled"):
            if item.status == "completed":
                self.progress_bar.setValue(100)
                self.open_btn.setVisible(True)
                self.folder_btn.setVisible(True)
            else:
                self.progress_bar.setVisible(False)
            self.cancel_btn.setVisible(False)
        else:
            self.progress_bar.setVisible(True)
            self.open_btn.setVisible(False)
            self.folder_btn.setVisible(False)
            self.cancel_btn.setVisible(True)

    @staticmethod
    def _format_size(size_bytes):
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

    def _open_file(self):
        filepath = self.download_item.filepath
        if os.path.exists(filepath):
            os.startfile(filepath)

    def _open_folder(self):
        filepath = self.download_item.filepath
        folder = os.path.dirname(filepath)
        if os.path.exists(folder):
            if platform.system() == "Windows":
                subprocess.Popen(f'explorer /select,"{filepath}"')
            else:
                os.startfile(folder)

    def _cancel_download(self):
        try:
            self.download_item.download.cancel()
        except Exception as e:
            print(f"Error cancelling download: {e}")


class DownloadDialog(QDialog):
    def __init__(self, download_manager, parent=None):
        super().__init__(parent)
        self.download_manager = download_manager
        self.item_widgets = {}  # map DownloadItem -> DownloadItemWidget
        
        self.setWindowTitle("Downloads")
        self.setMinimumSize(550, 450)
        self._setup_ui()
        self._load_active_downloads()
        
        # Connect live signals
        self.download_manager.download_added.connect(self._on_download_added)
        self.download_manager.download_updated.connect(self._on_download_updated)
        self.download_manager.download_finished.connect(self._on_download_finished)

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        header = QHBoxLayout()
        header.addWidget(QLabel("Download Manager"))
        header.addStretch()

        self.clear_btn = QPushButton("Clear Completed")
        self.clear_btn.clicked.connect(self._clear_completed)
        header.addWidget(self.clear_btn)

        layout.addLayout(header)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

    def _load_active_downloads(self):
        for item in self.download_manager.active_downloads:
            self._add_item_widget(item)

    def _add_item_widget(self, download_item):
        widget = DownloadItemWidget(download_item)
        list_item = QListWidgetItem()
        list_item.setSizeHint(widget.sizeHint())
        self.list_widget.insertItem(0, list_item)
        self.list_widget.setItemWidget(list_item, widget)
        self.item_widgets[id(download_item)] = (list_item, widget)

    def _on_download_added(self, download_item):
        self._add_item_widget(download_item)

    def _on_download_updated(self, download_item):
        key = id(download_item)
        if key in self.item_widgets:
            _, widget = self.item_widgets[key]
            widget.update_progress()

    def _on_download_finished(self, download_item):
        key = id(download_item)
        if key in self.item_widgets:
            _, widget = self.item_widgets[key]
            widget.update_progress()

    def _clear_completed(self):
        to_remove = []
        for key, (list_item, widget) in self.item_widgets.items():
            if widget.download_item.status != "downloading":
                row = self.list_widget.row(list_item)
                self.list_widget.takeItem(row)
                to_remove.append(key)
        for key in to_remove:
            del self.item_widgets[key]
        self.download_manager.clear_completed()
