import customtkinter as ctk


class JobsPage(ctk.CTkFrame):
    def __init__(self, parent, db_manager, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.db = db_manager  # Save a reference to the database

        # UI Colors (inherited from main app)
        self.bg_color = "#000000"
        self.card_color = "#121212"
        self.neon_green = "#39FF14"
        self.dark_green = "#2ce00f"

        self.build_ui()

    def build_ui(self):
        title = ctk.CTkLabel(self, text="Job Applications", font=("Arial", 28, "bold"), text_color="white")
        title.pack(anchor="w", pady=(0, 20))

        # Add Job Form Area
        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.pack(fill="x", pady=(0, 20))

        self.entry_company = ctk.CTkEntry(form_frame, placeholder_text="Company Name", width=250)
        self.entry_company.pack(side="left", padx=(0, 10))

        self.entry_role = ctk.CTkEntry(form_frame, placeholder_text="Job Role", width=250)
        self.entry_role.pack(side="left", padx=(0, 10))

        add_btn = ctk.CTkButton(form_frame, text="+ Add Job", fg_color=self.neon_green, text_color="black",
                                hover_color=self.dark_green, font=("Arial", 14, "bold"), command=self.handle_add_job)
        add_btn.pack(side="left")

        # Scrollable Job List Area
        self.job_list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.job_list_frame.pack(fill="both", expand=True)

        self.refresh_job_list()

    # --- ACTION HANDLERS ---
    def handle_add_job(self):
        company = self.entry_company.get()
        role = self.entry_role.get()
        if company and role:
            self.db.add_job(company, role)
            self.entry_company.delete(0, 'end')
            self.entry_role.delete(0, 'end')
            self.refresh_job_list()

    def handle_status_change(self, new_status, job_id):
        self.db.update_job_status(job_id, new_status)

    def handle_delete_job(self, job_id):
        self.db.delete_job(job_id)
        self.refresh_job_list()

    def confirm_delete_popup(self, job_id, company_name):
        popup = ctk.CTkToplevel(self)
        popup.title("Confirm Deletion")
        popup.geometry("320x150")
        popup.attributes("-topmost", True)
        popup.configure(fg_color=self.bg_color)

        lbl = ctk.CTkLabel(popup, text=f"Are you sure you want to delete\n{company_name}?", font=("Arial", 16),
                           text_color="white")
        lbl.pack(pady=(25, 15))

        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(fill="x")

        btn_yes = ctk.CTkButton(btn_frame, text="Yes, Delete", width=120, fg_color="#FF3333", hover_color="#990000",
                                command=lambda: [self.handle_delete_job(job_id), popup.destroy()])
        btn_yes.pack(side="left", padx=(25, 10))

        btn_no = ctk.CTkButton(btn_frame, text="Cancel", width=120, fg_color="#333333", hover_color="#555555",
                               command=popup.destroy)
        btn_no.pack(side="right", padx=(10, 25))

    def open_edit_popup(self, job_id, current_company, current_role):
        popup = ctk.CTkToplevel(self)
        popup.title("Edit Job")
        popup.geometry("350x250")
        popup.attributes("-topmost", True)
        popup.configure(fg_color=self.bg_color)

        lbl = ctk.CTkLabel(popup, text="Edit Job Details", font=("Arial", 18, "bold"), text_color="white")
        lbl.pack(pady=(20, 10))

        entry_comp = ctk.CTkEntry(popup, width=250)
        entry_comp.insert(0, current_company)
        entry_comp.pack(pady=10)

        entry_rol = ctk.CTkEntry(popup, width=250)
        entry_rol.insert(0, current_role)
        entry_rol.pack(pady=10)

        def save_edits():
            self.db.update_job_details(job_id, entry_comp.get(), entry_rol.get())
            popup.destroy()
            self.refresh_job_list()

        btn_save = ctk.CTkButton(popup, text="Save Changes", fg_color=self.neon_green, text_color="black",
                                 hover_color=self.dark_green, font=("Arial", 14, "bold"), command=save_edits)
        btn_save.pack(pady=15)

    def refresh_job_list(self):
        for widget in self.job_list_frame.winfo_children():
            widget.destroy()

        jobs = self.db.get_jobs()

        for job in jobs:
            job_id, company, role, status, created_at = job

            card = ctk.CTkFrame(self.job_list_frame, fg_color=self.card_color, corner_radius=10)
            card.pack(fill="x", pady=5)

            lbl_details = ctk.CTkLabel(card, text=f"{company}  |  {role}", font=("Arial", 16, "bold"),
                                       text_color="white")
            lbl_details.pack(side="left", padx=20, pady=15)

            controls_frame = ctk.CTkFrame(card, fg_color="transparent")
            controls_frame.pack(side="right", padx=10, pady=15)

            status_menu = ctk.CTkOptionMenu(controls_frame,
                                            values=["Waiting", "Interviewing", "Got the Job", "Ghosted", "Denied"],
                                            fg_color=self.card_color, button_color=self.neon_green,
                                            button_hover_color=self.dark_green, text_color=self.neon_green,
                                            dropdown_fg_color=self.card_color, dropdown_text_color="white",
                                            dropdown_hover_color="#1e1e1e",
                                            command=lambda val, j_id=job_id: self.handle_status_change(val, j_id))
            status_menu.set(status)
            status_menu.pack(side="left", padx=(0, 10))

            btn_edit = ctk.CTkButton(controls_frame, text="Edit", width=60, fg_color="#333333", hover_color="#555555",
                                     command=lambda j_id=job_id, c=company, r=role: self.open_edit_popup(j_id, c, r))
            btn_edit.pack(side="left", padx=(0, 5))

            btn_delete = ctk.CTkButton(controls_frame, text="X", width=30, fg_color="#FF3333", hover_color="#990000",
                                       text_color="white", font=("Arial", 12, "bold"),
                                       command=lambda j_id=job_id, c=company: self.confirm_delete_popup(j_id, c))
            btn_delete.pack(side="left")