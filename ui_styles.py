import customtkinter as ctk


class NeonApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("NoMoreChaos")
        self.geometry("1100x600")

        # Color Palette: Neon Green and Black
        self.bg_color = "#000000"
        self.neon_green = "#39FF14"

        ctk.set_appearance_mode("dark")

        # Create Navigation Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="#121212")
        self.sidebar.pack(side="left", fill="y")

        self.logo_label = ctk.CTkLabel(self.sidebar, text="NOMORECHAOS",
                                       font=ctk.CTkFont(size=20, weight="bold"),
                                       text_color=self.neon_green)
        self.logo_label.pack(pady=20)

        # Buttons for your pages
        self.btn_home = self.create_nav_btn("Home")
        self.btn_jobs = self.create_nav_btn("Job Applications")
        self.btn_videos = self.create_nav_btn("Video Ideas")
        self.btn_music = self.create_nav_btn("Music")
        self.btn_movies = self.create_nav_btn("Movies")
        self.btn_sports = self.create_nav_btn("Sports")

    def create_nav_btn(self, name):
        btn = ctk.CTkButton(self.sidebar, text=name, fg_color="transparent",
                            text_color="white", hover_color="#222222",
                            anchor="w", border_spacing=10)
        btn.pack(fill="x", padx=10, pady=5)
        return btn


if __name__ == "__main__":
    app = NeonApp()
    app.mainloop()