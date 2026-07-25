# -*- coding: utf-8 -*-
"""
Batch Queue Manager
Persistent SQLite queue for sequential, resumable folder batch runs.
"""
import sqlite3
import os
import time

class BatchQueue:
    """Manages persistent batch execution queue in local SQLite database."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS batch_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    input_file TEXT UNIQUE,
                    output_prefix TEXT,
                    status TEXT DEFAULT 'Queued', -- Queued, Running, Completed, Completed_Warnings, Skipped, Failed, Cancelled
                    error_message TEXT,
                    started_at TEXT,
                    completed_at TEXT
                )
            """)

    def add_job(self, input_file: str, output_prefix: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO batch_jobs (input_file, output_prefix, status)
                VALUES (?, ?, 'Queued')
                ON CONFLICT(input_file) DO UPDATE SET status='Queued', error_message=NULL
            """, (input_file, output_prefix))

    def get_next_job(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, input_file, output_prefix FROM batch_jobs WHERE status='Queued' LIMIT 1")
            return cursor.fetchone()

    def update_status(self, job_id: int, status: str, error_message: str = None):
        now = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        with sqlite3.connect(self.db_path) as conn:
            if status == 'Running':
                conn.execute("UPDATE batch_jobs SET status=?, started_at=? WHERE id=?", (status, now, job_id))
            else:
                conn.execute("UPDATE batch_jobs SET status=?, error_message=?, completed_at=? WHERE id=?", (status, error_message, now, job_id))

    def get_summary(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status, COUNT(*) FROM batch_jobs GROUP BY status")
            return dict(cursor.fetchall())
