import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
import sqlite3

UNIFORM_FONT = ("Segoe UI", 10)

WHITE     = "#ffffff"
BLACK     = "#000000"
HEADER_BG = "#eae8f0"
ROW_ALT   = "#f7f6fb"
ROW_SEL   = "#dcd8f0"
BORDER    = "#dde0ee"
FG_DARK   = "#1a1a2e"
FG_MUTED  = "#9aa3c2"

font_color_sidebar = "white"
sidebar_color = "#8A5F41"
active_color  = "#A77F60"
content_color = "#F3E4C9"
black = "#070707"

DB_NAME = "dorm_management.db"

class Database:
    def get_all_cleaning_staff(self, cleaning_tree):
        for row in cleaning_tree.get_children():
            cleaning_tree.delete(row)
        with sqlite3.connect(DB_NAME) as connect:
            cursor = connect.cursor()
            cursor.execute("SELECT cs_ID, full_name, contact, email FROM cleaningStaff")
            for row in cursor.fetchall():
                cleaning_tree.insert("", "end", values=row)
            

    def insert_cleaning_staff(self, cs_ID, last, first, mi, email, contact, full_name):
        with sqlite3.connect(DB_NAME) as connect:
            cursor = connect.cursor()
            cursor.execute(
                "INSERT INTO cleaningStaff VALUES (?, ?, ?, ?, ?, ?, ?)",
                (cs_ID, last, first, mi, email, contact, full_name)
            )



