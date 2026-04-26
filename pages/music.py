import customtkinter as ctk
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import math
import requests
from io import BytesIO
from PIL import Image
import threading

SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')


class MusicPage(ctk.CTkFrame):
    def __init__(self, parent, db_manager, auto_rate_album=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.db = db_manager

        auth_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
        self.sp = spotipy.Spotify(auth_manager=auth_manager)

        self.bg_color = "#000000"
        self.card_color = "#121212"
        self.neon_green = "#39FF14"
        self.dark_green = "#2ce00f"

        self.current_album = None
        self.track_items = []

        self.build_ui()
        # Catch the dashboard album and open the popup automatically
        if auto_rate_album:
            # delay the popup by 300ms so the UI finishes drawing first
            self.after(300, lambda: self.trigger_dashboard_rating(auto_rate_album))

    def build_ui(self):
        title = ctk.CTkLabel(self, text="Music Rater", font=("Arial", 28, "bold"), text_color="white")
        title.pack(anchor="w", pady=(0, 10))

        self.tabs = ctk.CTkTabview(self, fg_color="transparent", segmented_button_selected_color=self.neon_green,
                                   segmented_button_selected_hover_color=self.dark_green, text_color="white")
        self.tabs.pack(fill="both", expand=True)

        self.tab_search = self.tabs.add("Search")
        self.tab_queue = self.tabs.add("Queued Albums")
        self.tab_saved = self.tabs.add("Saved Albums")

        self.build_search_tab()
        self.build_queue_tab()
        self.build_saved_tab()

    # SEARCH TAB
    def build_search_tab(self):
        search_frame = ctk.CTkFrame(self.tab_search, fg_color="transparent")
        search_frame.pack(fill="x", pady=10)

        self.entry_search = ctk.CTkEntry(search_frame, placeholder_text="Search Album...", width=300)
        self.entry_search.pack(side="left", padx=(0, 10))
        self.entry_search.bind("<Return>", self.search_spotify)

        btn_search = ctk.CTkButton(search_frame, text="Search Spotify", fg_color=self.neon_green, text_color="black",
                                   hover_color=self.dark_green, command=self.search_spotify)
        btn_search.pack(side="left")

        self.results_frame = ctk.CTkScrollableFrame(self.tab_search, fg_color=self.card_color)
        self.results_frame.pack(fill="both", expand=True, pady=10)

    def search_spotify(self, event=None):
        query = self.entry_search.get()
        if not query: return
        for widget in self.results_frame.winfo_children(): widget.destroy()

        results = self.sp.search(q=query, type='album', limit=8)
        albums = results['albums']['items']

        for album in albums:
            name = album['name']
            artist = album['artists'][0]['name']
            album_id = album['id']
            img_url = album['images'][0]['url'] if album['images'] else None

            row = ctk.CTkFrame(self.results_frame, fg_color="transparent")
            row.pack(fill="x", pady=5, padx=5)

            # Create a blank placeholder label first so the UI instantly draws
            lbl_img = ctk.CTkLabel(row, text="", width=50, height=50)
            lbl_img.pack(side="left", padx=(0, 15))

            # Send the download task to the background
            if img_url:
                self.load_image_async(lbl_img, img_url, size=(50, 50))

            lbl_info = ctk.CTkLabel(row, text=f"{name}\nby {artist}", font=("Arial", 14), justify="left")
            lbl_info.pack(side="left", pady=10)

            btn_queue = ctk.CTkButton(row, text="+ Add to Queue", fg_color="#333333", hover_color="#555555")
            btn_queue.configure(
                command=lambda a=album_id, n=name, art=artist, u=img_url, b=btn_queue: self.queue_album(a, n, art, u,
                                                                                                        b))
            btn_queue.pack(side="right", padx=10)

    def queue_album(self, album_id, name, artist, img_url, btn_widget):
        self.db.add_to_queue(album_id, artist, name, img_url)
        btn_widget.configure(text="Added ✓", fg_color=self.dark_green, state="disabled")
        self.refresh_queue_list()

    # QUEUE & RATE TAB
    def build_queue_tab(self):
        content_frame = ctk.CTkFrame(self.tab_queue, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, pady=10)

        self.queue_list_frame = ctk.CTkScrollableFrame(content_frame, width=300, fg_color=self.card_color)
        self.queue_list_frame.pack(side="left", fill="y", padx=(0, 10))

        self.rating_frame = ctk.CTkScrollableFrame(content_frame, fg_color=self.card_color)
        self.rating_frame.pack(side="left", fill="both", expand=True)

        self.after(100, self.refresh_queue_list())

    def refresh_queue_list(self):
        for widget in self.queue_list_frame.winfo_children(): widget.destroy()

        queued = self.db.get_queued_albums()
        for alb in queued:
            a_id, artist, title, img_url = alb

            card = ctk.CTkFrame(self.queue_list_frame, fg_color="#1E1E1E", corner_radius=5)
            card.pack(fill="x", pady=5, padx=5)

            lbl = ctk.CTkLabel(card, text=f"{title}\n{artist}", font=("Arial", 12), justify="left")
            lbl.pack(side="left", padx=10, pady=10)

            btn_del = ctk.CTkButton(card, text="X", width=25, fg_color="#FF3333", hover_color="#990000",
                                    command=lambda i=a_id: [self.db.delete_from_queue(i), self.refresh_queue_list()])
            btn_del.pack(side="right", padx=5)

            btn_rate = ctk.CTkButton(card, text="Rate", width=50, fg_color=self.neon_green, text_color="black",
                                     hover_color=self.dark_green,
                                     command=lambda i=a_id, t=title, a=artist, u=img_url: self.load_album_for_rating(i,
                                                                                                                     t,
                                                                                                                     a,
                                                                                                                     u))
            btn_rate.pack(side="right", padx=5)

    def load_album_for_rating(self, album_id, name, artist, img_url):
        self.current_album = {'id': album_id, 'name': name, 'artist': artist, 'img_url': img_url}
        self.track_items = []

        for widget in self.rating_frame.winfo_children(): widget.destroy()

        # Create the large placeholder label
        lbl_large_img = ctk.CTkLabel(self.rating_frame, text="", width=150, height=150)
        lbl_large_img.pack(pady=10)

        if img_url:
            self.load_image_async(lbl_large_img, img_url, size=(150, 150))

        ctk.CTkLabel(self.rating_frame, text=f"{name}\n{artist}", font=("Arial", 22, "bold"),
                     text_color=self.neon_green).pack(pady=5)

        tracks = self.sp.album_tracks(album_id)['items']

        for track in tracks:
            track_row = ctk.CTkFrame(self.rating_frame, fg_color="transparent")
            track_row.pack(fill="x", pady=5, padx=10)

            full_track_name = track['name']
            if len(full_track_name) > 35:
                display_name = full_track_name[:32] + "..."
            else:
                display_name = full_track_name

            ctk.CTkLabel(track_row, text=f"{track['track_number']}. {display_name}", width=250, anchor="w").pack(
                side="left")

            entry_score = ctk.CTkEntry(track_row, width=50, placeholder_text="0-10")
            entry_score.pack(side="left", padx=10)

            check_interlude = ctk.CTkCheckBox(track_row, text="Interlude", text_color="white", fg_color=self.neon_green,
                                              hover_color=self.dark_green,
                                              command=lambda e=entry_score: self.toggle_interlude(e))
            check_interlude.pack(side="left", padx=10)

            self.track_items.append({'id': track['id'], 'name': full_track_name, 'track_number': track['track_number'],
                                     'entry': entry_score, 'checkbox': check_interlude})

        ctk.CTkButton(self.rating_frame, text="Save Album Rating", fg_color=self.neon_green, text_color="black",
                      hover_color=self.dark_green, font=("Arial", 16, "bold"), command=self.save_rating).pack(pady=20)

    def toggle_interlude(self, entry_widget):
        if entry_widget.cget("state") == "normal":
            entry_widget.delete(0, 'end')
            entry_widget.configure(state="disabled", fg_color="#333333")
        else:
            entry_widget.configure(state="normal", fg_color="#1d1d1d")

    def save_rating(self):
        if not self.current_album: return

        scores = []
        tracks_data = []

        for t in self.track_items:
            is_interlude = t['checkbox'].get()
            if is_interlude:
                score_val = -1
            else:
                raw_val = t['entry'].get()
                try:
                    score_val = int(raw_val)
                    if not (0 <= score_val <= 10): score_val = 0
                except ValueError:
                    score_val = 0
                scores.append(score_val)

            tracks_data.append(
                {'id': t['id'], 'name': t['name'], 'track_number': t['track_number'], 'score': score_val})

        if len(scores) > 0:
            raw_avg = sum(scores) / len(scores)
            final_avg = math.ceil(raw_avg * 10) / 10.0
        else:
            final_avg = 0.0

        self.db.save_album_rating(self.current_album['id'], self.current_album['artist'], self.current_album['name'],
                                  self.current_album['img_url'], final_avg, tracks_data)
        self.db.delete_from_queue(self.current_album['id'])

        for widget in self.rating_frame.winfo_children(): widget.destroy()
        ctk.CTkLabel(self.rating_frame, text=f"Saved! Album Score: {final_avg}/10", font=("Arial", 20),
                     text_color=self.neon_green).pack(pady=50)

        self.refresh_queue_list()
        self.refresh_saved_list()

    # SAVED TAB & EDITING
    def build_saved_tab(self):
        self.saved_list = ctk.CTkScrollableFrame(self.tab_saved, fg_color="transparent")
        self.saved_list.pack(fill="both", expand=True)
        self.after(100, self.refresh_saved_list)

    def refresh_saved_list(self):
        for widget in self.saved_list.winfo_children(): widget.destroy()

        albums = self.db.get_rated_albums()
        for alb in albums:
            a_id, artist, title, score, img_url = alb
            card = ctk.CTkFrame(self.saved_list, fg_color=self.card_color, corner_radius=10)
            card.pack(fill="x", pady=5)

            # Cover Art Placeholder
            lbl_img = ctk.CTkLabel(card, text="", width=60, height=60)
            lbl_img.pack(side="left", padx=(10, 5), pady=10)

            if img_url:
                self.load_image_async(lbl_img, img_url, size=(60, 60))

            # Details
            lbl_info = ctk.CTkLabel(card, text=f"[{score}/10] {title}\nby {artist}", font=("Arial", 16, "bold"),
                                    text_color="white", justify="left")
            lbl_info.pack(side="left", padx=15, pady=15)

            # Controls
            btn_del = ctk.CTkButton(card, text="X", width=30, fg_color="#FF3333", hover_color="#990000",
                                    command=lambda i=a_id: [self.db.delete_album(i), self.refresh_saved_list()])
            btn_del.pack(side="right", padx=(5, 15))

            btn_edit = ctk.CTkButton(card, text="View/Edit Tracks", width=120, fg_color="#333333",
                                     hover_color="#555555",
                                     command=lambda i=a_id, t=title, a=artist,
                                                    u=img_url: self.open_edit_saved_album_popup(i, t, a, u))
            btn_edit.pack(side="right", padx=5)

    def open_edit_saved_album_popup(self, album_id, title, artist, img_url):
        popup = ctk.CTkToplevel(self)
        popup.title(f"Edit {title}")
        popup.geometry("450x600")
        popup.attributes("-topmost", True)
        popup.configure(fg_color=self.bg_color)

        lbl_title = ctk.CTkLabel(popup, text=f"Edit: {title}", font=("Arial", 20, "bold"), text_color=self.neon_green)
        lbl_title.pack(pady=(15, 5))

        track_frame = ctk.CTkScrollableFrame(popup, fg_color=self.card_color)
        track_frame.pack(fill="both", expand=True, padx=10, pady=10)

        tracks = self.db.get_album_tracks(album_id)
        local_track_items = []

        for track in tracks:
            t_id, t_name, t_num, t_score = track

            row = ctk.CTkFrame(track_frame, fg_color="transparent")
            row.pack(fill="x", pady=5)

            display_name = t_name[:30] + "..." if len(t_name) > 33 else t_name
            ctk.CTkLabel(row, text=f"{t_num}. {display_name}", width=220, anchor="w").pack(side="left")

            entry_score = ctk.CTkEntry(row, width=40)
            entry_score.pack(side="left", padx=5)

            check_interlude = ctk.CTkCheckBox(row, text="N/A", text_color="white", fg_color=self.neon_green,
                                              hover_color=self.dark_green, width=50,
                                              command=lambda e=entry_score: self.toggle_interlude(e))
            check_interlude.pack(side="left", padx=5)

            # Pre-fill data
            if t_score == -1:
                check_interlude.select()
                entry_score.configure(state="disabled", fg_color="#333333")
            else:
                entry_score.insert(0, str(t_score))

            local_track_items.append(
                {'id': t_id, 'name': t_name, 'track_number': t_num, 'entry': entry_score, 'checkbox': check_interlude})

        # Function to save changes directly from popup
        def save_edits():
            scores = []
            tracks_data = []
            for t in local_track_items:
                is_interlude = t['checkbox'].get()
                if is_interlude:
                    score_val = -1
                else:
                    try:
                        score_val = int(t['entry'].get())
                        if not (0 <= score_val <= 10): score_val = 0
                    except ValueError:
                        score_val = 0
                    scores.append(score_val)

                tracks_data.append(
                    {'id': t['id'], 'name': t['name'], 'track_number': t['track_number'], 'score': score_val})

            if len(scores) > 0:
                raw_avg = sum(scores) / len(scores)
                final_avg = math.ceil(raw_avg * 10) / 10.0
            else:
                final_avg = 0.0

            self.db.save_album_rating(album_id, artist, title, img_url, final_avg, tracks_data)
            popup.destroy()
            self.refresh_saved_list()

        btn_save = ctk.CTkButton(popup, text="Save Updates", fg_color=self.neon_green, text_color="black",
                                 hover_color=self.dark_green, font=("Arial", 14, "bold"), command=save_edits)
        btn_save.pack(pady=15)

    def trigger_dashboard_rating(self, album_data):
        try:
            # Safely unpack the tuple your database returned
            album_id = album_data[0]
            album_name = album_data[1]
            artist = album_data[2]
            art_url = album_data[3] if len(album_data) > 3 else ""

            # Switch the view to the Queue tab so you can see the rating screen
            self.tabs.set("Queued Albums")

            # Call the correct function that loads the album tracks into the frame
            self.after(200, lambda:self.load_album_for_rating(album_id, album_name, artist, art_url))

        except Exception as e:
            print(f"Could not auto-open rating popup: {e}")

    def load_image_async(self, label_widget, url, size):
        # Sets a placeholder
        label_widget.configure(text="Loading...")

        def fetch_and_update():
            try:
                img_data = requests.get(url).content
                img_item = Image.open(BytesIO(img_data))
                ctk_img = ctk.CTkImage(light_image=img_item, dark_image=img_item, size=size)
                # Safely tell the main thread to update the image
                self.after(0, lambda: label_widget.configure(image=ctk_img, text=""))
            except:
                self.after(0, lambda: label_widget.configure(text="No Art"))

        # Run the download in the background
        threading.Thread(target=fetch_and_update, daemon=True).start()