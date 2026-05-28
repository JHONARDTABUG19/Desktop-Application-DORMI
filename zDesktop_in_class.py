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

    def create_student_table(self):
        with sqlite3.connect(DB_NAME) as connect:
            cursor = connect.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students
                (
                    student_no VARCHAR(255) PRIMARY KEY,
                    last_name VARCHAR(255) NOT NULL,
                    first_name VARCHAR(255) NOT NULL,
                    middle_initial VARCHAR(255),
                    program VARCHAR(255) NOT NULL,
                    status VARCHAR(255) NOT NULL,
                    contact VARCHAR(255) NOT NULL
                )
            """)
            connect.commit()

    def add_student(self, student_no, last, first, mi, program, status, contact):
        with sqlite3.connect(DB_NAME) as connect:
            cursor = connect.cursor()
            cursor.execute(
                "INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?)",
                (student_no, last, first, mi, program, status, contact)
            )
            connect.commit()

    def get_all_students(self, tree):
        for row in tree.get_children():
            tree.delete(row)
        with sqlite3.connect(DB_NAME) as connect:
            cursor = connect.cursor()
            cursor.execute("SELECT student_no, TRIM(first_name || ' ' || COALESCE(middle_initial || '. ', '') || last_name), program, '', status, contact FROM students")
            for row in cursor.fetchall():
                tree.insert("", "end", values=row)

    def update_student(self, original_no, student_no, last, first, mi, program, status, contact):
        with sqlite3.connect(DB_NAME) as connect:
            cursor = connect.cursor()
            cursor.execute("""
                UPDATE students
                SET student_no=?, last_name=?, first_name=?, middle_initial=?,
                    program=?, status=?, contact=?
                WHERE student_no=?
            """, (student_no, last, first, mi, program, status, contact, original_no))
            connect.commit()


    def delete_student(self, student_no):
        with sqlite3.connect(DB_NAME) as connect:
            cursor = connect.cursor()
            cursor.execute("DELETE FROM students WHERE student_no=?", (student_no,))
            connect.commit()
    



    def create_rooms_table(self):
        with sqlite3.connect(DB_NAME) as connect:
            cursor = connect.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rooms (
                    room_id      INTEGER PRIMARY KEY AUTOINCREMENT,
                    building     VARCHAR(255) NOT NULL,
                    room_number  VARCHAR(255) NOT NULL,
                    room_type    VARCHAR(255) NOT NULL,
                    capacity     INTEGER NOT NULL,
                    occupants    INTEGER DEFAULT 0,
                    status       VARCHAR(255) NOT NULL,
                    last_cleaned VARCHAR(255) DEFAULT '—'
                )
            """)
            connect.commit()

    def add_room(self, building, room_number, room_type, capacity, status):
        with sqlite3.connect(DB_NAME) as connect:
            cursor = connect.cursor()
            cursor.execute(
                "INSERT INTO rooms (building, room_number, room_type, capacity, status) VALUES (?, ?, ?, ?, ?)",
                (building, room_number, room_type, capacity, status)
            )
            connect.commit()

    def get_all_rooms(self, tree):
        for row in tree.get_children():
            tree.delete(row)
        with sqlite3.connect(DB_NAME) as connect:
            cursor = connect.cursor()
            cursor.execute("SELECT room_id, room_number, building, room_type, capacity, occupants, status, last_cleaned FROM rooms")
            for row in cursor.fetchall():
                room_id = row[0]
                values  = row[1:]   # everything except room_id
                tree.insert("", "end", values=values, tags=(room_id,))

    def update_room(self, room_id, building, room_number, room_type, capacity, status):
        with sqlite3.connect(DB_NAME) as connect:
            cursor = connect.cursor()
            cursor.execute("""
                UPDATE rooms
                SET building=?, room_number=?, room_type=?, capacity=?, status=?
                WHERE room_id=?
            """, (building, room_number, room_type, capacity, status, room_id))
            connect.commit()

    def delete_room(self, room_id):
        with sqlite3.connect(DB_NAME) as connect:
            cursor = connect.cursor()
            cursor.execute("DELETE FROM rooms WHERE room_id=?", (room_id,))
            connect.commit()



            

    def create_table_cleaning_staff(self):
        with sqlite3.connect(DB_NAME) as connect:
            cursor = connect.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cleaningStaff 
                (
                    cs_ID VARCHAR(255) PRIMARY KEY,
                    last_name VARCHAR(255) NOT NULL,
                    first_name VARCHAR(255) NOT NULL,
                    middle_initial VARCHAR(255),
                    email VARCHAR(255) UNIQUE NOT NULL,
                    contact VARCHAR(255) NOT NULL,
                    full_name VARCHAR(255) NOT NULL 
                )
            """)
            connect.commit()

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
            connect.commit()
        

    
            
    
    
            


class main(tk.Tk):
    """ This 1st function is called in login if confirmed. Also a function that is necessary 
    to run the whole program. It contains the layout of the whole program and the navigation 
    of the pages. All other pages are called in this function. """

    def __init__(self):
        super().__init__()
        self.geometry("1200x650")
        self.minsize(1150, 650)
        self.title("Dormi Admin Panel")
        self.db = Database()
        self.db.create_student_table()
        self.db.create_rooms_table()
        self.db.create_table_cleaning_staff()
        
        self.all_pages   = []
        self.all_buttons = []

        self.main_build_layout()

    # ── Layout ────────────────────────────────────────────────────────
    def main_build_layout(self):
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

        self.treeStuAss = ttk.Treeview(page, columns=("Student", "Room", "Start Date", "Status"), show="headings")

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
            win.geometry("500x400")
            win.resizable(False, False)
            win.grab_set()

            tk.Frame(win, bg=content_color)
            upperFrame = tk.Frame(win, bg=content_color)
            upperFrame.pack(fill="x", padx=15, pady=12)
            tk.Label(upperFrame,
                     text="Edit Student" if edit_item else "Add Student",
                     bg=content_color, fg=FG_DARK,
                     font=("Segoe UI", 15, "bold")).pack(side="left")

            midFrame = tk.Frame(win, bg=WHITE, padx=15, pady=5,
                                bd=1, relief="solid", highlightbackground=BORDER)
            midFrame.pack(fill="both", expand=True, padx=15, pady=5)
            midFrame.columnconfigure(0, weight=2)
            midFrame.columnconfigure(1, weight=2)
            midFrame.columnconfigure(2, weight=0)

            def make_entry(parent, row, col, colspan=1, padx=(0,0), width=None):
                border = tk.Frame(parent, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
                border.grid(row=row, column=col, columnspan=colspan, sticky="we",
                            padx=padx, pady=(0,10))
                kw = dict(bg=WHITE, fg=BLACK, font=UNIFORM_FONT, relief="flat", bd=0)
                if width:
                    kw["width"] = width
                e = tk.Entry(border, **kw)
                e.pack(fill="x", padx=5, pady=3)
                return e

            # Row 0-1: Student No. (full width)
            tk.Label(midFrame, text="Student No.", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0,2))
            e_no = make_entry(midFrame, 1, 0, colspan=3)

            # Row 2-3: Last Name | First Name | M.I.
            tk.Label(midFrame, text="Last Name", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).grid(row=2, column=0, sticky="w", padx=(0,6), pady=(0,2))
            tk.Label(midFrame, text="First Name", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).grid(row=2, column=1, sticky="w", padx=6, pady=(0,2))
            tk.Label(midFrame, text="M.I.", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).grid(row=2, column=2, sticky="w", padx=(6,0), pady=(0,2))

            e_last  = make_entry(midFrame, 3, 0, padx=(0,6))
            e_first = make_entry(midFrame, 3, 1, padx=(6,6))
            e_mi    = make_entry(midFrame, 3, 2, padx=(6,0), width=3)

            # Row 4-5: Program | Status
            tk.Label(midFrame, text="Program", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).grid(row=4, column=0, sticky="w", padx=(0,6), pady=(0,2))
            tk.Label(midFrame, text="Status", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).grid(row=4, column=1, sticky="w", padx=6, pady=(0,2))

            e_program = make_entry(midFrame, 5, 0, padx=(0,6))

            statusVar = tk.StringVar()
            statusDrop = ttk.Combobox(midFrame, textvariable=statusVar,
                                      values=["Active", "Inactive", "On Leave"],
                                      state="readonly", font=UNIFORM_FONT)
            statusDrop.grid(row=5, column=1, columnspan=2, sticky="we", padx=(6,0), pady=(0,10))
            statusDrop.current(0)

            # Row 6-7: Contact (full width)
            tk.Label(midFrame, text="Contact", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).grid(row=6, column=0, columnspan=3, sticky="w", pady=(0,2))
            e_contact = make_entry(midFrame, 7, 0, colspan=3)

            if prefill:
                e_no.insert(0,      prefill[0])
                e_program.insert(0, prefill[2])
                statusVar.set(      prefill[4])
                e_contact.insert(0, prefill[5])

                parts = prefill[1].split()
                e_first.insert(0, parts[0])
                
                if len(parts) == 3:
                    e_mi.insert(0,   parts[1].replace(".", ""))
                    e_last.insert(0, parts[2])
                elif len(parts) == 2:
                    e_last.insert(0, parts[1])

            err_label = tk.Label(win, text="", fg="#c0392b", bg=content_color, font=UNIFORM_FONT)
            err_label.pack()

            def save():
                no      = e_no.get().strip()
                last    = e_last.get().strip()
                first   = e_first.get().strip()
                mi      = e_mi.get().strip()
                program = e_program.get().strip()
                status  = statusVar.get()
                contact = e_contact.get().strip()

                if not no or not last or not first:
                    err_label.config(text="Student No., Last Name and First Name are required.")
                    return

                full_name = f"{first} {f'{mi}. ' if mi else ''}{last}".strip()

                if edit_item:
                    # ── update DB then refresh treeview row ──
                    original_no = self.tree.item(edit_item, "values")[0]
                    self.db.update_student(original_no, no, last, first, mi, program, status, contact)
                    self.tree.item(edit_item, values=(no, full_name, program, "", status, contact))
                else:
                    # ── insert into DB then add treeview row ──
                    self.db.add_student(no, last, first, mi, program, status, contact)
                    self.tree.insert("", "end", values=(no, full_name, program, "", status, contact))

                update_count()
                win.destroy()

            bottomFrame = tk.Frame(win, bg=content_color)
            bottomFrame.pack(fill="x", padx=15, pady=(0,20))
            tk.Button(bottomFrame, text="Save", font=UNIFORM_FONT,
                      bg=BLACK, fg=WHITE, relief="flat", padx=12, pady=0,
                      cursor="hand2", command=save).pack(side="right", padx=5)
            tk.Button(bottomFrame, text="Cancel", font=UNIFORM_FONT,
                      fg="#c0392b", relief="flat", padx=12, pady=0,
                      cursor="hand2", command=win.destroy).pack(side="right", padx=5)

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
            win.geometry("360x320")
            win.resizable(False, False)
            win.grab_set()

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
            win.grab_set()
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
    
        self.db.get_all_students(self.tree) #loading the treeview with the students from the database

    # ── Rooms page ────────────────────────────────────────────────────
    def build_rooms_page(self, page):

        def rooms_messagebox(msg, title="Info"):
            win = tk.Toplevel()
            win.title(title)
            win.config(bg=WHITE)
            win.geometry("300x120")
            win.resizable(False, False)
            win.grab_set()
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

        columns = ("room_no", "Building", "type", "capacity", "occupants", "status", "last_cleaned")
        tree_frame = tk.Frame(card, bg=WHITE)
        tree_frame.pack(fill="both", expand=True, padx=16)

        self.rooms_tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                       style="Rooms.Treeview", selectmode="browse")
        col_cfg = [
            ("room_no",      "Room No.",      90,  "center"),
            ("Building",     "Building",      70,  "center"),
            ("type",         "Type",         100,  "center"),
            ("capacity",     "Capacity",      80,  "center"),
            ("occupants",    "Occupants",     90,  "center"),
            ("status",       "Status",       120,  "center"),
            ("last_cleaned", "Last Cleaned", 140,  "w"),
        ]
        for cid, heading, width, anchor in col_cfg:
            self.rooms_tree.heading(cid, text=heading, anchor=anchor)
            self.rooms_tree.column(cid, width=width, anchor=anchor, stretch=True)


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
            win.grab_set()

            def save_room():
                room_no  = roomNumEntry.get().strip()
                if not room_no:
                    err_label.config(text="Room number is required.")
                    return
                building = buildingVar.get()
                r_type   = typeVar.get()
                cap      = int(capacityVar.get())
                status   = statusVar.get()

                if edit_item:
                    # get room_id stored in the iid tag
                    room_id = self.rooms_tree.item(edit_item, "tags")[0]
                    self.db.update_room(room_id, building, room_no, r_type, cap, status)
                else:
                    self.db.add_room(building, room_no, r_type, cap, status)

                # always re-fetch from DB to stay in sync
                self.db.get_all_rooms(self.rooms_tree)
                update_room_count()
                win.destroy()

            upperFrame = tk.Frame(win, bg=content_color)
            upperFrame.pack(fill="x", padx=15, pady=12)
            tk.Label(upperFrame,
                     text="Edit Room" if edit_item else "Add Room",
                     bg=content_color, fg=FG_DARK,
                     font=("Segoe UI", 15, "bold")).pack(side="left")

            midFrame = tk.Frame(win, bg=WHITE, padx=15, pady=10,
                                bd=1, relief="solid", highlightbackground=BORDER)
            midFrame.pack(fill="both", expand=True, padx=15, pady=(5,0))
            midFrame.columnconfigure(0, weight=1)
            midFrame.columnconfigure(1, weight=1)

           # Row 0 - Labels
            tk.Label(midFrame, text="Building", bg=WHITE, fg=FG_DARK,
                    font=UNIFORM_FONT).grid(row=0, column=0, sticky="w", padx=(0, 8), pady=(0, 2))

            tk.Label(midFrame, text="Room Number", bg=WHITE, fg=FG_DARK,
                    font=UNIFORM_FONT).grid(row=0, column=1, sticky="w", pady=(0, 2))

            # Row 2 - Labels
            tk.Label(midFrame, text="Room Type", bg=WHITE, fg=FG_DARK,
                    font=UNIFORM_FONT).grid(row=2, column=0, sticky="w", padx=(0, 8), pady=(0, 2))

            tk.Label(midFrame, text="Capacity", bg=WHITE, fg=FG_DARK,
                    font=UNIFORM_FONT).grid(row=2, column=1, sticky="w", pady=(0, 2))
            
            # Row 4 - Status label
            tk.Label(midFrame, text="Status", bg=WHITE, fg=FG_DARK,
                    font=UNIFORM_FONT).grid(row=4, column=0, columnspan=2, sticky="w", pady=(0, 2))

                      # Row 1 - Building dropdown + Room number entry
            buildingVar = tk.StringVar()
            buildingDropdown = ttk.Combobox(midFrame, textvariable=buildingVar,
                                            values=["BLD-A", "BLD-B", "BLD-C"],
                                            state="readonly", font=UNIFORM_FONT)
            buildingDropdown.grid(row=1, column=0, sticky="we", padx=(0, 8), pady=(0, 12))
            buildingDropdown.current(0)

            roomNumBorder = tk.Frame(midFrame, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
            roomNumBorder.grid(row=1, column=1, sticky="we", pady=(0, 12))
            roomNumEntry = tk.Entry(roomNumBorder, bg=WHITE, fg=BLACK, font=UNIFORM_FONT,
                                    relief="flat", bd=0, insertbackground=FG_DARK)
            roomNumEntry.pack(fill="x", padx=5, pady=3)


            typeVar = tk.StringVar()
            typeDropdown = ttk.Combobox(midFrame, textvariable=typeVar,
                                        values=["Single", "Double", "Triple", "Suite"],
                                        state="readonly", font=UNIFORM_FONT)
            typeDropdown.grid(row=3, column=0, sticky="we", padx=(0, 8), pady=(0, 12))
            typeDropdown.current(0)

            capacityVar = tk.StringVar()
            capDropdown = ttk.Combobox(midFrame, textvariable=capacityVar,
                                    values=["1", "2", "3", "4"],
                                    state="readonly", font=UNIFORM_FONT)
            capDropdown.grid(row=3, column=1, sticky="we", pady=(0, 12))
            capDropdown.current(0)

            

            # Row 5 - Status dropdown
            statusVar = tk.StringVar()
            statusDropdown = ttk.Combobox(midFrame, textvariable=statusVar,
                                        values=["Vacant", "Occupied", "Under Maintenance"],
                                        state="readonly", font=UNIFORM_FONT)
            statusDropdown.grid(row=5, column=0, columnspan=2, sticky="we", pady=(0, 4))
            statusDropdown.current(0)

            if prefill:
                buildingVar.set(prefill[1])       # building
                roomNumEntry.insert(0, prefill[0]) # room_no
                typeVar.set(prefill[2])            # type
                capacityVar.set(prefill[3])        # capacity
                statusVar.set(prefill[5])          # status

            err_label = tk.Label(win, text="", fg="#c0392b", bg=content_color, font=UNIFORM_FONT)
            err_label.pack()

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
                room_id = self.rooms_tree.item(selected[0], "tags")[0]
                self.db.delete_room(room_id)
                self.db.get_all_rooms(self.rooms_tree)
                update_room_count()

        def edit_room():
            selected = self.rooms_tree.selection()
            if not selected:
                rooms_messagebox("Select a room first.", "No Selection")
                return
            values = self.rooms_tree.item(selected[0], "values")
            # values = (room_no, building, type, capacity, occupants, status, last_cleaned)
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
            win.grab_set()

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
    
        self.db.get_all_rooms(self.rooms_tree)

    # ── Cleaning page ─────────────────────────────────────────────────
    def build_cleaning_page(self, page):
            cs_ID     = tk.StringVar()
            last      = tk.StringVar()
            first     = tk.StringVar()
            mi        = tk.StringVar()
            email     = tk.StringVar()
            contact   = tk.StringVar()
            full_name = tk.StringVar()

            def addCleaningStaff():
                addStaff = tk.Toplevel()
                addStaff.title("Add Cleaning Staff")
                addStaff.config(bg=content_color)
                addStaff.geometry("500x360")
                addStaff.resizable(False, False)
                addStaff.grab_set()

                def save_staff():
                    id_val       = idEntry.get().strip()
                    last_val     = LN_Entry.get().strip()
                    first_val    = FN_Entry.get().strip()
                    mi_val       = MI_Entry.get().strip()
                    email_val    = emailEntry.get().strip()
                    contact_val  = contactEntry.get().strip()
                    fullname_val = f"{last_val}, {first_val} {mi_val}".strip()

                    if not id_val or not last_val or not first_val or not email_val or not contact_val:
                        messagebox.showerror("Error", "Please fill in all required fields.")
                        return

                    try:
                        self.db.insert_cleaning_staff(id_val, last_val, first_val, mi_val, email_val, contact_val, fullname_val)
                        self.db.get_all_cleaning_staff(self.cleaning_tree)
                        addStaff.destroy()
                    except Exception as e:
                        messagebox.showerror("Database Error", f"Failed to add staff entry:\n{e}")

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

            def select_record(event):
                selected = self.cleaning_tree.focus()
                if selected:
                    values = self.cleaning_tree.item(selected, "values")
                    cs_ID.set(values[0])
                    full_name.set(values[1])
                    contact.set(values[2])
                    email.set(values[3])

            def edit_cleaning_stuff():
                if not self.cleaning_tree.focus():
                    messagebox.showwarning("Selection Required", "Please click a cleaning staff record from the table first.")
                    return

                editStaff = tk.Toplevel()
                editStaff.title("Edit Cleaning Staff")
                editStaff.config(bg=content_color)
                editStaff.geometry("500x360")
                editStaff.resizable(False, False)
                editStaff.grab_set()

                def update_staff():
                    id_val       = idEntry.get().strip()
                    last_val     = LN_Entry.get().strip()
                    first_val    = FN_Entry.get().strip()
                    mi_val       = MI_Entry.get().strip()
                    email_val    = emailEntry.get().strip()
                    contact_val  = contactEntry.get().strip()
                    fullname_val = f"{last_val}, {first_val} {mi_val}".strip()

                    if not id_val or not last_val or not first_val or not email_val or not contact_val:
                        messagebox.showerror("Error", "Please fill in all required fields.")
                        return

                    try:
                        con = sqlite3.connect(DB_NAME)
                        cur = con.cursor()
                        cur.execute(
                            "UPDATE cleaningStaff SET last_name=?, first_name=?, middle_initial=?, email=?, contact=?, full_name=? WHERE cs_ID=?",
                                (last_val, first_val, mi_val, email_val, contact_val, fullname_val, id_val)
                        )
                        con.commit()
                        con.close()
                        self.db.get_all_cleaning_staff(self.cleaning_tree)
                        load_data()
                        clear_fields()
                        editStaff.destroy()
                    except Exception as e:
                        messagebox.showerror("Database Modification Error", 
                                            f"Failed execution block.\nCheck if 'edit_cleaning_stuff' matches your helper method name exactly.\n\nError details: {e}")

                upperFrame = tk.Frame(editStaff, bg=content_color)
                upperFrame.pack(fill="x", padx=15, pady=12)
                tk.Label(upperFrame, text="Edit Cleaning Staff", bg=content_color, fg=FG_DARK,
                        font=("Segoe UI", 15, "bold")).pack(side="left")

                midFrame = tk.Frame(editStaff, bg=WHITE, padx=15, pady=15,
                                    bd=1, relief="solid", highlightbackground=BORDER)
                midFrame.pack(fill="x", padx=15, pady=5)
                midFrame.columnconfigure(0, weight=2)
                midFrame.columnconfigure(1, weight=2)
                midFrame.columnconfigure(2, weight=0)

                tk.Label(midFrame, text="Cleaning Staff ID", bg=WHITE, fg=FG_DARK,
                        font=UNIFORM_FONT).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 2))
                idFrame = tk.Frame(midFrame, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
                idFrame.grid(row=1, column=0, columnspan=3, sticky="we", pady=(0, 15))
                
                idEntry = tk.Entry(idFrame, bg=WHITE, fg=BLACK, font=UNIFORM_FONT, relief="flat", bd=0)
                idEntry.pack(fill="x", padx=5, pady=4)
                idEntry.insert(0, cs_ID.get())

                raw_name = full_name.get()
                last_name_segment = ""
                first_name_segment = ""
                mi_segment = ""
                
                if "," in raw_name:
                    last_name_segment, rest = raw_name.split(",", 1)
                    rest = rest.strip()
                    if " " in rest:
                        parts = rest.split(" ")
                        mi_segment = parts[-1]
                        first_name_segment = " ".join(parts[:-1])
                    else:
                        first_name_segment = rest

                lnGroup = tk.Frame(midFrame, bg=WHITE)
                lnGroup.grid(row=2, column=0, sticky="we", padx=(0, 6), pady=(0, 15))
                tk.Label(lnGroup, text="Last Name", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).pack(anchor="w", pady=(0, 2))
                lnBorder = tk.Frame(lnGroup, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
                lnBorder.pack(fill="x")
                LN_Entry = tk.Entry(lnBorder, bg=WHITE, fg=BLACK, font=UNIFORM_FONT, relief="flat", bd=0)
                LN_Entry.pack(fill="x", padx=5, pady=4)
                LN_Entry.insert(0, last_name_segment.strip())

                fnGroup = tk.Frame(midFrame, bg=WHITE)
                fnGroup.grid(row=2, column=1, sticky="we", padx=6, pady=(0, 15))
                tk.Label(fnGroup, text="First Name", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).pack(anchor="w", pady=(0, 2))
                fnBorder = tk.Frame(fnGroup, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
                fnBorder.pack(fill="x")
                FN_Entry = tk.Entry(fnBorder, bg=WHITE, fg=BLACK, font=UNIFORM_FONT, relief="flat", bd=0)
                FN_Entry.pack(fill="x", padx=5, pady=4)
                FN_Entry.insert(0, first_name_segment.strip())

                miGroup = tk.Frame(midFrame, bg=WHITE)
                miGroup.grid(row=2, column=2, sticky="w", padx=(6, 0), pady=(0, 15))
                tk.Label(miGroup, text="M.I.", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).pack(anchor="w", pady=(0, 2))
                miBorder = tk.Frame(miGroup, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
                miBorder.pack()
                MI_Entry = tk.Entry(miBorder, bg=WHITE, fg=BLACK, font=UNIFORM_FONT, relief="flat", bd=0, width=3)
                MI_Entry.pack(padx=5, pady=4)
                MI_Entry.insert(0, mi_segment.strip())

                emailGroup = tk.Frame(midFrame, bg=WHITE)
                emailGroup.grid(row=3, column=0, sticky="we", padx=(0, 6), pady=(0, 15))
                tk.Label(emailGroup, text="Email", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).pack(anchor="w", pady=(0, 2))
                emailBorder = tk.Frame(emailGroup, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
                emailBorder.pack(fill="x")
                emailEntry = tk.Entry(emailBorder, bg=WHITE, fg=BLACK, font=UNIFORM_FONT, relief="flat", bd=0)
                emailEntry.pack(fill="x", padx=5, pady=4)
                emailEntry.insert(0, email.get())

                contactGroup = tk.Frame(midFrame, bg=WHITE)
                contactGroup.grid(row=3, column=1, columnspan=2, sticky="we", padx=(6, 0), pady=(0, 15))
                tk.Label(contactGroup, text="Contact Number", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).pack(anchor="w", pady=(0, 2))
                contactBorder = tk.Frame(contactGroup, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
                contactBorder.pack(fill="x")
                contactEntry = tk.Entry(contactBorder, bg=WHITE, fg=BLACK, font=UNIFORM_FONT, relief="flat", bd=0)
                contactEntry.pack(fill="x", padx=5, pady=4)
                contactEntry.insert(0, contact.get())

                bottomFrame = tk.Frame(editStaff, bg=content_color)
                bottomFrame.pack(fill="x", padx=15, pady=15)
                tk.Button(bottomFrame, text="Save Changes", font=UNIFORM_FONT,
                        command=update_staff).pack(side="right", padx=(5, 0))
                tk.Button(bottomFrame, text="Cancel", fg="#c0392b", font=UNIFORM_FONT,
                        command=editStaff.destroy).pack(side="right")

            def load_data():
                for row in self.cleaning_tree.get_children():
                    self.cleaning_tree.delete(row)
                self.db.get_all_cleaning_staff(self.cleaning_tree)

            def clear_fields():
                cs_ID.set("")
                last.set("")
                first.set("")
                mi.set("")
                email.set("")
                contact.set("")
                full_name.set("")
                
            def delete_cleaning_staff():
                selected_id = cs_ID.get()
                if not selected_id:
                    messagebox.showwarning("Selection Required", "Please click a cleaning staff record from the table first.")
                    return
                    
                confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to permanently delete Staff ID: {selected_id}?")
                if confirm:
                    try:
                        con = sqlite3.connect(DB_NAME)
                        cur = con.cursor()
                        cur.execute("DELETE FROM cleaningStaff WHERE cs_ID=?", (cs_ID.get(),))
                        con.commit()
                        con.close()
                        load_data()
                        clear_fields()
                    except Exception as e:
                        messagebox.showerror("Database Error", f"Failed to execute row deletion:\n{e}")

            def CSassign_window():
                assign = tk.Toplevel()
                assign.title("Assign Cleaning")
                assign.config(bg=content_color)
                assign.geometry("420x360")
                assign.resizable(False, False)
                assign.grab_set()

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

                err_label = tk.Label(assign, text="", fg="#c0392b", bg=content_color, font=UNIFORM_FONT)
                err_label.pack()

                def confirm_assign():
                    room  = roomSelection.get().strip()
                    date  = dateEntry.get().strip()
                    t_start = timeStartEntry.get().strip()
                    t_end   = timeEndEntry.get().strip()

                    if not room:
                        err_label.config(text="Please select a room.")
                        return
                    if not date:
                        err_label.config(text="Please enter a date.")
                        return
                    if not t_start or not t_end:
                        err_label.config(text="Please enter both start and end times.")
                        return

                    try:
                        con = sqlite3.connect(DB_NAME)
                        cur = con.cursor()
                        cur.execute("""
                            CREATE TABLE IF NOT EXISTS cleaning_schedule (
                                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                                cs_ID     VARCHAR(255),
                                room      VARCHAR(255),
                                date      VARCHAR(255),
                                time_start VARCHAR(255),
                                time_end  VARCHAR(255)
                            )
                        """)
                        cur.execute(
                            "INSERT INTO cleaning_schedule (cs_ID, room, date, time_start, time_end) VALUES (?, ?, ?, ?, ?)",
                            (cs_ID.get(), room, date, t_start, t_end)
                        )
                        con.commit()
                        con.close()
                        messagebox.showinfo("Success", "Cleaning schedule assigned successfully.")
                        assign.destroy()
                    except Exception as e:
                        err_label.config(text=f"Error: {e}")

                bottomFrame = tk.Frame(assign, bg=content_color)
                bottomFrame.pack(fill="x", padx=15, pady=15)
                tk.Button(bottomFrame, text="Confirm",
                        font=UNIFORM_FONT, bg=BLACK, fg=WHITE, relief="flat",
                        padx=12, pady=5, cursor="hand2",
                        command=confirm_assign).pack(side="right", padx=(5, 0))
                tk.Button(bottomFrame, text="Cancel", fg="#c0392b",
                        font=UNIFORM_FONT, relief="flat", padx=12, pady=5,
                        cursor="hand2", command=assign.destroy).pack(side="right")

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

            self.cleaning_tree = ttk.Treeview(tree_frame,
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

            # Connect event to selection processor function
            self.cleaning_tree.bind("<ButtonRelease-1>", select_record)

            tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=16, pady=(6, 0))

            btnFrame = tk.Frame(card, bg=WHITE)
            btnFrame.pack(fill="x", padx=16, pady=10)

            btn_cfg = dict(bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT,
                        relief="solid", bd=1, padx=14, pady=5, cursor="hand2")
            tk.Button(btnFrame, text="✏  Edit", command=edit_cleaning_stuff,
                    **btn_cfg).pack(side="right", padx=4)
            tk.Button(btnFrame, text="⊞  Assign Cleaning",
                    command=CSassign_window, **btn_cfg).pack(side="right", padx=4)
            tk.Button(btnFrame, text="🗑  Delete", command=delete_cleaning_staff,
                    bg=WHITE, fg="#c0392b", font=UNIFORM_FONT,
                    relief="solid", bd=1, padx=14, pady=5,
                    cursor="hand2").pack(side="right", padx=4)

            tk.Label(card, text="ⓘ  Click a row to select before editing, assigning, or deleting.",
                    bg=WHITE, fg=FG_MUTED, font=("Segoe UI", 8),
                    anchor="w").pack(fill="x", padx=20, pady=(0, 10))

            self.db.get_all_cleaning_staff(self.cleaning_tree)
    # ── Settings page ─────────────────────────────────────────────────
    def build_settings_page(self, page):
        # ── Top bar ───────────────────────────────────────────────────────
        topbar = tk.Frame(page, bg=content_color)
        topbar.pack(fill="x", padx=28, pady=(20, 12))
        tk.Label(topbar, text="Settings", bg=content_color, fg=FG_DARK,
                font=("Segoe UI", 17, "bold")).pack(side="left")

        # ── Card ──────────────────────────────────────────────────────────
        card = tk.Frame(page, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="both", expand=True, padx=28, pady=(0, 20))

        # ── Section title ─────────────────────────────────────────────────
        tk.Label(card, text="Admin Accounts", bg=WHITE, fg=FG_DARK,
                font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=16, pady=(14, 4))
        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=16)

        # ── Treeview ──────────────────────────────────────────────────────
        tree_frame = tk.Frame(card, bg=WHITE)
        tree_frame.pack(fill="both", expand=True, padx=16, pady=(10, 0))

        style = ttk.Style()
        style.configure("Settings.Treeview", background=WHITE, foreground=FG_DARK,
                        rowheight=34, fieldbackground=WHITE, borderwidth=0, font=UNIFORM_FONT)
        style.configure("Settings.Treeview.Heading", background=HEADER_BG, foreground="#555577",
                        font=("Segoe UI", 9, "bold"), relief="flat", padding=(8, 6))
        style.map("Settings.Treeview",
                background=[("selected", ROW_SEL)],
                foreground=[("selected", FG_DARK)])
        style.layout("Settings.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

        self.settings_tree = ttk.Treeview(tree_frame, columns=("username", "password"),
                                        show="headings", style="Settings.Treeview",
                                        selectmode="browse", height=6)
        self.settings_tree.heading("username", text="Username", anchor="w")
        self.settings_tree.heading("password", text="Password", anchor="w")
        self.settings_tree.column("username", width=220, anchor="w", stretch=True)
        self.settings_tree.column("password", width=220, anchor="w", stretch=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.settings_tree.yview)
        self.settings_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.settings_tree.pack(side="left", fill="both", expand=True)

        # ── Entry fields ──────────────────────────────────────────────────
        fields_frame = tk.Frame(card, bg=WHITE)
        fields_frame.pack(fill="x", padx=16, pady=(14, 0))
        fields_frame.columnconfigure(0, weight=1)
        fields_frame.columnconfigure(1, weight=1)

        tk.Label(fields_frame, text="Username", bg=WHITE, fg=FG_DARK,
                font=UNIFORM_FONT).grid(row=0, column=0, sticky="w", padx=(0, 8), pady=(0, 2))
        tk.Label(fields_frame, text="Password", bg=WHITE, fg=FG_DARK,
                font=UNIFORM_FONT).grid(row=0, column=1, sticky="w", pady=(0, 2))

        user_border = tk.Frame(fields_frame, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        user_border.grid(row=1, column=0, sticky="we", padx=(0, 8), pady=(0, 12))
        user_entry = tk.Entry(user_border, bg=WHITE, fg=BLACK, font=UNIFORM_FONT,
                            relief="flat", bd=0, insertbackground=FG_DARK)
        user_entry.pack(fill="x", padx=5, pady=4)

        pass_border = tk.Frame(fields_frame, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        pass_border.grid(row=1, column=1, sticky="we", pady=(0, 12))
        pass_entry = tk.Entry(pass_border, bg=WHITE, fg=BLACK, font=UNIFORM_FONT,
                            relief="flat", bd=0, insertbackground=FG_DARK, show="*")
        pass_entry.pack(fill="x", padx=5, pady=4)

        # ── Populate entries on row select ────────────────────────────────
        def on_select(event):
            selected = self.settings_tree.focus()
            if selected:
                values = self.settings_tree.item(selected, "values")
                user_entry.delete(0, "end")
                pass_entry.delete(0, "end")
                user_entry.insert(0, values[0])
                pass_entry.insert(0, values[1])

        self.settings_tree.bind("<ButtonRelease-1>", on_select)

        # ── Action buttons ────────────────────────────────────────────────
        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=16, pady=(0, 0))

        btn_bar = tk.Frame(card, bg=WHITE)
        btn_bar.pack(fill="x", padx=16, pady=10)

        def add_user():
            username = user_entry.get().strip()
            password = pass_entry.get().strip()
            if not username or not password:
                return
            self.settings_tree.insert("", "end", values=(username, password))
            user_entry.delete(0, "end")
            pass_entry.delete(0, "end")

        def edit_user():
            selected = self.settings_tree.focus()
            if not selected:
                return
            username = user_entry.get().strip()
            password = pass_entry.get().strip()
            if not username or not password:
                return
            self.settings_tree.item(selected, values=(username, password))

        def delete_user():
            selected = self.settings_tree.focus()
            if not selected:
                return
            self.settings_tree.delete(selected)
            user_entry.delete(0, "end")
            pass_entry.delete(0, "end")

        btn_cfg = dict(bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT,
                    relief="solid", bd=1, padx=14, pady=5, cursor="hand2")
        tk.Button(btn_bar, text="＋  Add",    command=add_user,    **btn_cfg).pack(side="left", padx=(0, 6))
        tk.Button(btn_bar, text="✏  Edit",   command=edit_user,   **btn_cfg).pack(side="left", padx=6)
        tk.Button(btn_bar, text="🗑  Delete", command=delete_user,
                bg=WHITE, fg="#c0392b", font=UNIFORM_FONT,
                relief="solid", bd=1, padx=14, pady=5,
                cursor="hand2").pack(side="left", padx=6)
        
        tk.Button(btn_bar, text="⏻  Log Out",
                bg="#c0392b", fg=WHITE, font=UNIFORM_FONT,
                relief="flat", padx=14, pady=5, cursor="hand2",
                command=self.destroy).pack(side="right")

if __name__ == "__main__":
    app = main()
    app.mainloop()
