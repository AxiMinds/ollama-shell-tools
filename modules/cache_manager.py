import sqlite3
import json
import os
import threading
from datetime import datetime

class CacheManager:
    def __init__(self, db_path='prompt_cache.db'):
        self.db_path = db_path
        self.local = threading.local()
        self.create_table()

    def get_connection(self):
        if not hasattr(self.local, 'conn'):
            self.local.conn = sqlite3.connect(self.db_path)
        return self.local.conn

    def create_table(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prompt_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model TEXT,
                prompt TEXT,
                response TEXT,
                metadata TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

    def add_to_cache(self, model, prompt, response, metadata):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO prompt_cache (model, prompt, response, metadata, timestamp)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (model, prompt, response, json.dumps(metadata)))
        conn.commit()

    def get_from_cache(self, model, prompt):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT response, metadata FROM prompt_cache
            WHERE model = ? AND prompt = ?
            ORDER BY timestamp DESC LIMIT 1
        ''', (model, prompt))
        result = cursor.fetchone()
        if result:
            return result[0], json.loads(result[1])
        return None, None

    def clear_cache(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM prompt_cache')
        conn.commit()

    def get_cache_size(self):
        return os.path.getsize(self.db_path)

    def trim_cache(self, max_size=100*1024*1024):  # 100MB
        while self.get_cache_size() > max_size:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM prompt_cache WHERE id IN (SELECT id FROM prompt_cache ORDER BY timestamp ASC LIMIT 100)')
            conn.commit()

cache_manager = CacheManager()
