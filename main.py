import customtkinter as ctk
import os
from dotenv import load_dotenv

def resource_path(relative_path): # .env obscuring
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

load_dotenv(resource_path(".env"))
from database import DatabaseManager
from pages.jobs import JobsPage
from pages.videos import VideosPage
from pages.music import MusicPage
from pages.movies import MoviesPage
from pages.sports import SportsPage
import threading
import time
from plyer import notification
from dateutil import parser
from datetime import datetime, timezone, timedelta
from pages.home import HomePage
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
import sys



class ChaosApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Initialize Database
        self.db = DatabaseManager()

        # Window Setup
        self.title("No More Chaos")
        self.geometry("900x600")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        ctk.set_appearance_mode("dark")

        # Color Palette
        self.bg_color = "#000000"
        self.card_color = "#121212"
        self.neon_green = "#39FF14"

        self.configure(fg_color=self.bg_color)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=self.card_color)
        self.sidebar.pack(side="left", fill="y")

        self.logo = ctk.CTkLabel(self.sidebar, text="NO MORE\nCHAOS", font=("Arial", 20, "bold"),
                                 text_color=self.neon_green)
        self.logo.pack(pady=30)

        # Sidebar Buttons (Notice the commands!)
        self.btn_home = self.create_nav_btn("Home", command=lambda:self.show_page('home'))
        self.btn_jobs = self.create_nav_btn("Job Applications", command=lambda:self.show_page('jobs'))
        self.btn_videos = self.create_nav_btn("Video Ideas", command=lambda:self.show_page('videos'))
        self.btn_music = self.create_nav_btn("Music", command=lambda:self.show_page('music'))
        self.btn_movies = self.create_nav_btn("Movies", command=lambda:self.show_page('movies'))
        self.btn_sports = self.create_nav_btn("Sports", command=lambda:self.show_page('sports'))

        # --- MAIN CONTENT AREA ---
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        # Track current page widget to destroy it when switching pages
        self.current_page = None

        self.pages = {}
        self.pages['home'] = HomePage(self.main_content, self.db)
        self.pages['jobs'] = JobsPage(self.main_content, self.db)
        self.pages['videos'] = VideosPage(self.main_content, self.db)
        self.pages['music'] = MusicPage(self.main_content, self.db)
        self.pages['movies'] = MoviesPage(self.main_content, self.db)
        self.pages['sports'] = SportsPage(self.main_content, self.db)


        # Load default page
        self.show_page('home')

        # --- START SPORTS NOTIFICATION ENGINE ---
        threading.Thread(target=self.sports_notification_worker, daemon=True).start()

    def create_nav_btn(self, name, command):
        btn = ctk.CTkButton(self.sidebar, text=name, fg_color="transparent", text_color="white",
                            hover_color="#1e1e1e", anchor="w", border_spacing=10, command=command)
        btn.pack(fill="x", padx=10, pady=5)
        return btn

    # --- PAGE ROUTING ---
    def clear_main_content(self):
        if self.current_page is not None:
            self.current_page.destroy()

    def show_page(self, page_name, **kwargs):
        # 1. Hide all pages
        for page in self.pages.values():
            if page.winfo_ismapped():
                page.pack_forget()

        # 2. Force Tkinter to instantly clear the screen before doing heavy math!
        self.update_idletasks()

        # 3. Get the requested page
        page_to_show = self.pages[page_name]

        # 4. Show the new page empty first, so Tkinter knows its physical boundaries
        page_to_show.pack(fill="both", expand=True)

        # 5. Handle dashboard album routing
        if page_name == 'music' and 'auto_rate_album' in kwargs:
            page_to_show.trigger_dashboard_rating(kwargs['auto_rate_album'])

        # 6. Delay the heavy data refresh by 50ms so the UI finishes drawing the blank page first
        if hasattr(page_to_show, 'refresh_saved_list'):
            self.after(300, page_to_show.refresh_saved_list)
        elif hasattr(page_to_show, 'refresh_dashboard'):
            self.after(50, page_to_show.refresh_dashboard)

    def show_music_page(self, auto_rate_album=None):
        self.show_page('music')
        if auto_rate_album:
            self.pages['music'].trigger_dashboard_rating(auto_rate_album)

    # --- NOTIFICATION ENGINE ---
    def sports_notification_worker(self):
        while True:
            try:
                games = self.db.get_unnotified_games()
                now_utc = datetime.now(timezone.utc)

                for game in games:
                    g_id, league, home, away, start_utc, notified = game
                    game_time = parser.isoparse(start_utc)

                    time_diff = (game_time - now_utc).total_seconds()

                    # If game starts in exactly 15 minutes (900 seconds) or less, and hasn't started yet
                    if 0 < time_diff <= 900:
                        notification.notify(
                            title=f"{league} Alert: Game Starting!",
                            message=f"{away} @ {home} starts in 15 minutes.",
                            app_name="No More Chaos",
                            timeout=10
                        )
                        self.db.mark_game_notified(g_id)
            except Exception as e:
                print(f"Notification Engine Error: {e}")

            time.sleep(60)

    # ==========================================
    # CLOSING & SYSTEM TRAY LOGIC
    # ==========================================
    def on_closing(self):
        # Create a custom popup window
        self.close_window = ctk.CTkToplevel(self)
        self.close_window.title("Exit No More Chaos")
        self.close_window.geometry("400x150")
        self.close_window.attributes("-topmost", True)
        self.close_window.grab_set()

        ctk.CTkLabel(self.close_window, text="What would you like to do?", font=("Arial", 18, "bold")).pack(pady=20)

        btn_frame = ctk.CTkFrame(self.close_window, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)

        ctk.CTkButton(btn_frame, text="⏬ Minimize to Tray", command=self.minimize_to_tray).pack(side="left",
                                                                                                expand=True, padx=10)
        ctk.CTkButton(btn_frame, text="🚪 Quit & Backup", fg_color="#FF3333", hover_color="#CC0000",
                      command=self.quit_app).pack(side="right", expand=True, padx=10)

    def create_tray_icon(self):
        # Draw a simple neon green circle to serve as the tray icon
        image = Image.new('RGB', (64, 64), color=(0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.ellipse((10, 10, 54, 54), fill=(57, 255, 20))
        return image

    def minimize_to_tray(self):
        self.close_window.destroy()
        self.withdraw()  # Hides the main window from the taskbar

        # Setup system tray icon
        image = self.create_tray_icon()
        menu = (item('Open App', self.show_window_from_tray), item('Quit', self.quit_from_tray))
        self.tray_icon = pystray.Icon("NoMoreChaos", image, "No More Chaos", menu)

        # Run the tray icon in a background thread so it doesn't freeze Tkinter
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def show_window_from_tray(self, icon, item):
        icon.stop()
        # Bring the window back to the screen
        self.after(0, self.deiconify)

    def quit_from_tray(self, icon, item):
        icon.stop()
        self.after(0, self.quit_app)

    def quit_app(self):
        # Close the popup if it's open
        if hasattr(self, 'close_window') and self.close_window.winfo_exists():
            self.close_window.destroy()

        print("Backing up data to CSV...")
        self.db.backup_to_csv()

        print("Shutting down No More Chaos.")
        self.destroy()

    def show_music_page(self, auto_rate_album=None):
        self.clear_main_content()
        # Pass the auto_rate_album variable into the page when we create it
        self.current_page = MusicPage(self.main_content, self.db, auto_rate_album=auto_rate_album)
        self.current_page.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = ChaosApp()
    app.mainloop()