class main(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("1200x650")
        self.minsize(1150, 650)
        self.title("Dormi Admin Panel")
        self.db = Database()

        self.all_pages   = []
        self.all_buttons = []

        self.build_layout()

    # ── Layout ────────────────────────────────────────────────────────
    def build_layout(self):
        # ── Sidebar ───────────────────────────────────────────────────
        self.sidebar = tk.Frame(self, bg=sidebar_color, width=300)      # self — referenced in show_page and sidebar buttons
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="Dormi", bg=sidebar_color, fg=font_color_sidebar,
                 font=("Arial", 14, "bold")).pack(anchor="w", padx=15, pady=(20, 0))
        tk.Label(self.sidebar, text="Admin panel", bg=sidebar_color, fg=font_color_sidebar,
                 font=("Arial", 9)).pack(anchor="w", padx=15, pady=(0, 20))

        # ── Content area ──────────────────────────────────────────────
        content = tk.Frame(self, bg=content_color)
        content.pack(side="left", fill="both", expand=True)

        # ── Pages ─────────────────────────────────────────────────────
        self.dashboard_page = tk.Frame(content, bg=content_color)       # self — passed into show_page
        self.students_page  = tk.Frame(content, bg=content_color)
        self.rooms_page     = tk.Frame(content, bg=content_color)
        self.cleaning_page  = tk.Frame(content, bg=content_color)
        self.settings_page  = tk.Frame(content, bg=content_color)

        self.build_dashboard_page(self.dashboard_page)
        self.build_students_page(self.students_page)
        self.build_rooms_page(self.rooms_page)
        self.build_cleaning_page(self.cleaning_page)
        self.build_settings_page(self.settings_page)

        self.all_pages = [
            self.dashboard_page, self.students_page, self.rooms_page,
            self.cleaning_page,  self.settings_page
        ]

        # ── Sidebar buttons ───────────────────────────────────────────
        tk.Label(self.sidebar, text="MAIN", bg=sidebar_color, fg=font_color_sidebar,
                 font=("Arial", 8)).pack(anchor="w", padx=15, pady=(5, 2))

        self.dashboardButton = tk.Button(self.sidebar, text="  Dashboard",   # self — highlight toggled in show_page
                                         bg=active_color, fg=font_color_sidebar,
                                         font=("Arial", 10), relief="flat",
                                         anchor="w", padx=10, pady=8, cursor="hand2")
        self.dashboardButton.pack(fill="x", padx=10, pady=2)

        tk.Label(self.sidebar, text="MANAGE", bg=sidebar_color, fg=font_color_sidebar,
                 font=("Arial", 8)).pack(anchor="w", padx=15, pady=(10, 2))

        self.studentButton = tk.Button(self.sidebar, text="  Students",
                                       bg=sidebar_color, fg=font_color_sidebar,
                                       font=("Arial", 10), relief="flat",
                                       anchor="w", padx=10, pady=8, cursor="hand2")
        self.studentButton.pack(fill="x", padx=10, pady=2)

        self.roomsButton = tk.Button(self.sidebar, text="  Rooms",
                                     bg=sidebar_color, fg=font_color_sidebar,
                                     font=("Arial", 10), relief="flat",
                                     anchor="w", padx=10, pady=8, cursor="hand2")
        self.roomsButton.pack(fill="x", padx=10, pady=2)

        self.cleaningButton = tk.Button(self.sidebar, text="  Cleaning staff",
                                        bg=sidebar_color, fg=font_color_sidebar,
                                        font=("Arial", 10), relief="flat",
                                        anchor="w", padx=10, pady=8, cursor="hand2")
        self.cleaningButton.pack(fill="x", padx=10, pady=2)

        self.Settings = tk.Button(self.sidebar, text="  Settings",
                                  bg=sidebar_color, fg=font_color_sidebar,
                                  font=("Arial", 10), relief="flat",
                                  anchor="w", padx=10, pady=8, cursor="hand2")
        self.Settings.pack(fill="x", padx=10, pady=2)

        self.all_buttons = [
            self.dashboardButton, self.studentButton, self.roomsButton,
            self.cleaningButton,  self.Settings
        ]

        self.dashboardButton.config(command=lambda: self.show_page(self.dashboard_page, self.dashboardButton))
        self.studentButton.config(  command=lambda: self.show_page(self.students_page,  self.studentButton))
        self.roomsButton.config(    command=lambda: self.show_page(self.rooms_page,     self.roomsButton))
        self.cleaningButton.config( command=lambda: self.show_page(self.cleaning_page,  self.cleaningButton))
        self.Settings.config(       command=lambda: self.show_page(self.settings_page,  self.Settings))

        self.show_page(self.dashboard_page, self.dashboardButton)

    # ── Navigation ────────────────────────────────────────────────────
    def show_page(self, page, active_btn):
        for p in self.all_pages:
            p.pack_forget()
        for btn in self.all_buttons:
            btn.config(bg=sidebar_color)
        page.pack(fill="both", expand=True)
        active_btn.config(bg=active_color)

    # ── Dashboard page ────────────────────────────────────────────────
    def build_dashboard_page(self, page):
        tk.Label(page, text="Dashboard", bg=content_color, fg="black",
                 font=("Arial", 16, "bold")).pack(anchor="w", pady=20, padx=20)

        cards_frame = tk.Frame(page, bg=content_color)
        cards_frame.pack(fill="x", padx=30, pady=10)

        totalstudents_Lframe = tk.LabelFrame(cards_frame, width=200, height=150, bg="white")
        totalstudents_Lframe.pack(side="left", padx=(0, 10), fill="x", expand=True)
        totalstudents_Lframe.pack_propagate(False)
        tk.Label(totalstudents_Lframe, text="🧑", font=("Arial", 24),
                 bg="white", fg="brown").pack(anchor="w", padx=10, pady=5)
        self.tsNum = tk.Label(totalstudents_Lframe, text="0",
                              font=("Arial", 24, "bold"), bg="white", fg="black")
        self.tsNum.pack(anchor="w", padx=10, pady=5)
        tk.Label(totalstudents_Lframe, text="Total students", font=("Arial", 15),
                 bg="white", fg="black").pack(anchor="w", padx=10, pady=(5, 0))

        totalrooms_Lframe = tk.LabelFrame(cards_frame, width=200, height=150, bg="white")
        totalrooms_Lframe.pack(side="left", padx=10, fill="x", expand=True)
        totalrooms_Lframe.pack_propagate(False)
        tk.Label(totalrooms_Lframe, text="🛏️", font=("Arial", 24),
                 bg="white", fg="Green").pack(anchor="w", padx=10, pady=5)
        self.trNum = tk.Label(totalrooms_Lframe, text="0",
                              font=("Arial", 24, "bold"), bg="white", fg="black")
        self.trNum.pack(anchor="w", padx=10, pady=5)
        tk.Label(totalrooms_Lframe, text="Total rooms", font=("Arial", 15),
                 bg="white", fg="black").pack(anchor="w", padx=10, pady=(5, 0))

        totalroomsoccupied_Lframe = tk.LabelFrame(cards_frame, width=200, height=150, bg="white")
        totalroomsoccupied_Lframe.pack(side="left", padx=10, fill="x", expand=True)
        totalroomsoccupied_Lframe.pack_propagate(False)
        tk.Label(totalroomsoccupied_Lframe, text="🛏️", font=("Arial", 24),
                 bg="white", fg="violet").pack(anchor="w", padx=10, pady=5)
        self.troNum = tk.Label(totalroomsoccupied_Lframe, text="0",
                               font=("Arial", 24, "bold"), bg="white", fg="black")
        self.troNum.pack(anchor="w", padx=10, pady=5)
        tk.Label(totalroomsoccupied_Lframe, text="Rooms occupied", font=("Arial", 15),
                 bg="white", fg="black").pack(anchor="w", padx=10, pady=(5, 0))

        totalcleaning_Lframe = tk.LabelFrame(cards_frame, width=200, height=150, bg="white")
        totalcleaning_Lframe.pack(side="left", padx=(10, 0), fill="x", expand=True)
        totalcleaning_Lframe.pack_propagate(False)
        tk.Label(totalcleaning_Lframe, text="🧹", font=("Arial", 24),
                 bg="white", fg="brown").pack(anchor="w", padx=10, pady=5)
        self.tcNum = tk.Label(totalcleaning_Lframe, text="0",
                              font=("Arial", 24, "bold"), bg="white", fg="black")
        self.tcNum.pack(anchor="w", padx=10, pady=5)
        tk.Label(totalcleaning_Lframe, text="Cleaning tasks", font=("Arial", 15),
                 bg="white", fg="black").pack(anchor="w", padx=10, pady=(5, 0))

        tk.Label(page, text="Recent student assignments", bg=content_color,
                 font=("Arial", 12, "bold"), fg="black").pack(anchor="w", pady=5, padx=30)

        self.treeStuAss = ttk.Treeview(page,
                                       columns=("Student", "Room", "Start Date", "Status"),
                                       show="headings")
        self.treeStuAss.heading("Student",    text="Student Name")
        self.treeStuAss.heading("Room",       text="Room")
        self.treeStuAss.heading("Start Date", text="Start Date")
        self.treeStuAss.heading("Status",     text="Status")
        self.treeStuAss.column("Student",    width=150)
        self.treeStuAss.column("Room",       width=50)
        self.treeStuAss.column("Start Date", width=75)
        self.treeStuAss.column("Status",     width=75)
        self.treeStuAss.pack(fill="both", padx=20, pady=10)

        tk.Label(page, text="Cleaning assignments today", bg=content_color,
                 font=("Arial", 12, "bold"), fg="black").pack(anchor="w", pady=5, padx=30)

        self.treeCleanAss = ttk.Treeview(page,
                                         columns=("ID", "StaffName", "Room", "TimeStart", "TimeEnd"),
                                         show="headings")
        self.treeCleanAss.heading("ID",        text="ID")
        self.treeCleanAss.heading("StaffName", text="Staff Name")
        self.treeCleanAss.heading("Room",      text="Room")
        self.treeCleanAss.heading("TimeStart", text="Time Start")
        self.treeCleanAss.heading("TimeEnd",   text="Time End")
        self.treeCleanAss.column("ID",        width=50)
        self.treeCleanAss.column("StaffName", width=150)
        self.treeCleanAss.column("Room",      width=50)
        self.treeCleanAss.column("TimeStart", width=75)
        self.treeCleanAss.column("TimeEnd",   width=75)
        self.treeCleanAss.pack(fill="both", padx=20, pady=10)

    # ── Students page ─────────────────────────────────────────────────
    def build_students_page(self, page):

        def add_student_window(prefill=None, edit_item=None):
            win = tk.Toplevel()
            win.title("Edit Student" if edit_item else "Add Student")
            win.config(bg=content_color)
            win.geometry("420x420")
            win.resizable(False, False)

            tk.Frame(win, bg=content_color)
            upperFrame = tk.Frame(win, bg=content_color)
            upperFrame.pack(fill="x", padx=15, pady=12)
            tk.Label(upperFrame,
                     text="Edit Student" if edit_item else "Add Student",
                     bg=content_color, fg=FG_DARK,
                     font=("Segoe UI", 15, "bold")).pack(side="left")

            midFrame = tk.Frame(win, bg=WHITE, padx=15, pady=15,
                                bd=1, relief="solid", highlightbackground=BORDER)
            midFrame.pack(fill="both", expand=True, padx=15, pady=5)
            midFrame.columnconfigure(0, weight=1)
            midFrame.columnconfigure(1, weight=1)

            tk.Label(midFrame, text="Student No.", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).grid(row=0, column=0, sticky="w", padx=(0,8), pady=(0,2))
            tk.Label(midFrame, text="Name", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).grid(row=0, column=1, sticky="w", pady=(0,2))

            def make_entry(parent, row, col, colspan=1, padx=(0,0)):
                border = tk.Frame(parent, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
                border.grid(row=row, column=col, columnspan=colspan, sticky="we",
                            padx=padx, pady=(0,10))
                e = tk.Entry(border, bg=WHITE, fg=BLACK, font=UNIFORM_FONT, relief="flat", bd=0)
                e.pack(fill="x", padx=5, pady=3)
                return e

            e_no      = make_entry(midFrame, 1, 0, padx=(0,8))
            e_name    = make_entry(midFrame, 1, 1)

            tk.Label(midFrame, text="Program", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).grid(row=2, column=0, sticky="w", padx=(0,8), pady=(0,2))
            tk.Label(midFrame, text="Room", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).grid(row=2, column=1, sticky="w", pady=(0,2))

            e_program = make_entry(midFrame, 3, 0, padx=(0,8))
            e_room    = make_entry(midFrame, 3, 1)

            tk.Label(midFrame, text="Status", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).grid(row=4, column=0, sticky="w", padx=(0,8), pady=(0,2))
            tk.Label(midFrame, text="Contact", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).grid(row=4, column=1, sticky="w", pady=(0,2))

            statusVar = tk.StringVar()
            statusDrop = ttk.Combobox(midFrame, textvariable=statusVar,
                                      values=["Active", "Inactive", "On Leave"],
                                      state="readonly", font=UNIFORM_FONT)
            statusDrop.grid(row=5, column=0, sticky="we", padx=(0,8), pady=(0,10))
            statusDrop.current(0)

            e_contact = make_entry(midFrame, 5, 1)

            if prefill:
                e_no.insert(0, prefill[0])
                e_name.insert(0, prefill[1])
                e_program.insert(0, prefill[2])
                e_room.insert(0, prefill[3])
                statusVar.set(prefill[4])
                e_contact.insert(0, prefill[5])

            err_label = tk.Label(win, text="", fg="#c0392b", bg=content_color, font=UNIFORM_FONT)
            err_label.pack()

            def save():
                no      = e_no.get().strip()
                name    = e_name.get().strip()
                program = e_program.get().strip()
                room    = e_room.get().strip()
                status  = statusVar.get()
                contact = e_contact.get().strip()

                if not no or not name:
                    err_label.config(text="Student No. and Name are required.")
                    return

                if edit_item:
                    self.tree.item(edit_item, values=(no, name, program, room, status, contact))
                else:
                    self.tree.insert("", "end", values=(no, name, program, room, status, contact))

                update_count()
                win.destroy()

            bottomFrame = tk.Frame(win, bg=content_color)
            bottomFrame.pack(fill="x", padx=15, pady=10)
            tk.Button(bottomFrame, text="Save", font=UNIFORM_FONT,
                      bg=BLACK, fg=WHITE, relief="flat", padx=12, pady=5,
                      cursor="hand2", command=save).pack(side="right", padx=(5,0))
            tk.Button(bottomFrame, text="Cancel", font=UNIFORM_FONT,
                      fg="#c0392b", relief="flat", padx=12, pady=5,
                      cursor="hand2", command=win.destroy).pack(side="right")

        def delete_student():
            selected = self.tree.selection()
            if not selected:
                messagebox_info("Select a student first.", "No Selection")
                return
            if messagebox_confirm("Delete this student? This cannot be undone."):
                self.tree.delete(selected[0])
                update_count()

        def edit_student():
            selected = self.tree.selection()
            if not selected:
                messagebox_info("Select a student first.", "No Selection")
                return
            values = self.tree.item(selected[0], "values")
            add_student_window(prefill=values, edit_item=selected[0])

        def assign_room():
            selected = self.tree.selection()
            if not selected:
                messagebox_info("Select a student first.", "No Selection")
                return
            values = self.tree.item(selected[0], "values")

            win = tk.Toplevel()
            win.title("Assign Room")
            win.config(bg=content_color)
            win.geometry("360x260")
            win.resizable(False, False)

            upperFrame = tk.Frame(win, bg=content_color)
            upperFrame.pack(fill="x", padx=15, pady=12)
            tk.Label(upperFrame, text="Assign Room", bg=content_color, fg=FG_DARK,
                     font=("Segoe UI", 15, "bold")).pack(side="left")

            midFrame = tk.Frame(win, bg=WHITE, padx=15, pady=15,
                                bd=1, relief="solid", highlightbackground=BORDER)
            midFrame.pack(fill="both", expand=True, padx=15, pady=5)
            midFrame.columnconfigure(0, weight=1)

            tk.Label(midFrame, text=f"Student:  {values[1]}", bg=WHITE, fg=FG_DARK,
                     font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", pady=(0,12))
            tk.Label(midFrame, text="Select Room", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).grid(row=1, column=0, sticky="w", pady=(0,4))

            roomVar = tk.StringVar()
            roomDrop = ttk.Combobox(midFrame, textvariable=roomVar,
                                    values=["101", "102", "103", "104", "105", "106"],
                                    state="readonly", font=UNIFORM_FONT)
            roomDrop.grid(row=2, column=0, sticky="we", pady=(0,12))
            if values[3]:
                roomDrop.set(values[3])
            else:
                roomDrop.current(0)

            tk.Label(midFrame, text="Status", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).grid(row=3, column=0, sticky="w", pady=(0,4))
            statusVar2 = tk.StringVar()
            statusDrop2 = ttk.Combobox(midFrame, textvariable=statusVar2,
                                       values=["Active", "Inactive", "On Leave"],
                                       state="readonly", font=UNIFORM_FONT)
            statusDrop2.grid(row=4, column=0, sticky="we")
            statusVar2.set(values[4] if values[4] else "Active")

            def save_room():
                new_vals = (values[0], values[1], values[2],
                            roomVar.get(), statusVar2.get(), values[5])
                self.tree.item(selected[0], values=new_vals)
                win.destroy()

            bottomFrame = tk.Frame(win, bg=content_color)
            bottomFrame.pack(fill="x", padx=15, pady=10)
            tk.Button(bottomFrame, text="Assign", font=UNIFORM_FONT,
                      bg=BLACK, fg=WHITE, relief="flat", padx=12, pady=5,
                      cursor="hand2", command=save_room).pack(side="right", padx=(5,0))
            tk.Button(bottomFrame, text="Cancel", font=UNIFORM_FONT,
                      fg="#c0392b", relief="flat", padx=12, pady=5,
                      cursor="hand2", command=win.destroy).pack(side="right")

        def messagebox_info(msg, title="Info"):
            win = tk.Toplevel()
            win.title(title)
            win.config(bg=WHITE)
            win.geometry("300x120")
            win.resizable(False, False)
            tk.Label(win, text=msg, bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT, wraplength=260).pack(pady=20)
            tk.Button(win, text="OK", bg=BLACK, fg=WHITE, font=UNIFORM_FONT,
                      relief="flat", padx=20, pady=4,
                      command=win.destroy).pack()

        def messagebox_confirm(msg):
            result = [False]
            win = tk.Toplevel()
            win.title("Confirm")
            win.config(bg=WHITE)
            win.geometry("320x130")
            win.resizable(False, False)
            tk.Label(win, text=msg, bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT, wraplength=280).pack(pady=16)
            btn_row = tk.Frame(win, bg=WHITE)
            btn_row.pack()
            def confirm():
                result[0] = True
                win.destroy()
            tk.Button(btn_row, text="Delete", bg="#c0392b", fg=WHITE, font=UNIFORM_FONT,
                      relief="flat", padx=14, pady=4,
                      cursor="hand2", command=confirm).pack(side="left", padx=6)
            tk.Button(btn_row, text="Cancel", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT,
                      relief="solid", bd=1, padx=14, pady=4,
                      cursor="hand2", command=win.destroy).pack(side="left", padx=6)
            win.grab_set()
            win.wait_window()
            return result[0]

        topbar = tk.Frame(page, bg=content_color)
        topbar.pack(fill="x", padx=28, pady=(20, 12))
        tk.Label(topbar, text="Students", bg=content_color, fg=FG_DARK,
                 font=("Segoe UI", 17, "bold")).pack(side="left")
        tk.Label(topbar, text="⋯", bg=content_color, fg=FG_DARK,
                 font=("Segoe UI", 13)).pack(side="right", padx=(6, 0))
        tk.Button(topbar, text="+ Add student", bg=WHITE, fg=FG_DARK,
                  font=UNIFORM_FONT, relief="solid", bd=1,
                  padx=12, pady=5, cursor="hand2",
                  command=add_student_window).pack(side="right")

        card = tk.Frame(page, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="both", expand=True, padx=28, pady=(0, 20))

        search_wrap = tk.Frame(card, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        search_wrap.pack(fill="x", padx=16, pady=(14, 10))
        tk.Label(search_wrap, text="🔍", bg=WHITE, fg=FG_MUTED,
                 font=UNIFORM_FONT).pack(side="left", padx=(8, 2), pady=6)
        search_entry = tk.Entry(search_wrap, bg=WHITE, fg=FG_MUTED,
                                font=UNIFORM_FONT, relief="flat", bd=0,
                                insertbackground=FG_DARK)
        search_entry.insert(0, "Search by name or student number...")
        search_entry.pack(side="left", fill="x", expand=True, pady=7, padx=4)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Students.Treeview", background=WHITE, foreground=FG_DARK,
                        rowheight=36, fieldbackground=WHITE, borderwidth=0, font=UNIFORM_FONT)
        style.configure("Students.Treeview.Heading", background=HEADER_BG, foreground="#555577",
                        font=("Segoe UI", 9, "bold"), relief="flat", padding=(8, 6))
        style.map("Students.Treeview",
                  background=[("selected", ROW_SEL)],
                  foreground=[("selected", FG_DARK)])
        style.layout("Students.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

        columns = ("student_no", "name", "program", "room", "status", "contact")
        tree_frame = tk.Frame(card, bg=WHITE)
        tree_frame.pack(fill="both", expand=True, padx=16)

        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                 style="Students.Treeview", selectmode="browse")
        col_cfg = [
            ("student_no", "Student no.", 120, "w"),
            ("name",       "Name",        190, "w"),
            ("program",    "Program",      85, "center"),
            ("room",       "Room",         70, "center"),
            ("status",     "Status",       95, "center"),
            ("contact",    "Contact",     120, "w"),
        ]
        for cid, heading, width, anchor in col_cfg:
            self.tree.heading(cid, text=heading, anchor=anchor)
            self.tree.column(cid,  width=width,  anchor=anchor, stretch=True)

        sample_students = [
            ("2021-0001", "Juan dela Cruz",   "BSCS",  "101", "Active",   "09171234567"),
            ("2021-0002", "Maria Santos",     "BSIT",  "102", "Active",   "09181234567"),
            ("2021-0003", "Jose Reyes",       "BSECE", "103", "On Leave", "09191234567"),
            ("2021-0004", "Ana Garcia",       "BSCS",  "104", "Active",   "09201234567"),
            ("2021-0005", "Pedro Villanueva", "BSIT",  "",    "Inactive", "09211234567"),
        ]
        for row in sample_students:
            self.tree.insert("", "end", values=row)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=16, pady=(6, 0))

        action_bar = tk.Frame(card, bg=WHITE)
        action_bar.pack(fill="x", padx=16, pady=10)

        self.count_label = tk.Label(action_bar, text="5 students", bg=WHITE,
                                    fg=FG_MUTED, font=UNIFORM_FONT)
        self.count_label.pack(side="left", padx=(4, 0))

        def update_count():
            count = len(self.tree.get_children())
            self.count_label.config(text=f"{count} student{'s' if count != 1 else ''}")

        btn_cfg = dict(bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT,
                       relief="solid", bd=1, padx=14, pady=5, cursor="hand2")
        tk.Button(action_bar, text="✏  Edit",
                  command=edit_student, **btn_cfg).pack(side="right", padx=4)
        tk.Button(action_bar, text="⊞  Assign room",
                  command=assign_room,  **btn_cfg).pack(side="right", padx=4)
        tk.Button(action_bar, text="🗑  Delete",
                  bg=WHITE, fg="#c0392b", font=UNIFORM_FONT,
                  relief="solid", bd=1, padx=14, pady=5,
                  cursor="hand2", command=delete_student).pack(side="right", padx=4)

        tk.Label(card, text="ⓘ  Click a row to select before editing, assigning, or deleting.",
                 bg=WHITE, fg=FG_MUTED, font=("Segoe UI", 8),
                 anchor="w").pack(fill="x", padx=20, pady=(0, 10))

    # ── Rooms page ────────────────────────────────────────────────────
    def build_rooms_page(self, page):

        def rooms_messagebox(msg, title="Info"):
            win = tk.Toplevel()
            win.title(title)
            win.config(bg=WHITE)
            win.geometry("300x120")
            win.resizable(False, False)
            tk.Label(win, text=msg, bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT, wraplength=260).pack(pady=20)
            tk.Button(win, text="OK", bg=BLACK, fg=WHITE, font=UNIFORM_FONT,
                      relief="flat", padx=20, pady=4,
                      command=win.destroy).pack()

        def rooms_messagebox_confirm(msg):
            result = [False]
            win = tk.Toplevel()
            win.title("Confirm")
            win.config(bg=WHITE)
            win.geometry("320x130")
            win.resizable(False, False)
            tk.Label(win, text=msg, bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT, wraplength=280).pack(pady=16)
            btn_row = tk.Frame(win, bg=WHITE)
            btn_row.pack()
            def confirm():
                result[0] = True
                win.destroy()
            tk.Button(btn_row, text="Delete", bg="#c0392b", fg=WHITE, font=UNIFORM_FONT,
                      relief="flat", padx=14, pady=4,
                      cursor="hand2", command=confirm).pack(side="left", padx=6)
            tk.Button(btn_row, text="Cancel", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT,
                      relief="solid", bd=1, padx=14, pady=4,
                      cursor="hand2", command=win.destroy).pack(side="left", padx=6)
            win.grab_set()
            win.wait_window()
            return result[0]

        topbar = tk.Frame(page, bg=content_color)
        topbar.pack(fill="x", padx=28, pady=(20, 12))
        tk.Label(topbar, text="Rooms", bg=content_color, fg=FG_DARK,
                 font=("Segoe UI", 17, "bold")).pack(side="left")
        add_btn = tk.Button(topbar, text="+ Add room", bg=WHITE, fg=FG_DARK,
                            font=UNIFORM_FONT, relief="solid", bd=1,
                            padx=12, pady=5, cursor="hand2")
        add_btn.pack(side="right")

        card = tk.Frame(page, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="both", expand=True, padx=28, pady=(0, 20))

        search_wrap = tk.Frame(card, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        search_wrap.pack(fill="x", padx=16, pady=(14, 10))
        tk.Label(search_wrap, text="🔍", bg=WHITE, fg=FG_MUTED,
                 font=UNIFORM_FONT).pack(side="left", padx=(8, 2), pady=6)
        search_entry = tk.Entry(search_wrap, bg=WHITE, fg=FG_MUTED,
                                font=UNIFORM_FONT, relief="flat", bd=0,
                                insertbackground=FG_DARK)
        search_entry.insert(0, "Search by room number or type...")
        search_entry.pack(side="left", fill="x", expand=True, pady=7, padx=4)

        filter_frame = tk.Frame(card, bg=WHITE)
        filter_frame.pack(fill="x", padx=16, pady=(0, 8))
        tk.Label(filter_frame, text="Filter:", bg=WHITE, fg=FG_MUTED,
                 font=("Segoe UI", 9)).pack(side="left", padx=(0, 6))
        for label, color in [("All", FG_DARK), ("Vacant", "#27ae60"),
                              ("Occupied", "#8e44ad"), ("Maintenance", "#e67e22")]:
            tk.Button(filter_frame, text=label, bg=WHITE, fg=color,
                      font=("Segoe UI", 8), relief="solid", bd=1,
                      padx=10, pady=3, cursor="hand2").pack(side="left", padx=3)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Rooms.Treeview", background=WHITE, foreground=FG_DARK,
                        rowheight=36, fieldbackground=WHITE, borderwidth=0, font=UNIFORM_FONT)
        style.configure("Rooms.Treeview.Heading", background=HEADER_BG, foreground="#555577",
                        font=("Segoe UI", 9, "bold"), relief="flat", padding=(8, 6))
        style.map("Rooms.Treeview",
                  background=[("selected", ROW_SEL)],
                  foreground=[("selected", FG_DARK)])
        style.layout("Rooms.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

        columns = ("room_no", "type", "capacity", "occupants", "status", "last_cleaned")
        tree_frame = tk.Frame(card, bg=WHITE)
        tree_frame.pack(fill="both", expand=True, padx=16)

        self.rooms_tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                       style="Rooms.Treeview", selectmode="browse")
        col_cfg = [
            ("room_no",      "Room No.",      90,  "center"),
            ("type",         "Type",         100,  "center"),
            ("capacity",     "Capacity",      80,  "center"),
            ("occupants",    "Occupants",     90,  "center"),
            ("status",       "Status",       120,  "center"),
            ("last_cleaned", "Last Cleaned", 140,  "w"),
        ]
        for cid, heading, width, anchor in col_cfg:
            self.rooms_tree.heading(cid, text=heading, anchor=anchor)
            self.rooms_tree.column(cid, width=width, anchor=anchor, stretch=True)

        sample_rooms = [
            ("101", "Single", "1", "1", "Occupied",    "May 20, 2025"),
            ("102", "Double", "2", "0", "Vacant",       "May 19, 2025"),
            ("103", "Triple", "3", "3", "Occupied",    "May 18, 2025"),
            ("104", "Single", "1", "0", "Maintenance", "May 15, 2025"),
            ("105", "Suite",  "4", "2", "Occupied",    "May 20, 2025"),
            ("106", "Double", "2", "0", "Vacant",       "May 17, 2025"),
        ]
        for row in sample_rooms:
            self.rooms_tree.insert("", "end", values=row)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.rooms_tree.yview)
        self.rooms_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.rooms_tree.pack(side="left", fill="both", expand=True)

        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=16, pady=(6, 0))

        action_bar = tk.Frame(card, bg=WHITE)
        action_bar.pack(fill="x", padx=16, pady=10)

        room_count_label = tk.Label(action_bar, text="6 rooms total", bg=WHITE,
                                    fg=FG_MUTED, font=UNIFORM_FONT)
        room_count_label.pack(side="left", padx=(4, 0))

        def update_room_count():
            count = len(self.rooms_tree.get_children())
            room_count_label.config(text=f"{count} room{'s' if count != 1 else ''} total")

        def add_room_window(prefill=None, edit_item=None):
            win = tk.Toplevel()
            win.title("Edit Room" if edit_item else "Add Room")
            win.config(bg=content_color)
            win.geometry("420x340")
            win.resizable(False, False)

            upperFrame = tk.Frame(win, bg=content_color)
            upperFrame.pack(fill="x", padx=15, pady=12)
            tk.Label(upperFrame,
                     text="Edit Room" if edit_item else "Add Room",
                     bg=content_color, fg=FG_DARK,
                     font=("Segoe UI", 15, "bold")).pack(side="left")

            midFrame = tk.Frame(win, bg=WHITE, padx=15, pady=15,
                                bd=1, relief="solid", highlightbackground=BORDER)
            midFrame.pack(fill="both", expand=True, padx=15, pady=5)
            midFrame.columnconfigure(0, weight=1)
            midFrame.columnconfigure(1, weight=1)

            tk.Label(midFrame, text="Room Number", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 2))
            roomNumBorder = tk.Frame(midFrame, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
            roomNumBorder.grid(row=1, column=0, columnspan=2, sticky="we", pady=(0, 12))
            roomNumEntry = tk.Entry(roomNumBorder, bg=WHITE, fg=BLACK,
                                    font=UNIFORM_FONT, relief="flat", bd=0, insertbackground=FG_DARK)
            roomNumEntry.pack(fill="x", padx=5, pady=3)

            tk.Label(midFrame, text="Room Type", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).grid(row=2, column=0, sticky="w", padx=(0, 8), pady=(0, 2))
            tk.Label(midFrame, text="Capacity", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).grid(row=2, column=1, sticky="w", pady=(0, 2))

            typeVar = tk.StringVar()
            typeDropdown = ttk.Combobox(midFrame, textvariable=typeVar,
                                        values=["Single", "Double", "Triple", "Suite"],
                                        state="readonly", font=UNIFORM_FONT)
            typeDropdown.grid(row=3, column=0, sticky="we", padx=(0, 8), pady=(0, 12))
            typeDropdown.current(0)

            capVar = tk.StringVar()
            capDropdown = ttk.Combobox(midFrame, textvariable=capVar,
                                       values=["1", "2", "3", "4"],
                                       state="readonly", font=UNIFORM_FONT)
            capDropdown.grid(row=3, column=1, sticky="we", pady=(0, 12))
            capDropdown.current(0)

            tk.Label(midFrame, text="Status", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).grid(row=4, column=0, columnspan=2, sticky="w", pady=(0, 2))
            statusVar = tk.StringVar()
            statusDropdown = ttk.Combobox(midFrame, textvariable=statusVar,
                                          values=["Vacant", "Occupied", "Under Maintenance"],
                                          state="readonly", font=UNIFORM_FONT)
            statusDropdown.grid(row=5, column=0, columnspan=2, sticky="we", pady=(0, 4))
            statusDropdown.current(0)

            if prefill:
                roomNumEntry.insert(0, prefill[0])
                typeVar.set(prefill[1])
                capVar.set(prefill[2])
                statusVar.set(prefill[4])

            err_label = tk.Label(win, text="", fg="#c0392b", bg=content_color, font=UNIFORM_FONT)
            err_label.pack()

            def save_room():
                room_no = roomNumEntry.get().strip()
                if not room_no:
                    err_label.config(text="Room number is required.")
                    return
                r_type = typeVar.get()
                cap    = capVar.get()
                status = statusVar.get()

                if edit_item:
                    orig = self.rooms_tree.item(edit_item, "values")
                    occupants    = orig[3]
                    last_cleaned = orig[5]
                    self.rooms_tree.item(edit_item, values=(room_no, r_type, cap, occupants, status, last_cleaned))
                else:
                    self.rooms_tree.insert("", "end", values=(room_no, r_type, cap, "0", status, "—"))
                    update_room_count()

                win.destroy()

            bottomFrame = tk.Frame(win, bg=content_color)
            bottomFrame.pack(fill="x", padx=15, pady=15)
            tk.Button(bottomFrame, text="Save", font=UNIFORM_FONT,
                      bg=BLACK, fg=WHITE, relief="flat", padx=12, pady=5,
                      cursor="hand2", command=save_room).pack(side="right", padx=(5, 0))
            tk.Button(bottomFrame, text="Cancel", font=UNIFORM_FONT,
                      fg="#c0392b", relief="flat", padx=12, pady=5,
                      cursor="hand2", command=win.destroy).pack(side="right")

        def delete_room():
            selected = self.rooms_tree.selection()
            if not selected:
                rooms_messagebox("Select a room first.", "No Selection")
                return
            if rooms_messagebox_confirm("Delete this room? This cannot be undone."):
                self.rooms_tree.delete(selected[0])
                update_room_count()

        def edit_room():
            selected = self.rooms_tree.selection()
            if not selected:
                rooms_messagebox("Select a room first.", "No Selection")
                return
            values = self.rooms_tree.item(selected[0], "values")
            add_room_window(prefill=values, edit_item=selected[0])

        def view_room_details():
            selected = self.rooms_tree.selection()
            if not selected:
                rooms_messagebox("Select a room first.", "No Selection")
                return
            values = self.rooms_tree.item(selected[0], "values")

            win = tk.Toplevel()
            win.title(f"Room {values[0]} — Details")
            win.config(bg=content_color)
            win.geometry("360x320")
            win.resizable(False, False)

            upperFrame = tk.Frame(win, bg=content_color)
            upperFrame.pack(fill="x", padx=15, pady=12)
            tk.Label(upperFrame, text=f"Room {values[0]} Details",
                     bg=content_color, fg=FG_DARK,
                     font=("Segoe UI", 15, "bold")).pack(side="left")

            midFrame = tk.Frame(win, bg=WHITE, padx=20, pady=20,
                                bd=1, relief="solid", highlightbackground=BORDER)
            midFrame.pack(fill="both", expand=True, padx=15, pady=5)
            midFrame.columnconfigure(0, weight=1)
            midFrame.columnconfigure(1, weight=2)

            fields = [
                ("Room Number",  values[0]),
                ("Room Type",    values[1]),
                ("Capacity",     values[2]),
                ("Occupants",    values[3]),
                ("Status",       values[4]),
                ("Last Cleaned", values[5]),
            ]
            for i, (label, value) in enumerate(fields):
                tk.Label(midFrame, text=label, bg=WHITE, fg=FG_MUTED,
                         font=("Segoe UI", 9)).grid(row=i, column=0, sticky="w", pady=5)
                tk.Label(midFrame, text=value, bg=WHITE, fg=FG_DARK,
                         font=("Segoe UI", 10, "bold")).grid(row=i, column=1, sticky="w", pady=5, padx=(10, 0))

            bottomFrame = tk.Frame(win, bg=content_color)
            bottomFrame.pack(fill="x", padx=15, pady=10)
            tk.Button(bottomFrame, text="Close", font=UNIFORM_FONT,
                      bg=BLACK, fg=WHITE, relief="flat", padx=12, pady=5,
                      cursor="hand2", command=win.destroy).pack(side="right")

        add_btn.config(command=add_room_window)

        btn_cfg = dict(bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT,
                       relief="solid", bd=1, padx=14, pady=5, cursor="hand2")
        tk.Button(action_bar, text="✏  Edit",
                  command=edit_room, **btn_cfg).pack(side="right", padx=4)
        tk.Button(action_bar, text="⊞  View details",
                  command=view_room_details, **btn_cfg).pack(side="right", padx=4)
        tk.Button(action_bar, text="🗑  Delete",
                  bg=WHITE, fg="#c0392b", font=UNIFORM_FONT,
                  relief="solid", bd=1, padx=14, pady=5,
                  cursor="hand2", command=delete_room).pack(side="right", padx=4)

        tk.Label(card, text="ⓘ  Click a row to select before editing, viewing details, or deleting.",
                 bg=WHITE, fg=FG_MUTED, font=("Segoe UI", 8),
                 anchor="w").pack(fill="x", padx=20, pady=(0, 10))

    # ── Cleaning page ─────────────────────────────────────────────────
    def build_cleaning_page(self, page):

        def addCleaningStaff():
            addStaff = tk.Toplevel()
            addStaff.title("Add Cleaning Staff")
            addStaff.config(bg=content_color)
            addStaff.geometry("500x360")
            addStaff.resizable(False, False)

            def save_staff():
                cs_ID   = idEntry.get().strip()
                last    = LN_Entry.get().strip()
                first   = FN_Entry.get().strip()
                mi      = MI_Entry.get().strip()
                email   = emailEntry.get().strip()
                contact = contactEntry.get().strip()
                full_name = f"{last}, {first} {mi}".strip()

                if not cs_ID or not last or not first or not email or not contact:
                    messagebox.showerror("Error", "Please fill in all required fields.")
                    return

                self.db.insert_cleaning_staff(cs_ID, last, first, mi, email, contact, full_name)
                self.db.get_all_cleaning_staff()
                addStaff.destroy()

            

            upperFrame = tk.Frame(addStaff, bg=content_color)
            upperFrame.pack(fill="x", padx=15, pady=12)
            tk.Label(upperFrame, text="Add Cleaning Staff", bg=content_color, fg=FG_DARK,
                     font=("Segoe UI", 15, "bold")).pack(side="left")

            midFrame = tk.Frame(addStaff, bg=WHITE, padx=15, pady=15,
                                bd=1, relief="solid", highlightbackground=BORDER)
            midFrame.pack(fill="x", padx=15, pady=5)
            midFrame.columnconfigure(0, weight=2)
            midFrame.columnconfigure(1, weight=2)
            midFrame.columnconfigure(2, weight=0)

            tk.Label(midFrame, text="Cleaning Staff ID", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 2))
            idFrame = tk.Frame(midFrame, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
            idFrame.grid(row=1, column=0, columnspan=3, sticky="we", pady=(0, 15))
            idEntry = tk.Entry(idFrame, bg=WHITE, fg=BLACK, font=UNIFORM_FONT,
                               relief="flat", bd=0, insertbackground=FG_DARK)
            idEntry.pack(fill="x", padx=5, pady=4)

            lnGroup = tk.Frame(midFrame, bg=WHITE)
            lnGroup.grid(row=2, column=0, sticky="we", padx=(0, 6), pady=(0, 15))
            tk.Label(lnGroup, text="Last Name", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).pack(anchor="w", pady=(0, 2))
            lnBorder = tk.Frame(lnGroup, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
            lnBorder.pack(fill="x")
            LN_Entry = tk.Entry(lnBorder, bg=WHITE, fg=BLACK, font=UNIFORM_FONT,
                                relief="flat", bd=0, insertbackground=FG_DARK)
            LN_Entry.pack(fill="x", padx=5, pady=4)

            fnGroup = tk.Frame(midFrame, bg=WHITE)
            fnGroup.grid(row=2, column=1, sticky="we", padx=6, pady=(0, 15))
            tk.Label(fnGroup, text="First Name", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).pack(anchor="w", pady=(0, 2))
            fnBorder = tk.Frame(fnGroup, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
            fnBorder.pack(fill="x")
            FN_Entry = tk.Entry(fnBorder, bg=WHITE, fg=BLACK, font=UNIFORM_FONT,
                                relief="flat", bd=0, insertbackground=FG_DARK)
            FN_Entry.pack(fill="x", padx=5, pady=4)

            miGroup = tk.Frame(midFrame, bg=WHITE)
            miGroup.grid(row=2, column=2, sticky="w", padx=(6, 0), pady=(0, 15))
            tk.Label(miGroup, text="M.I.", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).pack(anchor="w", pady=(0, 2))
            miBorder = tk.Frame(miGroup, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
            miBorder.pack()
            MI_Entry = tk.Entry(miBorder, bg=WHITE, fg=BLACK, font=UNIFORM_FONT,
                                relief="flat", bd=0, insertbackground=FG_DARK, width=3)
            MI_Entry.pack(padx=5, pady=4)

            emailGroup = tk.Frame(midFrame, bg=WHITE)
            emailGroup.grid(row=3, column=0, sticky="we", padx=(0, 6), pady=(0, 15))
            tk.Label(emailGroup, text="Email", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).pack(anchor="w", pady=(0, 2))
            emailBorder = tk.Frame(emailGroup, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
            emailBorder.pack(fill="x")
            emailEntry = tk.Entry(emailBorder, bg=WHITE, fg=BLACK, font=UNIFORM_FONT,
                                  relief="flat", bd=0, insertbackground=FG_DARK)
            emailEntry.pack(fill="x", padx=5, pady=4)

            contactGroup = tk.Frame(midFrame, bg=WHITE)
            contactGroup.grid(row=3, column=1, columnspan=2, sticky="we", padx=(6, 0), pady=(0, 15))
            tk.Label(contactGroup, text="Contact Number", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).pack(anchor="w", pady=(0, 2))
            contactBorder = tk.Frame(contactGroup, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
            contactBorder.pack(fill="x")
            contactEntry = tk.Entry(contactBorder, bg=WHITE, fg=BLACK, font=UNIFORM_FONT,
                                    relief="flat", bd=0, insertbackground=FG_DARK)
            contactEntry.pack(fill="x", padx=5, pady=4)

            bottomFrame = tk.Frame(addStaff, bg=content_color)
            bottomFrame.pack(fill="x", padx=15, pady=15)
            tk.Button(bottomFrame, text="Add Staff", font=UNIFORM_FONT,
                      command=save_staff).pack(side="right", padx=(5, 0))
            tk.Button(bottomFrame, text="Cancel", fg="#c0392b", font=UNIFORM_FONT,
                      command=addStaff.destroy).pack(side="right")

        def CSassign_window():
            assign = tk.Toplevel()
            assign.title("Assign Cleaning")
            assign.config(bg=content_color)
            assign.geometry("420x360")
            assign.resizable(False, False)

            upperFrame = tk.Frame(assign, bg=content_color)
            upperFrame.pack(fill="x", padx=15, pady=12)
            tk.Label(upperFrame, text="Assign Cleaning", bg=content_color, fg=FG_DARK,
                     font=("Segoe UI", 15, "bold")).pack(side="left")

            midFrame = tk.Frame(assign, bg=WHITE, padx=15, pady=15,
                                bd=1, relief="solid", highlightbackground=BORDER)
            midFrame.pack(fill="both", expand=True, padx=15, pady=5)
            midFrame.columnconfigure(0, weight=1)
            midFrame.columnconfigure(1, weight=1)

            tk.Label(midFrame, text="Room", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 2))
            roomSelection = tk.StringVar()
            roomOptions = ["Option 1", "Option 2", "Option 3"]
            roomDropdown = ttk.Combobox(midFrame, textvariable=roomSelection, values=roomOptions,
                                        state="readonly", font=UNIFORM_FONT)
            roomDropdown.grid(row=1, column=0, columnspan=2, sticky="we", pady=(0, 12))
            roomDropdown.current(0)

            tk.Label(midFrame, text="Date", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 2))
            searchFrame = tk.Frame(midFrame, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
            searchFrame.grid(row=3, column=0, columnspan=2, sticky="we", pady=(0, 12))
            dateEntry = tk.Entry(searchFrame, bg=WHITE, fg=BLACK, font=UNIFORM_FONT,
                                 relief="flat", bd=0, insertbackground=FG_DARK)
            dateEntry.pack(fill="x", padx=5, pady=3)

            timeStartFrame = tk.Frame(midFrame, bg=WHITE)
            timeStartFrame.grid(row=4, column=0, sticky="we", padx=(0, 8))
            tk.Label(timeStartFrame, text="Time Start", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).pack(anchor="w", pady=(0, 2))
            tStartBorder = tk.Frame(timeStartFrame, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
            tStartBorder.pack(fill="x")
            timeStartEntry = tk.Entry(tStartBorder, bg=WHITE, fg=BLACK, font=UNIFORM_FONT,
                                      relief="flat", bd=0)
            timeStartEntry.pack(fill="x", padx=5, pady=3)

            timeEndFrame = tk.Frame(midFrame, bg=WHITE)
            timeEndFrame.grid(row=4, column=1, sticky="we", padx=(8, 0))
            tk.Label(timeEndFrame, text="Time End", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).pack(anchor="w", pady=(0, 2))
            tEndBorder = tk.Frame(timeEndFrame, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
            tEndBorder.pack(fill="x")
            timeEndEntry = tk.Entry(tEndBorder, bg=WHITE, fg=BLACK, font=UNIFORM_FONT,
                                    relief="flat", bd=0)
            timeEndEntry.pack(fill="x", padx=5, pady=3)

            bottomFrame = tk.Frame(assign, bg=content_color)
            bottomFrame.pack(fill="x", padx=15, pady=15)
            tk.Button(bottomFrame, text="Save Schedule",
                      font=UNIFORM_FONT).pack(side="right", padx=(5, 0))
            tk.Button(bottomFrame, text="Cancel", fg="#c0392b",
                      font=UNIFORM_FONT).pack(side="right")


        # ── Top bar ───────────────────────────────────────────────────
        upperFrame = tk.Frame(page, bg=content_color)
        upperFrame.pack(fill="x", padx=28, pady=(20, 12))
        tk.Label(upperFrame, text="Cleaning Staff", bg=content_color, fg=FG_DARK,
                 font=("Segoe UI", 17, "bold")).pack(side="left")
        tk.Button(upperFrame, text="+ Add Staff", command=addCleaningStaff,
                  bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT, relief="solid", bd=1,
                  padx=12, pady=5, cursor="hand2").pack(side="right")

        # ── Card ──────────────────────────────────────────────────────
        card = tk.Frame(page, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="both", expand=True, padx=28, pady=(0, 20))

        searchFrame = tk.Frame(card, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        searchFrame.pack(fill="x", padx=16, pady=(14, 10))
        tk.Label(searchFrame, text="🔍", bg=WHITE, fg=FG_MUTED,
                 font=UNIFORM_FONT).pack(side="left", padx=(8, 2), pady=6)
        CSsearchEntry = tk.Entry(searchFrame, bg=WHITE, fg=BLACK,
                                 font=UNIFORM_FONT, relief="flat", bd=0,
                                 insertbackground=FG_DARK)
        CSsearchEntry.pack(side="left", fill="x", expand=True, pady=7, padx=4)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("CleaningStaff.Treeview", background=WHITE, foreground=FG_DARK,
                        rowheight=36, fieldbackground=WHITE, borderwidth=0, font=UNIFORM_FONT)
        style.configure("CleaningStaff.Treeview.Heading", background=HEADER_BG, foreground="#555577",
                        font=("Segoe UI", 9, "bold"), relief="flat", padding=(8, 6))
        style.map("CleaningStaff.Treeview",
                  background=[("selected", ROW_SEL)],
                  foreground=[("selected", FG_DARK)])
        style.layout("CleaningStaff.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

        tree_frame = tk.Frame(card, bg=WHITE)
        tree_frame.pack(fill="both", expand=True, padx=16)

        self.cleaning_tree = ttk.Treeview(tree_frame,                          # self — used by add_staff_treeview
                                          columns=("CS_ID", "CS_NAME", "CS_CONTACT", "CS_EMAIL"),
                                          show="headings",
                                          style="CleaningStaff.Treeview")
        self.cleaning_tree.heading("CS_ID",      text="Staff ID")
        self.cleaning_tree.heading("CS_NAME",    text="Name")
        self.cleaning_tree.heading("CS_CONTACT", text="Contact")
        self.cleaning_tree.heading("CS_EMAIL",   text="Email")
        self.cleaning_tree.column("CS_ID",      width=80)
        self.cleaning_tree.column("CS_NAME",    width=200)
        self.cleaning_tree.column("CS_CONTACT", width=300)
        self.cleaning_tree.column("CS_EMAIL",   width=300)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.cleaning_tree.yview)
        self.cleaning_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.cleaning_tree.pack(side="left", fill="both", expand=True)

        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=16, pady=(6, 0))

        btnFrame = tk.Frame(card, bg=WHITE)
        btnFrame.pack(fill="x", padx=16, pady=10)

        btn_cfg = dict(bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT,
                       relief="solid", bd=1, padx=14, pady=5, cursor="hand2")
        tk.Button(btnFrame, text="✏  Edit",            **btn_cfg).pack(side="right", padx=4)
        tk.Button(btnFrame, text="⊞  Assign Cleaning",
                  command=CSassign_window, **btn_cfg).pack(side="right", padx=4)
        tk.Button(btnFrame, text="🗑  Delete",
                  bg=WHITE, fg="#c0392b", font=UNIFORM_FONT,
                  relief="solid", bd=1, padx=14, pady=5,
                  cursor="hand2").pack(side="right", padx=4)

        tk.Label(card, text="ⓘ  Click a row to select before editing, assigning, or deleting.",
                 bg=WHITE, fg=FG_MUTED, font=("Segoe UI", 8),
                 anchor="w").pack(fill="x", padx=20, pady=(0, 10))

        self.db.get_all_cleaning_staff(self.cleaning_tree)

    # ── Settings page ─────────────────────────────────────────────────
    def build_settings_page(self, page):
        tk.Label(page, text="FOR LOG OUT AND USER MANAGEMENT", bg=content_color,
                 fg=font_color_sidebar, font=("Arial", 16, "bold")).pack(pady=20)


if __name__ == "__main__":
    app = main()
    app.mainloop()