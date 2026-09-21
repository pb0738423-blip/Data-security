import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "secure_transfer.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute(
            '''
            CREATE TABLE IF NOT EXISTS transfers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_filename TEXT NOT NULL,
                stored_filename TEXT NOT NULL,
                sender TEXT NOT NULL,
                receiver TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                risk_label TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            '''
        )
        connection.commit()


def add_transfer(original_filename, stored_filename, sender, receiver,
                 file_size, risk_label):
    with get_connection() as connection:
        cursor = connection.execute(
            '''
            INSERT INTO transfers
            (original_filename, stored_filename, sender, receiver, file_size, risk_label)
            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            (original_filename, stored_filename, sender, receiver, file_size, risk_label),
        )
        connection.commit()
        return cursor.lastrowid


def list_transfers():
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM transfers ORDER BY created_at DESC"
        ).fetchall()
        return [dict(row) for row in rows]
