# doujinshi_manager/database.py
import sqlite3
import os

class Database:
    def __init__(self, db_path="db/tracker.db"):
        # Ensure the db directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        # Create/connect to the database
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key enforcement
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()