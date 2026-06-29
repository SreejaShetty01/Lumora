import sqlite3
import pandas as pd
import os

class DatabaseManager:
    def __init__(self, db_path="database/lumora.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize the database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Lectures table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lectures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_path TEXT,
                status TEXT DEFAULT 'processing',
                transcript TEXT,
                notes TEXT,
                faiss_path TEXT
            )
        ''')

        # Add quiz and flashcards columns if they don't exist
        try:
            cursor.execute("ALTER TABLE lectures ADD COLUMN quiz TEXT")
        except sqlite3.OperationalError:
            pass
            
        try:
            cursor.execute("ALTER TABLE lectures ADD COLUMN flashcards TEXT")
        except sqlite3.OperationalError:
            pass

        # Chat history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lecture_id INTEGER,
                role TEXT,
                content TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lecture_id) REFERENCES lectures(id)
            )
        ''')
        
        conn.commit()
        conn.close()

    def get_connection(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)
