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
            cursor.execute('''CREATE TABLE IF NOT EXISTS jobs
                              (
                                  id
                                  INTEGER
                                  PRIMARY
                                  KEY,
                                  company
                                  TEXT,
                                  role
                                  TEXT,
                                  status
                                  TEXT
                                  DEFAULT
                                  'Waiting'
                              )''')

            cursor.execute('''CREATE TABLE IF NOT EXISTS videos
                              (
                                  id
                                  INTEGER
                                  PRIMARY
                                  KEY,
                                  topic
                                  TEXT,
                                  type
                                  TEXT,
                                  strength_score
                                  INTEGER,
                                  time_to_beat
                                  TEXT,
                                  is_ready
                                  BOOLEAN
                                  DEFAULT
                                  0,
                                  is_completed
                                  BOOLEAN
                                  DEFAULT
                                  0
                              )''')

            cursor.execute('''CREATE TABLE IF NOT EXISTS subtopics
            (
                id
                INTEGER
                PRIMARY
                KEY,
                video_id
                INTEGER,
                game_name
                TEXT,
                is_completed
                BOOLEAN
                DEFAULT
                0,
                FOREIGN
                KEY
                              (
                video_id
                              ) REFERENCES videos
                              (
                                  id
                              ))''')

            # --- SAFE MIGRATION: Add new columns to subtopics if they don't exist ---
            try:
                cursor.execute("ALTER TABLE subtopics ADD COLUMN strength_score INTEGER DEFAULT 0")
                cursor.execute("ALTER TABLE subtopics ADD COLUMN time_to_beat TEXT DEFAULT ''")
                cursor.execute("ALTER TABLE subtopics ADD COLUMN is_ready BOOLEAN DEFAULT 0")
            except sqlite3.OperationalError:
                pass  # Columns already exist, move on

            cursor.execute("UPDATE videos SET is_ready = 0 WHERE is_ready IS NULL")
            cursor.execute("UPDATE videos SET is_completed = 0 WHERE is_completed IS NULL")
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

    # --- VIDEO FUNCTIONS ---
    def add_video(self, topic, v_type, score, ttb):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO videos (topic, type, strength_score, time_to_beat, is_ready, is_completed) VALUES (?, ?, ?, ?, 0, 0)",
                (topic, v_type, score, ttb))
            conn.commit()

    def get_videos(self, is_ready=0):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM videos WHERE is_ready = ? ORDER BY strength_score DESC", (is_ready,))
            return cursor.fetchall()

    def update_video_ready_status(self, video_id, is_ready):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE videos SET is_ready = ? WHERE id = ?", (is_ready, video_id))
            conn.commit()

    def update_video_details(self, video_id, topic, v_type, score, ttb):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE videos SET topic = ?, type = ?, strength_score = ?, time_to_beat = ? WHERE id = ?",
                           (topic, v_type, score, ttb, video_id))
            conn.commit()

    def delete_video(self, video_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM videos WHERE id = ?", (video_id,))
            cursor.execute("DELETE FROM subtopics WHERE video_id = ?", (video_id,))
            conn.commit()

    # --- SUBTOPIC (MULTI-GAME) FUNCTIONS ---
    def add_subtopic(self, video_id, game_name, score, ttb):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO subtopics (video_id, game_name, strength_score, time_to_beat, is_ready) VALUES (?, ?, ?, ?, 0)",
                (video_id, game_name, score, ttb))
            conn.commit()
        self.sync_parent_multi_game(video_id)  # Update parent automatically

    def get_subtopics(self, video_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, game_name, strength_score, time_to_beat, is_ready FROM subtopics WHERE video_id = ? ORDER BY strength_score DESC",
                (video_id,))
            return cursor.fetchall()

    def update_subtopic_ready(self, sub_id, video_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE subtopics SET is_ready = 1 WHERE id = ?", (sub_id,))
            conn.commit()
        self.sync_parent_multi_game(video_id)  # Check if all are ready

    def delete_subtopic(self, sub_id, video_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM subtopics WHERE id = ?", (sub_id,))
            conn.commit()
        self.sync_parent_multi_game(video_id)

    def sync_parent_multi_game(self, video_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Get total subgames, count of ready subgames, and the max score
            cursor.execute("SELECT COUNT(id), SUM(is_ready), MAX(strength_score) FROM subtopics WHERE video_id = ?",
                           (video_id,))
            total, ready_count, max_score = cursor.fetchone()

            if total == 0 or total is None:
                # No subgames yet, reset to 0
                cursor.execute("UPDATE videos SET strength_score = 0, is_ready = 0 WHERE id = ?", (video_id,))
            else:
                max_score = max_score if max_score is not None else 0
                # If total subgames equals ready subgames, the parent is ready!
                is_ready = 1 if total == ready_count else 0
                cursor.execute("UPDATE videos SET strength_score = ?, is_ready = ? WHERE id = ?",
                               (max_score, is_ready, video_id))
            conn.commit()