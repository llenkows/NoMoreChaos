import customtkinter as ctk
import requests
from io import BytesIO
from PIL import Image
from dateutil import parser

class HomePage(ctk.CTkFrame):
    def __init__(self, parent, db_manager, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.db = db_manager

        self.bg_color = "#000000"
        self.card_color = "#121212"
        self.neon_green = "#39FF14"
        self.dark_green = "#2ce00f"
        self.warning_red = "#FF3333"

        self.build_ui()

    def build_ui(self):
        title = ctk.CTkLabel(self, text="Today's Agenda!", font=("Arial", 32, "bold"), text_color="white")
        title.pack(anchor="w", pady=(0, 20))

        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)

        left_column = ctk.CTkFrame(content_frame, fg_color="transparent")
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right_column = ctk.CTkFrame(content_frame, fg_color="transparent")
        right_column.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # JOBS REMINDER
        jobs_today = self.db.get_jobs_count_today()
        job_card = ctk.CTkFrame(left_column, fg_color=self.card_color, corner_radius=10)
        job_card.pack(fill="x", pady=(0, 20), ipady=15)

        ctk.CTkLabel(job_card, text="💼 Job Applications", font=("Arial", 14, "bold"), text_color="#AAAAAA").pack(
            pady=(10, 5))
        if jobs_today == 0:
            ctk.CTkLabel(job_card, text="⚠️ You haven't applied to any jobs today!", font=("Arial", 18, "bold"),
                         text_color=self.warning_red).pack()
        else:
            ctk.CTkLabel(job_card, text=f"✅ Daily Goal Met! ({jobs_today} app{'s' if jobs_today > 1 else ''} today)",
                         font=("Arial", 18, "bold"), text_color=self.neon_green).pack()

        # RANDOM VIDEO
        video = self.db.get_dashboard_video()
        vid_card = ctk.CTkFrame(left_column, fg_color=self.card_color, corner_radius=10)
        vid_card.pack(fill="x", pady=(0, 20), ipady=15)

        ctk.CTkLabel(vid_card, text="🎥 Focus Topic", font=("Arial", 14, "bold"), text_color="#AAAAAA").pack(
            pady=(10, 5))
        if video:
            topic, subtitle = video
            ctk.CTkLabel(vid_card, text=topic, font=("Arial", 22, "bold"), text_color=self.neon_green,
                         wraplength=350).pack()
            ctk.CTkLabel(vid_card, text=subtitle, font=("Arial", 14), text_color="white").pack(pady=(5, 0))
        else:
            ctk.CTkLabel(vid_card, text="No pending videos. You're all caught up!", font=("Arial", 16),
                         text_color="white").pack()

        # TODAY'S SPORTS
        sports_card = ctk.CTkFrame(left_column, fg_color=self.card_color, corner_radius=10)
        sports_card.pack(fill="x", pady=(0, 20), ipady=10)

        ctk.CTkLabel(sports_card, text="🏀 Today's Games", font=("Arial", 14, "bold"), text_color="#AAAAAA").pack(
            pady=(10, 5))

        today_games = self.db.get_games_for_today()

        if not today_games:
            ctk.CTkLabel(sports_card, text="No games scheduled for today.", font=("Arial", 14),
                         text_color="#555555").pack(pady=10)
        else:
            for league, home, away, start_utc in today_games:
                try:
                    dt_utc = parser.isoparse(start_utc)
                    time_str = dt_utc.astimezone().strftime("%I:%M %p")
                except:
                    time_str = "TBD"

                is_philly = any(pt in home or pt in away for pt in self.db.philly_teams)

                game_text = f"[{league}] {away} @ {home} - {time_str}"
                game_color = self.neon_green if is_philly else "white"

                ctk.CTkLabel(sports_card, text=game_text, font=("Arial", 14, "bold" if is_philly else "normal"),
                             text_color=game_color, wraplength=350).pack(pady=2)

        # RANDOM ALBUM
        album = self.db.get_dashboard_album()
        music_card = ctk.CTkFrame(right_column, fg_color=self.card_color, corner_radius=10)
        music_card.pack(fill="both", expand=True, pady=(0, 10))
        ctk.CTkLabel(music_card, text="🎵 Listen to this", font=("Arial", 14, "bold"), text_color="#AAAAAA").pack(
            pady=(10, 5))
        if album:
            album_id, title_text, artist, img_url = album
            self.load_image(music_card, img_url, size=(120, 120))
            ctk.CTkLabel(music_card, text=title_text, font=("Arial", 18, "bold"), text_color=self.neon_green,
                         wraplength=300).pack(pady=(10, 0))
            ctk.CTkLabel(music_card, text=f"by {artist}", font=("Arial", 14), text_color="white").pack()
            btn_rate = ctk.CTkButton(music_card, text="Rate This Album ➔", fg_color=self.neon_green,
                                     text_color="black",
                                     hover_color=self.dark_green, font=("Arial", 14, "bold"),
                                     command=lambda a=album: self.winfo_toplevel().show_page('music', auto_rate_album=album))
            btn_rate.pack(pady=(15, 0))
        else:
            ctk.CTkLabel(music_card, text="Queue is empty.", font=("Arial", 16), text_color="white").pack(pady=20)

        # RANDOM MOVIE
        movie = self.db.get_dashboard_movie()
        movie_card = ctk.CTkFrame(right_column, fg_color=self.card_color, corner_radius=10)
        movie_card.pack(fill="both", expand=True, pady=(10, 0))

        ctk.CTkLabel(movie_card, text="🍿 Watch this", font=("Arial", 14, "bold"), text_color="#AAAAAA").pack(
            pady=(10, 5))
        if movie:
            slug, m_title, runtime, rating, poster_url, lbx_url = movie
            self.load_image(movie_card, poster_url, size=(100, 150))
            ctk.CTkLabel(movie_card, text=m_title, font=("Arial", 18, "bold"), text_color=self.neon_green,
                         wraplength=300).pack(pady=(10, 0))
        else:
            ctk.CTkLabel(movie_card, text="Watchlist is empty.", font=("Arial", 16), text_color="white").pack(pady=20)



    def load_image(self, parent, url, size):
        if url:
            try:
                img_data = requests.get(url).content
                img_item = Image.open(BytesIO(img_data))
                ctk_img = ctk.CTkImage(light_image=img_item, dark_image=img_item, size=size)
                ctk.CTkLabel(parent, text="", image=ctk_img).pack(pady=5)
            except:
                ctk.CTkLabel(parent, text="[Image Unavailable]", text_color="#555555").pack(pady=5)