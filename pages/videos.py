import customtkinter as ctk


class VideosPage(ctk.CTkFrame):
    def __init__(self, parent, db_manager, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.db = db_manager

        self.bg_color = "#000000"
        self.card_color = "#121212"
        self.neon_green = "#39FF14"
        self.dark_green = "#2ce00f"
        self.sub_card_color = "#1E1E1E"  # Lighter color for subgames

        self.build_ui()

    def build_ui(self):
        title = ctk.CTkLabel(self, text="Video Ideas", font=("Arial", 28, "bold"), text_color="white")
        title.pack(anchor="w", pady=(0, 10))

        # --- ADD VIDEO FORM ---
        form_frame = ctk.CTkFrame(self, fg_color=self.card_color, corner_radius=10)
        form_frame.pack(fill="x", pady=(0, 20), ipadx=10, ipady=10)

        row1 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5, padx=10)

        self.entry_topic = ctk.CTkEntry(row1, placeholder_text="Video Topic / Game Name", width=300)
        self.entry_topic.pack(side="left", padx=(0, 10))

        self.menu_type = ctk.CTkOptionMenu(row1, values=["Single Game", "Multi-Game"],
                                           fg_color="#333333", button_color=self.neon_green,
                                           button_hover_color=self.dark_green, text_color="white",
                                           command=self.toggle_inputs)
        self.menu_type.pack(side="left", padx=(0, 10))

        self.row2 = ctk.CTkFrame(form_frame, fg_color="transparent")
        self.row2.pack(fill="x", pady=5, padx=10)

        self.entry_score = ctk.CTkEntry(self.row2, placeholder_text="Strength Score (0-100)", width=150)
        self.entry_score.pack(side="left", padx=(0, 10))

        self.entry_ttb = ctk.CTkEntry(self.row2, placeholder_text="Time to Beat (e.g. 15h)", width=140)
        self.entry_ttb.pack(side="left", padx=(0, 10))

        self.lbl_subcount = ctk.CTkLabel(self.row2, text="Auto-Create Subgames:", text_color="white",
                                         font=("Arial", 14, "bold"))
        self.entry_subcount = ctk.CTkEntry(self.row2, placeholder_text="e.g. 5")
        self.entry_subcount = ctk.CTkEntry(self.row2, placeholder_text="Qty", width=60)
        self.entry_subcount.insert(0, "0")
        self.lbl_subdesc = ctk.CTkLabel(self.row2, text="(Generates blank templates)", text_color="#AAAAAA",
                                        font=("Arial", 12, "italic"))

        self.add_btn = ctk.CTkButton(self.row2, text="+ Add Video Idea", fg_color=self.neon_green, text_color="black",
                                     hover_color=self.dark_green, font=("Arial", 14, "bold"),
                                     command=self.handle_add_video)
        self.toggle_inputs(self.menu_type.get())
        self.add_btn.pack(side="left")

        # --- TABS ---
        self.tabs = ctk.CTkTabview(self, fg_color="transparent", segmented_button_selected_color=self.neon_green,
                                   segmented_button_selected_hover_color=self.dark_green, text_color="white")
        self.tabs.pack(fill="both", expand=True)

        self.tab_pending = self.tabs.add("Pending Ideas")
        self.tab_ready = self.tabs.add("Ready to Make Videos")

        self.pending_list = ctk.CTkScrollableFrame(self.tab_pending, fg_color="transparent")
        self.pending_list.pack(fill="both", expand=True)

        self.ready_list = ctk.CTkScrollableFrame(self.tab_ready, fg_color="transparent")
        self.ready_list.pack(fill="both", expand=True)

        self.refresh_video_lists()

    # --- ACTION HANDLERS ---
    def toggle_inputs(self, choice):
        # 1. Hide everything in the row first
        self.entry_score.pack_forget()
        self.entry_ttb.pack_forget()
        self.lbl_subcount.pack_forget()
        self.entry_subcount.pack_forget()
        self.lbl_subdesc.pack_forget()
        self.add_btn.pack_forget()

        # 2. Put them back based on the choice
        if choice == "Multi-Game":
            self.add_btn.pack(side="left")
            self.entry_subcount.pack(side="left", padx=(0, 10))
            self.lbl_subdesc.pack(side="left", padx=(0, 15))
            self.add_btn.pack(side="left")
        else:
            # Pack all three in the correct order
            self.entry_score.pack(side="left", padx=(0, 10))
            self.entry_ttb.pack(side="left", padx=(0, 10))
            self.add_btn.pack(side="left")

    def handle_add_video(self):
        topic = self.entry_topic.get()
        v_type = self.menu_type.get()
        sub_count = 0

        if topic:
            if v_type == "Single Game":
                score = self.entry_score.get()
                score = int(score) if score.isdigit() else 0
                score = min(score, 100)
                ttb = self.entry_ttb.get()
            else:
                # Multi-Game starts with 0 score and blank TTB
                score = 0
                ttb = ""
                try:
                    sub_count = int(self.entry_subcount.get())
                except ValueError:
                    sub_count = 0

            self.db.add_video(topic, v_type, score, ttb, subgame_count=sub_count)
            self.entry_topic.delete(0, 'end')
            self.entry_score.delete(0, 'end')
            self.entry_ttb.delete(0, 'end')
            self.refresh_video_lists()

    def handle_delete_video(self, video_id):
        self.db.delete_video(video_id)
        self.refresh_video_lists()

    def handle_move_to_ready(self, video_id):
        self.db.update_video_ready_status(video_id, 1)
        self.refresh_video_lists()

    def handle_subtopic_ready(self, sub_id, video_id):
        self.db.update_subtopic_ready(sub_id, video_id)
        self.refresh_video_lists()  # Refresh to see if parent moved

    def handle_delete_subtopic(self, sub_id, video_id):
        self.db.delete_subtopic(sub_id, video_id)
        self.refresh_video_lists()

    # --- POPUPS ---
    def open_add_subgame_popup(self, video_id):
        popup = ctk.CTkToplevel(self)
        popup.title("Add Subgame")
        popup.geometry("350x250")
        popup.attributes("-topmost", True)
        popup.configure(fg_color=self.bg_color)

        lbl = ctk.CTkLabel(popup, text="Add Game to Topic", font=("Arial", 18, "bold"), text_color="white")
        lbl.pack(pady=(20, 10))

        entry_name = ctk.CTkEntry(popup, placeholder_text="Game Name", width=250)
        entry_name.pack(pady=5)

        entry_score = ctk.CTkEntry(popup, placeholder_text="Score (0-100)", width=250)
        entry_score.pack(pady=5)

        entry_ttb = ctk.CTkEntry(popup, placeholder_text="Time to Beat", width=250)
        entry_ttb.pack(pady=5)

        def save_subgame():
            score = entry_score.get()
            score = int(score) if score.isdigit() else 0
            score = min(score, 100)
            if entry_name.get():
                self.db.add_subtopic(video_id, entry_name.get(), score, entry_ttb.get())
                popup.destroy()
                self.refresh_video_lists()

        btn_save = ctk.CTkButton(popup, text="Add Game", fg_color=self.neon_green, text_color="black",
                                 hover_color=self.dark_green, font=("Arial", 14, "bold"), command=save_subgame)
        btn_save.pack(pady=15)

    def confirm_complete_popup(self, video_id, topic_name):
        popup = ctk.CTkToplevel(self)
        popup.title("Complete Video")
        popup.geometry("350x150")
        popup.attributes("-topmost", True)
        popup.configure(fg_color=self.bg_color)

        lbl = ctk.CTkLabel(popup, text=f"Did you finish making:\n{topic_name}?", font=("Arial", 16), text_color="white")
        lbl.pack(pady=(25, 15))

        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(fill="x")

        btn_yes = ctk.CTkButton(btn_frame, text="Yes, Remove It", width=120, fg_color=self.neon_green,
                                text_color="black", hover_color=self.dark_green,
                                command=lambda: [self.handle_delete_video(video_id), popup.destroy()])
        btn_yes.pack(side="left", padx=(25, 10))
        btn_no = ctk.CTkButton(btn_frame, text="Cancel", width=120, fg_color="#333333", hover_color="#555555",
                               command=popup.destroy)
        btn_no.pack(side="right", padx=(10, 25))

    # --- RENDER LISTS ---
        # --- RENDER LISTS ---
    def refresh_video_lists(self):
        # 1. Save scroll positions for BOTH lists
        try:
            pending_scroll = self.pending_list._parent_canvas.yview()
        except:
            pending_scroll = (0.0, 0.0)

        try:
            ready_scroll = self.ready_list._parent_canvas.yview()
        except:
            ready_scroll = (0.0, 0.0)

        # 2. Clear existing widgets
        for widget in self.pending_list.winfo_children(): widget.destroy()
        for widget in self.ready_list.winfo_children(): widget.destroy()

        # 3. Re-draw Pending Videos
        pending_videos = self.db.get_videos(is_ready=0)
        for vid in pending_videos:
            self.create_video_card(vid, self.pending_list)

        # 4. Re-draw Ready Videos
        ready_videos = self.db.get_videos(is_ready=1)
        for vid in ready_videos:
            self.create_video_card(vid, self.ready_list)

        # 5. Restore scroll positions safely!
        self.after(50, lambda: self.pending_list._parent_canvas.yview_moveto(pending_scroll[0]))
        self.after(50, lambda: self.ready_list._parent_canvas.yview_moveto(ready_scroll[0]))

    def create_video_card(self, video_data, parent_frame):
        vid_id, topic, v_type, score, ttb, is_ready, is_completed = video_data

        card = ctk.CTkFrame(parent_frame, fg_color=self.card_color, corner_radius=10)
        card.pack(fill="x", pady=5)

        # Header Row
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", pady=10, padx=10)

        info_text = f"[{score}/100] {topic}  |  {v_type}"
        if v_type == "Single Game":
            info_text += f"  |  TTB: {ttb}"

        lbl_info = ctk.CTkLabel(header, text=info_text, font=("Arial", 16, "bold"), text_color="white")
        lbl_info.pack(side="left", padx=10)

        controls = ctk.CTkFrame(header, fg_color="transparent")
        controls.pack(side="right", padx=10)

        # Multi-Game Specific "Add Subgame" Button
        if v_type == "Multi-Game" and is_ready == 0:
            btn_add = ctk.CTkButton(controls, text="+ Add Game", width=80, fg_color="#444444", hover_color="#666666",
                                    command=lambda v=vid_id: self.open_add_subgame_popup(v))
            btn_add.pack(side="left", padx=(0, 10))

        if is_ready == 0 and v_type == "Single Game":
            btn_move = ctk.CTkButton(controls, text="Move to Ready ➔", width=120, fg_color="#1E90FF",
                                     hover_color="#0000CD",
                                     command=lambda v=vid_id: self.handle_move_to_ready(v))
            btn_move.pack(side="left", padx=(0, 10))
            btn_edit_vid = ctk.CTkButton(card, text="Edit", width=60, fg_color="#333333",
                                         command=lambda v=vid_id, t=topic, vt=v_type, sc=score,
                                                        tb=ttb: self.open_edit_video(v, t, vt, sc, tb))
            btn_edit_vid.pack(side="right", padx=5)
        elif is_ready == 1:
            btn_complete = ctk.CTkButton(controls, text="Complete ✓", width=100, fg_color=self.neon_green,
                                         text_color="black", hover_color=self.dark_green,
                                         command=lambda v=vid_id, t=topic: self.confirm_complete_popup(v, t))
            btn_complete.pack(side="left", padx=(0, 10))

        btn_delete = ctk.CTkButton(controls, text="X", width=30, fg_color="#FF3333", hover_color="#990000",
                                   text_color="white",
                                   command=lambda v=vid_id: self.handle_delete_video(v))
        btn_delete.pack(side="left")

        # --- RENDER SUBGAMES (If Multi-Game) ---
        if v_type == "Multi-Game":
            subgames = self.db.get_subtopics(vid_id)
            if subgames:
                sub_container = ctk.CTkFrame(card, fg_color="transparent")
                sub_container.pack(fill="x", padx=40, pady=(0, 15))  # Indented container

                for sub in subgames:
                    sub_id, name, sub_score, sub_ttb, sub_ready = sub

                    sub_row = ctk.CTkFrame(sub_container, fg_color=self.sub_card_color, corner_radius=5)
                    sub_row.pack(fill="x", pady=3)

                    # Strike through name if ready
                    display_name = f"{name} (Ready)" if sub_ready else name
                    sub_text = f"[{sub_score}/100]  {display_name}  |  TTB: {sub_ttb}"
                    color = "#888888" if sub_ready else "#CCCCCC"

                    lbl_sub = ctk.CTkLabel(sub_row, text=sub_text, font=("Arial", 14), text_color=color)
                    lbl_sub.pack(side="left", padx=15, pady=5)

                    sub_controls = ctk.CTkFrame(sub_row, fg_color="transparent")
                    sub_controls.pack(side="right", padx=10)

                    if not sub_ready:
                        btn_ready = ctk.CTkButton(sub_controls, text="Mark Ready", width=80, fg_color="#1E90FF",
                                                  hover_color="#0000CD",
                                                  command=lambda s=sub_id, v=vid_id: self.handle_subtopic_ready(s, v))
                        btn_ready.pack(side="left", padx=(0, 5))

                        # NEW: The missing Edit button and pack command
                        btn_edit_sub = ctk.CTkButton(sub_controls, text="✏️ Edit", width=60, fg_color="#333333",
                                                     command=lambda sid=sub_id, vid=vid_id, n=name, sc=sub_score,
                                                                    tb=sub_ttb: self.open_edit_subtopic(sid, vid, n, sc,
                                                                                                        tb))
                        btn_edit_sub.pack(side="left", padx=(0, 5))
                    else:
                        btn_unready = ctk.CTkButton(sub_controls, text="↩️ Unready", width=80, fg_color="#FF8800",
                                                    hover_color="#CC6600",
                                                    command=lambda sid=sub_id, vid=vid_id: self.unready_subtopic(sid,
                                                                                                                 vid))
                        # FIX: This pack command was missing!
                        btn_unready.pack(side="left", padx=(0, 5))

                    btn_del_sub = ctk.CTkButton(sub_controls, text="X", width=30, fg_color="#FF3333",
                                                hover_color="#990000", text_color="white",
                                                command=lambda s=sub_id, v=vid_id: self.handle_delete_subtopic(s, v))
                    btn_del_sub.pack(side="left")

    # EDIT & UNREADY LOGIC
    def unready_subtopic(self, sub_id, video_id):
        self.db.unready_subtopic(sub_id, video_id)
        self.refresh_video_lists()

    def open_edit_video(self, vid_id, current_topic, current_type, current_score, current_ttb):
        edit_win = ctk.CTkToplevel(self)
        edit_win.title("Edit Video")
        edit_win.geometry("400x450")
        edit_win.attributes("-topmost", True)

        ctk.CTkLabel(edit_win, text="Topic:").pack(pady=(10, 0))
        topic_ent = ctk.CTkEntry(edit_win, width=300)
        topic_ent.pack()
        topic_ent.insert(0, current_topic)

        ctk.CTkLabel(edit_win, text="Score (1-10):").pack(pady=(10, 0))
        score_ent = ctk.CTkEntry(edit_win, width=300)
        score_ent.pack()
        score_ent.insert(0, str(current_score))

        ctk.CTkLabel(edit_win, text="Time to Beat:").pack(pady=(10, 0))
        ttb_ent = ctk.CTkEntry(edit_win, width=300)
        ttb_ent.pack()
        ttb_ent.insert(0, current_ttb)

        def save_edits():
            self.db.update_video_details(vid_id, topic_ent.get(), current_type, int(score_ent.get() or 0), ttb_ent.get())
            edit_win.destroy()
            self.refresh_video_lists()

        ctk.CTkButton(edit_win, text="Save Changes", fg_color=self.neon_green, text_color="black", command=save_edits).pack(pady=20)

    def open_edit_subtopic(self, sub_id, video_id, current_name, current_score, current_ttb):
        edit_win = ctk.CTkToplevel(self)
        edit_win.title("Edit Subgame")
        edit_win.geometry("400x400")
        edit_win.attributes("-topmost", True)

        ctk.CTkLabel(edit_win, text="Subgame Name:").pack(pady=(10, 0))
        name_ent = ctk.CTkEntry(edit_win, width=300)
        name_ent.pack()
        name_ent.insert(0, current_name)

        ctk.CTkLabel(edit_win, text="Score (1-10):").pack(pady=(10, 0))
        score_ent = ctk.CTkEntry(edit_win, width=300)
        score_ent.pack()
        score_ent.insert(0, str(current_score))

        ctk.CTkLabel(edit_win, text="Time to Beat:").pack(pady=(10, 0))
        ttb_ent = ctk.CTkEntry(edit_win, width=300)
        ttb_ent.pack()
        ttb_ent.insert(0, current_ttb)

        def save_edits():
            self.db.update_subtopic_details(sub_id, name_ent.get(), int(score_ent.get() or 0), ttb_ent.get())
            self.db.sync_parent_multi_game(video_id) # Syncs the new max score to the parent!
            edit_win.destroy()
            self.refresh_video_lists()

        ctk.CTkButton(edit_win, text="Save Subgame", fg_color=self.neon_green, text_color="black", command=save_edits).pack(pady=20)