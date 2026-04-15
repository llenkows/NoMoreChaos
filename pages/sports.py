import customtkinter as ctk
import requests
import threading
from dateutil import parser
from datetime import datetime, timedelta

class SportsPage(ctk.CTkFrame):
    def __init__(self, parent, db_manager, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.db = db_manager

        self.bg_color = "#000000"
        self.card_color = "#121212"
        self.neon_green = "#39FF14"
        self.philly_teams = ["Philadelphia Eagles", "Philadelphia Phillies", "Philadelphia 76ers",
                             "Philadelphia Flyers", "Philadelphia Union"]

        self.build_ui()

    def build_ui(self):
        title = ctk.CTkLabel(self, text="Sports Calendar", font=("Arial", 28, "bold"), text_color="white")
        title.pack(anchor="w", pady=(0, 10))

        # SYNC ROW
        sync_frame = ctk.CTkFrame(self, fg_color=self.card_color, corner_radius=10)
        sync_frame.pack(fill="x", pady=(0, 20), ipadx=10, ipady=10)

        self.btn_sync = ctk.CTkButton(sync_frame, text="Sync ESPN Schedule (7 Days)", width=250,
                                      fg_color=self.neon_green, text_color="black",
                                      hover_color="#2ce00f", font=("Arial", 14, "bold"),
                                      command=self.start_sync_thread)

        self.btn_sync.pack(side="left", padx=10)

        self.lbl_status = ctk.CTkLabel(sync_frame, text="Click to fetch the latest schedules.", text_color="#AAAAAA")
        self.lbl_status.pack(side="left", padx=15)

        # SCHEDULE DISPLAY
        self.schedule_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.schedule_frame.pack(fill="both", expand=True)

        self.refresh_schedule_list()

    def start_sync_thread(self):
        self.btn_sync.configure(state="disabled", text="Syncing ESPN...")
        self.lbl_status.configure(text="Fetching live data...", text_color=self.neon_green)
        threading.Thread(target=self.sync_espn_data, daemon=True).start()

    def sync_espn_data(self):
        try:
            self.db.clear_old_games()

            today = datetime.now()
            next_week = today + timedelta(days=7)
            # ESPN requires dates in YYYYMMDD format (e.g., 20260415-20260422)
            date_range = f"{today.strftime('%Y%m%d')}-{next_week.strftime('%Y%m%d')}"

            leagues = {
                "NFL": "football/nfl",
                "NBA": "basketball/nba",
                "MLB": "baseball/mlb",
                "NHL": "hockey/nhl",
                "MLS": "soccer/usa.1"
            }

            games_found = 0

            for league_name, endpoint in leagues.items():
                self.lbl_status.configure(text=f"Fetching {league_name}...")

                url = f"https://site.api.espn.com/apis/site/v2/sports/{endpoint}/scoreboard?dates={date_range}&limit=500"

                response = requests.get(url).json()
                events = response.get('events', [])

                for event in events:
                    game_id = event['id']
                    start_time = event['date']

                    competitors = event['competitions'][0]['competitors']
                    home_team = next(
                        (team['team']['displayName'] for team in competitors if team['homeAway'] == 'home'),
                        "Unknown Home")
                    away_team = next(
                        (team['team']['displayName'] for team in competitors if team['homeAway'] == 'away'),
                        "Unknown Away")

                    is_philly = any(pt in home_team or pt in away_team for pt in self.philly_teams)
                    is_nfl = (league_name == "NFL")
                    is_playoffs = event.get('season', {}).get('type') == 3

                    notes = event['competitions'][0].get('notes', [])
                    notes = event['competitions'][0].get('notes', [])
                    is_playoff_note = any("game" in n.get('headline', '').lower() or
                                          "round" in n.get('headline', '').lower() or
                                          "play-in" in n.get('headline', '').lower()
                                          for n in notes)

                    if is_philly or is_nfl or is_playoffs or is_playoff_note:
                        self.db.save_sports_game(game_id, league_name, home_team, away_team, start_time)
                        games_found += 1

            self.lbl_status.configure(text=f"Success! {games_found} relevant games synced.", text_color=self.neon_green)
        except Exception as e:
            self.lbl_status.configure(text="Error syncing sports data.", text_color="#FF3333")
            print(f"ESPN Sync Error: {e}")
        finally:
            # Tell the MAIN thread to safely handle the UI updates and widget destruction
            self.after(0, self.finish_sync_ui)

    def refresh_schedule_list(self):
        for widget in self.schedule_frame.winfo_children(): widget.destroy()

        games = self.db.get_upcoming_games()
        if not games:
            ctk.CTkLabel(self.schedule_frame, text="No games scheduled. Hit Sync!", text_color="#555555").pack(pady=20)
            return

        for game in games:
            g_id, league, home, away, start_utc, notified = game

            # Convert UTC string to local computer time for display
            try:
                dt_utc = parser.isoparse(start_utc)
                dt_local = dt_utc.astimezone()
                time_str = dt_local.strftime("%A, %b %d @ %I:%M %p")
            except:
                time_str = start_utc

            # Highlight card if it features a Philly team
            is_philly = any(pt in home or pt in away for pt in self.philly_teams)
            card_color = "#1A2B1A" if is_philly else self.card_color  # Slight green tint for Philly
            text_color = self.neon_green if is_philly else "white"

            card = ctk.CTkFrame(self.schedule_frame, fg_color=card_color, corner_radius=8)
            card.pack(fill="x", pady=5, padx=5)

            ctk.CTkLabel(card, text=f"{league}", font=("Arial", 14, "bold"), text_color="#888888", width=50).pack(
                side="left", padx=15, pady=15)
            ctk.CTkLabel(card, text=f"{away} @ {home}", font=("Arial", 16, "bold"), text_color=text_color).pack(
                side="left", padx=10)
            ctk.CTkLabel(card, text=time_str, font=("Arial", 14), text_color="#AAAAAA").pack(side="right", padx=20)

    def finish_sync_ui(self):
        self.btn_sync.configure(state="normal", text="Sync ESPN Schedule (7 Days)")
        self.refresh_schedule_list()