import os
import sqlite3
import logging
from pathlib import Path
from datetime import datetime

from PyQt6.QtCore import QObject, pyqtSignal, QStandardPaths
from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest

logger = logging.getLogger("BroSer.Downloads")

class DownloadItem:
    """Represents a single download with its metadata and state."""
    def __init__(self, download: QWebEngineDownloadRequest):
        self.download = download
        self.filename = os.path.basename(download.downloadFileName())
        self.url = download.url().toString()
        self.filepath = download.downloadDirectory() + "/" + download.downloadFileName()
        self.total_bytes = download.totalBytes()
        self.received_bytes = 0
        self.status = "downloading"  # downloading, completed, failed, cancelled


class DownloadManager(QObject):
    download_added = pyqtSignal(object)       # emits DownloadItem
    download_updated = pyqtSignal(object)     # emits DownloadItem
    download_finished = pyqtSignal(object)    # emits DownloadItem

    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_downloads = []
        
        # Use system Downloads folder
        self.download_dir = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DownloadLocation
        )
        
        # Setup SQLite for download history
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        os.makedirs(data_dir, exist_ok=True)
        self.db_path = os.path.join(data_dir, 'downloads.db')
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
        except sqlite3.Error as e:
            logger.error(f"Failed to set PRAGMA on downloads DB: {e}")
        return conn

    def _init_db(self):
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS downloads (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        filename TEXT NOT NULL,
                        url TEXT,
                        filepath TEXT,
                        size_bytes INTEGER,
                        status TEXT,
                        timestamp TEXT NOT NULL
                    )
                ''')
            logger.info("Downloads database initialized successfully.")
        except sqlite3.Error as e:
            logger.critical(f"Database initialization error in DownloadManager: {e}", exc_info=True)
        finally:
            conn.close()

    def handle_download(self, download: QWebEngineDownloadRequest):
        """Called when a download is requested by the browser engine."""
        # Set save directory to the preferred Downloads folder
        download.setDownloadDirectory(self.download_dir)
        
        item = DownloadItem(download)
        item.filepath = os.path.join(self.download_dir, download.downloadFileName())
        self.active_downloads.append(item)

        # Connect download signals
        download.receivedBytesChanged.connect(lambda: self._on_progress(item))
        download.isFinishedChanged.connect(lambda: self._on_finished(item))
        
        # Accept the download
        download.accept()
        logger.info(f"Accepted download request: {item.filename} ({item.url})")
        self.download_added.emit(item)

    def _on_progress(self, item: DownloadItem):
        item.received_bytes = item.download.receivedBytes()
        item.total_bytes = item.download.totalBytes()
        self.download_updated.emit(item)

    def _on_finished(self, item: DownloadItem):
        state = item.download.state()
        if state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
            item.status = "completed"
            logger.info(f"Download completed successfully: {item.filename}")
        elif state == QWebEngineDownloadRequest.DownloadState.DownloadCancelled:
            item.status = "cancelled"
            logger.info(f"Download cancelled: {item.filename}")
        else:
            item.status = "failed"
            logger.warning(f"Download failed: {item.filename} with state code {state}")
        
        item.received_bytes = item.download.receivedBytes()
        item.total_bytes = item.download.totalBytes()
        
        # Save to history DB
        self._save_to_history(item)
        self.download_finished.emit(item)

    def _save_to_history(self, item: DownloadItem):
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO downloads (filename, url, filepath, size_bytes, status, timestamp) VALUES (?, ?, ?, ?, ?, ?)',
                    (item.filename, item.url, item.filepath, item.total_bytes, item.status, datetime.now().isoformat())
                )
            logger.info(f"Saved download result to history database: {item.filename} ({item.status})")
        except sqlite3.Error as e:
            logger.error(f"Failed to save download history for {item.filename}: {e}", exc_info=True)
        finally:
            conn.close()

    def get_download_history(self, limit=50):
        conn = self._get_connection()
        rows = []
        try:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT filename, url, filepath, size_bytes, status, timestamp FROM downloads ORDER BY id DESC LIMIT ?',
                (limit,)
            )
            rows = cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Failed to fetch download history: {e}", exc_info=True)
        finally:
            conn.close()
        return rows

    def clear_completed(self):
        """Remove completed downloads from active list."""
        self.active_downloads = [d for d in self.active_downloads if d.status == "downloading"]
        logger.info("Cleared completed downloads from active monitor list.")

