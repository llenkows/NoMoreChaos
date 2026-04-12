import sqlite3
import os


class DatabaseManager:
    def __init__(self):
        doc_path = os.path.expanduser("~/Documents/NoMoreChaos")
        if not os.path.exists(doc_path):
            os.makedirs(doc_path)

        self.db_path = os.path.join(doc_path, "chaos_data.db")
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Jobs Table
            cursor.execute('''CREATE TABLE IF NOT EXISTS jobs (
                                  id INTEGER PRIMARY KEY,
                                  company TEXT,
                                  role TEXT,
                                  status TEXT DEFAULT 'Waiting')''')

            # Videos Table (For later)
            cursor.execute('''CREATE TABLE IF NOT EXISTS videos (
                                  id INTEGER PRIMARY KEY,
                                  topic TEXT,
                                  type TEXT,
                                  strength_score INTEGER,
                                  time_to_beat TEXT,
                                  is_ready BOOLEAN,
                                  is_completed BOOLEAN DEFAULT 0)''')
            conn.commit()

    # --- JOB FUNCTIONS ---
    def add_job(self, company, role):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO jobs (company, role) VALUES (?, ?)", (company, role))
            conn.commit()

    def get_jobs(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM jobs ORDER BY id DESC")
            return cursor.fetchall()

    def update_job_status(self, job_id, status):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE jobs SET status = ? WHERE id = ?", (status, job_id))
            conn.commit()

    def update_job_details(self, job_id, company, role):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE jobs SET company = ?, role = ? WHERE id = ?", (company, role, job_id))
            conn.commit()

    def delete_job(self, job_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
            conn.commit()