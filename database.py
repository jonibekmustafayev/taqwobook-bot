import sqlite3
import logging
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.db_path = Config.DB_PATH
        self._init_db()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")   # Tezlik uchun
        conn.execute("PRAGMA synchronous=NORMAL") # Tezlik uchun
        return conn

    def _init_db(self):
        """Jadvallarni yaratadi."""
        with self._get_conn() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id     INTEGER PRIMARY KEY,
                    username    TEXT,
                    full_name   TEXT,
                    joined_at   TEXT DEFAULT (datetime('now')),
                    last_seen   TEXT DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS books (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    name        TEXT NOT NULL,
                    name_lower  TEXT NOT NULL,
                    file_id     TEXT NOT NULL UNIQUE,
                    file_size   INTEGER DEFAULT 0,
                    downloads   INTEGER DEFAULT 0,
                    added_at    TEXT DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS downloads (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id     INTEGER,
                    book_id     INTEGER,
                    downloaded_at TEXT DEFAULT (datetime('now'))
                );

                CREATE INDEX IF NOT EXISTS idx_books_name ON books(name_lower);
            """)
        logger.info("Database initialized.")

    # ─── USERS ────────────────────────────────────────────────────────────────

    def add_user(self, user_id: int, username: str, full_name: str):
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO users (user_id, username, full_name)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    username  = excluded.username,
                    full_name = excluded.full_name,
                    last_seen = datetime('now')
            """, (user_id, username, full_name))

    # ─── BOOKS ────────────────────────────────────────────────────────────────

    def add_book(self, name: str, file_id: str, file_size: int = 0):
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO books (name, name_lower, file_id, file_size)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(file_id) DO UPDATE SET
                    name       = excluded.name,
                    name_lower = excluded.name_lower
            """, (name, name.lower(), file_id, file_size))
        logger.info(f"Book added/updated: {name}")

    def search_books(self, query: str) -> list:
        """Kitobni qidiradi — tez va aniq."""
        q = query.lower().strip()
        with self._get_conn() as conn:
            # Avval aniq moslikni qidirish
            rows = conn.execute("""
                SELECT id, name, file_id, file_size, downloads
                FROM books
                WHERE name_lower LIKE ?
                ORDER BY
                    CASE WHEN name_lower = ? THEN 0
                         WHEN name_lower LIKE ? THEN 1
                         ELSE 2 END,
                    downloads DESC
                LIMIT 10
            """, (f"%{q}%", q, f"{q}%")).fetchall()

        return [dict(row) for row in rows]

    def get_book_by_id(self, book_id: int) -> dict | None:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT id, name, file_id, file_size, downloads FROM books WHERE id = ?",
                (book_id,)
            ).fetchone()
        return dict(row) if row else None

    # ─── DOWNLOADS ────────────────────────────────────────────────────────────

    def log_download(self, user_id: int, book_id: int):
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO downloads (user_id, book_id) VALUES (?, ?)",
                (user_id, book_id)
            )
            conn.execute(
                "UPDATE books SET downloads = downloads + 1 WHERE id = ?",
                (book_id,)
            )

    # ─── STATS ────────────────────────────────────────────────────────────────

    def get_stats(self) -> dict:
        with self._get_conn() as conn:
            users     = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            books     = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
            downloads = conn.execute("SELECT COUNT(*) FROM downloads").fetchone()[0]
        return {"users": users, "books": books, "downloads": downloads}
