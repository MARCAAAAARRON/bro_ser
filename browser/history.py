import os
import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger("BroSer.History")

class HistoryManager:
    def __init__(self):
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        os.makedirs(data_dir, exist_ok=True)
        self.db_path = os.path.join(data_dir, 'history.db')
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
        except sqlite3.Error as e:
            logger.error(f"Failed to set PRAGMA on history DB: {e}")
        return conn

    def _init_db(self):
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS visits (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        url TEXT NOT NULL,
                        title TEXT,
                        timestamp TEXT NOT NULL
                    )
                ''')
                # Index timestamp and url for high-performance sorting and searches
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_visits_timestamp ON visits(timestamp DESC)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_visits_url ON visits(url)')
            logger.info("History database initialized successfully with WAL and indexes.")
        except sqlite3.Error as e:
            logger.critical(f"Database initialization error in HistoryManager: {e}", exc_info=True)
        finally:
            conn.close()

    def add_visit(self, url, title=""):
        if not url or url in ("about:blank", ""):
            return
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO visits (url, title, timestamp) VALUES (?, ?, ?)',
                    (url, title, datetime.now().isoformat())
                )
            logger.debug(f"Added history visit: {url}")
        except sqlite3.Error as e:
            logger.error(f"Failed to add history visit for {url}: {e}", exc_info=True)
        finally:
            conn.close()

    def get_recent_visits(self, limit=100):
        conn = self._get_connection()
        rows = []
        try:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT url, title, timestamp FROM visits ORDER BY timestamp DESC, id DESC LIMIT ?',
                (limit,)
            )
            rows = cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Failed to query recent visits: {e}", exc_info=True)
        finally:
            conn.close()
        return rows

    def clear_history(self):
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM visits')
            logger.info("Browsing history cleared successfully.")
        except sqlite3.Error as e:
            logger.error(f"Failed to clear history: {e}", exc_info=True)
        finally:
            conn.close()


class BookmarkManager:
    def __init__(self):
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        os.makedirs(data_dir, exist_ok=True)
        self.db_path = os.path.join(data_dir, 'bookmarks.db')
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
        except sqlite3.Error as e:
            logger.error(f"Failed to set PRAGMA on bookmarks DB: {e}")
        return conn

    def _init_db(self):
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS bookmarks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        url TEXT NOT NULL UNIQUE,
                        title TEXT,
                        timestamp TEXT NOT NULL
                    )
                ''')
                # Index bookmarks url for super fast lookup check (star button on toolbar)
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_bookmarks_url ON bookmarks(url)')
            logger.info("Bookmarks database initialized successfully.")
        except sqlite3.Error as e:
            logger.critical(f"Database initialization error in BookmarkManager: {e}", exc_info=True)
        finally:
            conn.close()

    def add_bookmark(self, url, title=""):
        if not url or url in ("about:blank", ""):
            return False
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO bookmarks (url, title, timestamp) VALUES (?, ?, ?)',
                    (url, title, datetime.now().isoformat())
                )
            logger.info(f"Bookmarked page: {url}")
            return True
        except sqlite3.IntegrityError:
            # Already bookmarked
            return False
        except sqlite3.Error as e:
            logger.error(f"Failed to add bookmark: {e}", exc_info=True)
            return False
        finally:
            conn.close()

    def remove_bookmark(self, url):
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM bookmarks WHERE url = ?', (url,))
            logger.info(f"Removed bookmark: {url}")
        except sqlite3.Error as e:
            logger.error(f"Failed to remove bookmark: {e}", exc_info=True)
        finally:
            conn.close()

    def is_bookmarked(self, url):
        conn = self._get_connection()
        result = None
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM bookmarks WHERE url = ?', (url,))
            result = cursor.fetchone()
        except sqlite3.Error as e:
            logger.error(f"Failed to check bookmark status for {url}: {e}", exc_info=True)
        finally:
            conn.close()
        return result is not None

    def get_bookmarks(self):
        conn = self._get_connection()
        rows = []
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT url, title, timestamp FROM bookmarks ORDER BY id DESC')
            rows = cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Failed to query bookmarks: {e}", exc_info=True)
        finally:
            conn.close()
        return rows

