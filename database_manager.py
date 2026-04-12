import sqlite3
import os

class DatabaseManager:
    def __init__(self):
        # Path to Documents/NeonHub
        doc_path = os.path.expanduser("~/Documents/NoMoreChaos")
        if not os.path.exists(doc_path):
            os.makedirs(doc_path)

        self.db_path = os.path.join(doc_path, "neon_data.db")
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

            # Video Ideas Table (Parent)
            cursor.execute('''CREATE TABLE IF NOT EXISTS videos (
                                  id INTEGER PRIMARY KEY,
                                  topic TEXT,
                                  type TEXT, -- 'Single' or 'Multi'
                                  strength_score INTEGER,
                                  time_to_beat TEXT,
                                  is_ready BOOLEAN,
                                  is_completed BOOLEAN DEFAULT 0)''')

            # Subtopics for Multi-Game Videos
            cursor.execute('''CREATE TABLE IF NOT EXISTS subtopics (
                id INTEGER PRIMARY KEY,
                video_id INTEGER,
                name TEXT,
                is_completed BOOLEAN DEFAULT 0,
                FOREIGN KEY(video_id) REFERENCES videos(id))''')
            conn.commit()


db = DatabaseManager()
print(f"Database initialized at: {db.db_path}")