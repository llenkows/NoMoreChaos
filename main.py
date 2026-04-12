import customtkinter as ctk
from database import DatabaseManager
from pages.jobs import JobsPage


class ChaosApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Init Database
        self.db = DatabaseManager()

        # Window Setup
        self.title("No More Chaos")
        self.geometry("900x600")
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
        self.btn_jobs = self.create_nav_btn("Job Applications", command=self.show_jobs_page)
        self.btn_videos = self.create_nav_btn("Video Ideas", command=None)  # Placeholder for next page

        # --- MAIN CONTENT AREA ---
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        # Track current page widget to destroy it when switching pages
        self.current_page = None

        # Load default page
        self.show_jobs_page()

    def create_nav_btn(self, name, command):
        btn = ctk.CTkButton(self.sidebar, text=name, fg_color="transparent", text_color="white",
                            hover_color="#1e1e1e", anchor="w", border_spacing=10, command=command)
        btn.pack(fill="x", padx=10, pady=5)
        return btn

    # --- PAGE ROUTING ---
    def clear_main_content(self):
        if self.current_page is not None:
            self.current_page.destroy()

    def show_jobs_page(self):
        self.clear_main_content()
        # Create the JobsPage widget and pass it the main_content area and the database
        self.current_page = JobsPage(self.main_content, self.db)
        self.current_page.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = ChaosApp()
    app.mainloop()