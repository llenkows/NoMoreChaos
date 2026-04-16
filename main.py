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
        self.btn_home = self.create_nav_btn("Home", command=self.show_home_page)
        self.btn_jobs = self.create_nav_btn("Job Applications", command=self.show_jobs_page)
        self.btn_videos = self.create_nav_btn("Video Ideas", command=self.show_videos_page)
        self.btn_music = self.create_nav_btn("Music", command=self.show_music_page)
        self.btn_movies = self.create_nav_btn("Movies", command=self.show_movies_page)
        self.btn_sports = self.create_nav_btn("Sports", command=self.show_sports_page)

        # --- MAIN CONTENT AREA ---
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        # Track current page widget to destroy it when switching pages
        self.current_page = None

        # Load default page
        self.show_home_page()

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

    def show_home_page(self):
        self.clear_main_content()
        self.current_page = HomePage(self.main_content, self.db)
        self.current_page.pack(fill="both", expand=True)

    def show_jobs_page(self):
        self.clear_main_content()
        self.current_page = JobsPage(self.main_content, self.db)
        self.current_page.pack(fill="both", expand=True)

    def show_videos_page(self):
        self.clear_main_content()
        self.current_page = VideosPage(self.main_content, self.db)
        self.current_page.pack(fill="both", expand=True)

    def show_music_page(self):
        self.clear_main_content()
        self.current_page = MusicPage(self.main_content, self.db)
        self.current_page.pack(fill="both", expand=True)

    def show_movies_page(self):
        self.clear_main_content()
        self.current_page = MoviesPage(self.main_content, self.db)
        self.current_page.pack(fill="both", expand=True)

    def show_sports_page(self):
        self.clear_main_content()
        self.current_page = SportsPage(self.main_content, self.db)
        self.current_page.pack(fill="both", expand=True)

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

if __name__ == "__main__":
    app = ChaosApp()
    app.mainloop()