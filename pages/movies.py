import customtkinter as ctk
from customtkinter import filedialog
import requests
import threading
import csv
from io import BytesIO
from PIL import Image
import webbrowser

TMDB_API_KEY = '7f2d94ac8dc4365b1fecb2e1cf16dcd8'


class MoviesPage(ctk.CTkFrame):
    def __init__(self, parent, db_manager, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.db = db_manager

        self.bg_color = "#000000"
        self.card_color = "#121212"
        self.neon_green = "#39FF14"
        self.dark_green = "#2ce00f"

        self.build_ui()

    def build_ui(self):
        title = ctk.CTkLabel(self, text="Movie Watchlist", font=("Arial", 28, "bold"), text_color="white")
        title.pack(anchor="w", pady=(0, 10))

        # --- IMPORT ROW ---
        sync_frame = ctk.CTkFrame(self, fg_color=self.card_color, corner_radius=10)
        sync_frame.pack(fill="x", pady=(0, 20), ipadx=10, ipady=10)

        self.btn_import = ctk.CTkButton(sync_frame, text="Import Watchlist CSV", fg_color=self.neon_green,
                                        text_color="black",
                                        hover_color=self.dark_green, font=("Arial", 14, "bold"),
                                        command=self.select_file_and_sync)
        self.btn_import.pack(side="left", padx=(10, 10))

        self.lbl_status = ctk.CTkLabel(sync_frame, text="Click to update your local database.", text_color="#AAAAAA")
        self.lbl_status.pack(side="left", padx=15)

        # --- ACTION BUTTONS ---
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(fill="x", pady=10)

        btn_random = ctk.CTkButton(action_frame, text="🎲 Random Movie", fg_color="#333333", hover_color="#555555",
                                   font=("Arial", 16, "bold"), command=lambda: self.display_movie("random"))
        btn_random.pack(side="left", expand=True, padx=5, ipady=10)

        btn_shortest = ctk.CTkButton(action_frame, text="⏱️ Shortest Movie", fg_color="#333333", hover_color="#555555",
                                     font=("Arial", 16, "bold"), command=lambda: self.display_movie("shortest"))
        btn_shortest.pack(side="left", expand=True, padx=5, ipady=10)

        btn_highest = ctk.CTkButton(action_frame, text="⭐ Highest Rated", fg_color="#333333", hover_color="#555555",
                                    font=("Arial", 16, "bold"), command=lambda: self.display_movie("highest"))
        btn_highest.pack(side="left", expand=True, padx=5, ipady=10)

        # --- DISPLAY AREA ---
        self.display_frame = ctk.CTkFrame(self, fg_color=self.card_color, corner_radius=15)
        self.display_frame.pack(fill="both", expand=True, pady=20)

        self.lbl_poster = ctk.CTkLabel(self.display_frame, text="Import a CSV or click a button above to begin.",
                                       text_color="#555555", font=("Arial", 18))
        self.lbl_poster.pack(pady=50)

    # ==========================================
    # 🔄 CSV IMPORT LOGIC
    # ==========================================
    def select_file_and_sync(self):
        # Open Windows File Picker
        file_path = filedialog.askopenfilename(
            title="Select Letterboxd Watchlist CSV",
            filetypes=[("CSV Files", "*.csv")]
        )

        if file_path:
            self.btn_import.configure(state="disabled", text="Importing...")
            self.lbl_status.configure(text="Reading CSV and fetching posters...", text_color=self.neon_green)

            threading.Thread(target=self.process_csv, args=(file_path,), daemon=True).start()

    def process_csv(self, file_path):
        try:
            self.db.clear_movies()  # Clear the old database so we don't get duplicates
            movies_found = 0

            # Read the CSV with UTF-8 encoding
            with open(file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    title = row.get('Name')
                    year = row.get('Year')
                    lbx_url = row.get('Letterboxd URI')

                    if not title: continue

                    # Create a unique ID from the Letterboxd URL (e.g., extracting '2b0k' from 'https://boxd.it/2b0k')
                    slug = lbx_url.strip('/').split('/')[-1] if lbx_url else title.replace(" ", "-").lower()

                    # --- FETCH TMDB DATA ---
                    tmdb_url = "https://api.themoviedb.org/3/search/movie"
                    tmdb_params = {
                        "query": title,
                        "api_key": TMDB_API_KEY
                    }
                    # Add year for extreme accuracy if the CSV provided it
                    if year:
                        tmdb_params["primary_release_year"] = year

                    tmdb_search = requests.get(tmdb_url, params=tmdb_params).json()

                    if tmdb_search.get('results'):
                        tmdb_id = tmdb_search['results'][0]['id']
                        details_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
                        details = requests.get(details_url, params={"api_key": TMDB_API_KEY}).json()

                        runtime = details.get('runtime') or 0
                        rating = details.get('vote_average') or 0.0
                        poster_path = details.get('poster_path')
                        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""

                        self.db.save_movie(slug, title, runtime, rating, poster_url, lbx_url)
                        movies_found += 1

                        self.lbl_status.configure(text=f"Imported {movies_found} movies...")

            if movies_found > 0:
                self.lbl_status.configure(text=f"Success! {movies_found} movies imported.", text_color=self.neon_green)
            else:
                self.lbl_status.configure(text="No valid movies found in CSV.", text_color="#AAAAAA")

        except Exception as e:
            self.lbl_status.configure(text="Error importing CSV. Make sure it's the correct Letterboxd format.",
                                      text_color="#FF3333")
            print(f"Import Error: {e}")
        finally:
            self.btn_import.configure(state="normal", text="Import Watchlist CSV")

    # ==========================================
    # 🎬 DISPLAY LOGIC
    # ==========================================
    def display_movie(self, criteria):
        movie = self.db.get_movie_by_criteria(criteria)
        if not movie:
            self.lbl_poster.configure(text="No movies found. Please import your watchlist first.")
            return

        slug, title, runtime, rating, poster_url, lbx_url = movie

        for widget in self.display_frame.winfo_children(): widget.destroy()

        poster_frame = ctk.CTkFrame(self.display_frame, fg_color="transparent")
        poster_frame.pack(side="left", padx=30, pady=30)

        info_frame = ctk.CTkFrame(self.display_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, pady=30, padx=(0, 30))

        # --- Load Poster ---
        if poster_url:
            try:
                img_data = requests.get(poster_url).content
                img_item = Image.open(BytesIO(img_data))
                ctk_img = ctk.CTkImage(light_image=img_item, dark_image=img_item, size=(200, 300))
                lbl_img = ctk.CTkLabel(poster_frame, text="", image=ctk_img)
                lbl_img.pack()
            except:
                ctk.CTkLabel(poster_frame, text="Poster Unavailable", width=200, height=300, fg_color="#333333").pack()

        ctk.CTkLabel(info_frame, text=title, font=("Arial", 36, "bold"), text_color=self.neon_green, wraplength=400,
                     justify="left").pack(anchor="w", pady=(0, 10))

        info_text = f"⏱️ Runtime: {runtime} minutes\n⭐ TMDB Rating: {round(rating, 1)} / 10"
        ctk.CTkLabel(info_frame, text=info_text, font=("Arial", 18), text_color="white", justify="left").pack(
            anchor="w", pady=10)

        btn_lbx = ctk.CTkButton(info_frame, text="Open in Letterboxd ↗", fg_color="#2C3440", hover_color="#445566",
                                font=("Arial", 16, "bold"), command=lambda: webbrowser.open(lbx_url))
        btn_lbx.pack(anchor="w", pady=20)

        btn_watched = ctk.CTkButton(info_frame, text="✅ Mark as Watched", fg_color=self.neon_green, text_color="black",
                                    hover_color=self.dark_green, font=("Arial", 16, "bold"),
                                    command=lambda s=slug, t=title: self.mark_as_watched(s, t))
        btn_watched.pack(anchor="w", pady=5)

    def mark_as_watched(self, slug, title):
        # 1. Delete from the local database
        self.db.delete_movie(slug)

        # 2. Clear the screen
        for widget in self.display_frame.winfo_children(): widget.destroy()

        # 3. Show a satisfying success message
        self.lbl_poster = ctk.CTkLabel(self.display_frame, text=f"✅ '{title}' marked as watched and removed!",
                                       text_color=self.neon_green, font=("Arial", 20, "bold"))
        self.lbl_poster.pack(pady=50)