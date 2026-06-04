import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
import sqlite3
import re

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


# ══════════════════════════════════════════════════════════════════════
#  DATABASE LAYER
# ══════════════════════════════════════════════════════════════════════
class Database:

    # ── Dashboard ─────────────────────────────────────────────────────
    def for_dashboard(self):
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute("SELECT COUNT(*) FROM students")
            total_students = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM rooms")
            total_rooms = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM rooms WHERE occupants > 0")
            rooms_occupied = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM cleaningStaff")
            total_cleaning_staff = cur.fetchone()[0]
            return total_students, total_rooms, rooms_occupied, total_cleaning_staff

    # ── Students ──────────────────────────────────────────────────────
    def create_student_table(self):
        with sqlite3.connect(DB_NAME) as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    student_no      VARCHAR(255) PRIMARY KEY,
                    last_name       VARCHAR(255) NOT NULL,
                    first_name      VARCHAR(255) NOT NULL,
                    middle_initial  VARCHAR(255),
                    program         VARCHAR(255) NOT NULL,
                    status          VARCHAR(255) NOT NULL,
                    contact         VARCHAR(255) NOT NULL,
                    room            VARCHAR(255) DEFAULT '',
                    building        VARCHAR(255) DEFAULT ''
                )
            """)
            con.commit()

    def add_student(self, student_no, last, first, mi, program, status, contact):
        with sqlite3.connect(DB_NAME) as con:
            con.execute(
                "INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (student_no, last, first, mi, program, status, contact, "", "")
            )
            con.commit()

    def get_all_students(self, tree):
        for row in tree.get_children():
            tree.delete(row)
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute("""
                SELECT student_no,
                    TRIM(first_name || ' ' || COALESCE(middle_initial || '. ', '') || last_name),
                    program, contact, building, room, status
                FROM students
            """)
            for row in cur.fetchall():
                tree.insert("", "end", values=row)

    def update_student(self, original_no, student_no, last, first, mi, program, status, contact):
        with sqlite3.connect(DB_NAME) as con:
            con.execute("""
                UPDATE students
                SET student_no=?, last_name=?, first_name=?, middle_initial=?,
                    program=?, status=?, contact=?
                WHERE student_no=?
            """, (student_no, last, first, mi, program, status, contact, original_no))
            con.commit()

    def delete_student(self, student_no):
        with sqlite3.connect(DB_NAME) as con:
            con.execute("DELETE FROM students WHERE student_no=?", (student_no,))
            con.commit()

    def migrate_students_table(self):
        with sqlite3.connect(DB_NAME) as con:
            try:
                con.execute("ALTER TABLE students ADD COLUMN room VARCHAR(255) DEFAULT ''")
                con.execute("ALTER TABLE students ADD COLUMN building VARCHAR(255) DEFAULT ''")
                con.commit()
            except Exception:
                pass

    def assign_room_to_student(self, student_no, room, building):
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute("UPDATE students SET room=?, building=? WHERE student_no=?",
                        (room, building, student_no))
            cur.execute("UPDATE rooms SET occupants = occupants + 1 WHERE room_number=? AND building=?",
                        (room, building))
            cur.execute("""UPDATE rooms SET status='Occupied'
                           WHERE room_number=? AND building=? AND occupants >= capacity""",
                        (room, building))
            con.commit()

    def remove_student_from_room(self, student_no):
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute("SELECT room, building FROM students WHERE student_no=?", (student_no,))
            row = cur.fetchone()
            if row and row[0] and row[1]:
                room, building = row
                cur.execute("UPDATE rooms SET occupants = MAX(0, occupants - 1) WHERE room_number=? AND building=?",
                            (room, building))
                cur.execute("""UPDATE rooms SET status='Vacant'
                               WHERE room_number=? AND building=? AND occupants < capacity AND status='Occupied'""",
                            (room, building))
                cur.execute("UPDATE students SET room='', building='' WHERE student_no=?", (student_no,))
            con.commit()

    def seed_sample_students(self):
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute("SELECT COUNT(*) FROM students")
            if cur.fetchone()[0] > 0:
                return
            sample = [
                ("2021-00001", "Reyes",      "Maria",    "S", "BSCS",  "Active",   "09171234567"),
                ("2021-00002", "Santos",     "Juan",     "D", "BSIT",  "Active",   "09189876543"),
                ("2021-00003", "Dela Cruz",  "Anna",     "L", "BSN",   "Active",   "09201112222"),
                ("2021-00004", "Garcia",     "Carlo",    "M", "BSEE",  "Inactive", "09333334444"),
                ("2021-00005", "Torres",     "Patricia", "R", "BSME",  "On Leave", "09455556666"),
                ("2022-00001", "Villanueva", "Miguel",   "A", "BSCS",  "Active",   "09567778888"),
                ("2022-00002", "Castillo",   "Sophia",   "B", "BSIT",  "Active",   "09689990000"),
                ("2022-00003", "Morales",    "Andres",   "C", "BSCE",  "Active",   "09701231234"),
                ("2022-00004", "Navarro",    "Isabella", "P", "BSN",   "Inactive", "09823454567"),
                ("2022-00005", "Mendoza",    "Luis",     "T", "BSBA",  "Active",   "09945677890"),
            ]
            cur.executemany(
                "INSERT OR IGNORE INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [(s[0], s[1], s[2], s[3], s[4], s[5], s[6], "", "") for s in sample]
            )
            con.commit()

    # ── Rooms ─────────────────────────────────────────────────────────
    def create_rooms_table(self):
        with sqlite3.connect(DB_NAME) as con:
            con.execute("""
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
            con.commit()

    def add_room(self, building, room_number, room_type, capacity, status):
        with sqlite3.connect(DB_NAME) as con:
            con.execute(
                "INSERT INTO rooms (building, room_number, room_type, capacity, status) VALUES (?, ?, ?, ?, ?)",
                (building, room_number, room_type, capacity, status)
            )
            con.commit()

    def get_all_rooms(self, tree):
        for row in tree.get_children():
            tree.delete(row)
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute("SELECT room_id, room_number, building, room_type, capacity, occupants, status, last_cleaned FROM rooms")
            for row in cur.fetchall():
                tree.insert("", "end", values=row[1:], tags=(row[0],))

    def update_room(self, room_id, building, room_number, room_type, capacity, status):
        with sqlite3.connect(DB_NAME) as con:
            con.execute("""
                UPDATE rooms SET building=?, room_number=?, room_type=?, capacity=?, status=?
                WHERE room_id=?
            """, (building, room_number, room_type, capacity, status, room_id))
            con.commit()

    def delete_room(self, room_id):
        with sqlite3.connect(DB_NAME) as con:
            con.execute("DELETE FROM rooms WHERE room_id=?", (room_id,))
            con.commit()

    def get_distinct_buildings(self):
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute("SELECT DISTINCT building FROM rooms ORDER BY building")
            return [row[0] for row in cur.fetchall()]

    def get_rooms_by_building(self, building):
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute("""
                SELECT room_number FROM rooms
                WHERE building=? AND occupants <= capacity AND status != 'Under Maintenance'
                ORDER BY room_number
            """, (building,))
            return [row[0] for row in cur.fetchall()]

    # ── Cleaning Staff ────────────────────────────────────────────────
    def create_table_cleaning_staff(self):
        with sqlite3.connect(DB_NAME) as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS cleaningStaff (
                    cs_ID          VARCHAR(255) PRIMARY KEY,
                    last_name      VARCHAR(255) NOT NULL,
                    first_name     VARCHAR(255) NOT NULL,
                    middle_initial VARCHAR(255),
                    email          VARCHAR(255) UNIQUE NOT NULL,
                    contact        VARCHAR(255) NOT NULL,
                    full_name      VARCHAR(255) NOT NULL
                )
            """)
            con.commit()

    def insert_cleaning_staff(self, cs_ID, last, first, mi, email, contact, full_name):
        with sqlite3.connect(DB_NAME) as con:
            con.execute(
                "INSERT INTO cleaningStaff VALUES (?, ?, ?, ?, ?, ?, ?)",
                (cs_ID, last, first, mi, email, contact, full_name)
            )
            con.commit()

    def update_cleaning_staff(self, cs_ID, last, first, mi, email, contact, full_name):
        with sqlite3.connect(DB_NAME) as con:
            con.execute("""
                UPDATE cleaningStaff
                SET last_name=?, first_name=?, middle_initial=?, email=?, contact=?, full_name=?
                WHERE cs_ID=?
            """, (last, first, mi, email, contact, full_name, cs_ID))
            con.commit()

    def delete_cleaning_staff(self, cs_ID):
        with sqlite3.connect(DB_NAME) as con:
            con.execute("DELETE FROM cleaningStaff WHERE cs_ID=?", (cs_ID,))
            # also remove all their schedules
            con.execute("DELETE FROM cleaning_schedule WHERE cs_ID=?", (cs_ID,))
            con.commit()

    def get_all_cleaning_staff(self, tree):
        """Master list: one row per staff member with assignment count."""
        for row in tree.get_children():
            tree.delete(row)
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute("""
                        SELECT cs.cs_ID, cs.full_name, cs.contact, cs.email,
                            COUNT(sch.id) AS assignments
                        FROM cleaningStaff cs
                        LEFT JOIN cleaning_schedule sch 
                            ON cs.cs_ID = sch.cs_ID
                            AND date(
                                printf('%04d-%02d-%02d', 
                                    CAST(sch.year AS INT), 
                                    CAST(sch.month AS INT), 
                                    CAST(sch.day AS INT))
                            ) >= date('now')
                        GROUP BY cs.cs_ID
                        ORDER BY cs.full_name
                    """)

            for row in cur.fetchall():
                tree.insert("", "end", values=row)

    # ── Cleaning Schedule ─────────────────────────────────────────────
    def create_cleaning_schedule_table(self):
        with sqlite3.connect(DB_NAME) as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS cleaning_schedule (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    cs_ID      VARCHAR(255) NOT NULL,
                    building   VARCHAR(255) NOT NULL,
                    room       VARCHAR(255) NOT NULL,
                    month      VARCHAR(255) NOT NULL,
                    day        VARCHAR(255) NOT NULL,
                    year       VARCHAR(255) NOT NULL,
                    time_start VARCHAR(255) NOT NULL,
                    time_end   VARCHAR(255) NOT NULL
                )
            """)
            con.commit()

    def get_schedules_for_staff(self, cs_ID, tree):
        """Detail panel: all schedule rows for one staff member."""
        for row in tree.get_children():
            tree.delete(row)
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute("""
                SELECT id, building, room,
                       month || '/' || day || '/' || year,
                       time_start, time_end
                FROM cleaning_schedule
                WHERE cs_ID=?
                ORDER BY year, month, day, time_start
            """, (cs_ID,))
            for i, row in enumerate(cur.fetchall(), start=1):
                sched_id = row[0]
                values   = (i,) + row[1:]    # prepend row number; store sched_id as tag
                tree.insert("", "end", values=values, tags=(sched_id,))

    def add_schedule(self, cs_ID, building, room, month, day, year, time_start, time_end):
        with sqlite3.connect(DB_NAME) as con:
            con.execute("""
                INSERT INTO cleaning_schedule (cs_ID, building, room, month, day, year, time_start, time_end)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (cs_ID, building, room, month, day, year, time_start, time_end))
            con.commit()

    def delete_schedule(self, sched_id):
        with sqlite3.connect(DB_NAME) as con:
            con.execute("DELETE FROM cleaning_schedule WHERE id=?", (sched_id,))
            con.commit()

    #============================================================
    #new add for dashboard

    def get_assigned_students(self):
        with sqlite3.connect(DB_NAME) as connect:
            cursor = connect.cursor()
            cursor.execute("""
                SELECT first_name || ' ' || last_name, building, room, status
                FROM students
                WHERE room != '' AND room IS NOT NULL
                ORDER BY building, room
            """)
            return cursor.fetchall()

    def get_todays_cleaning_assignments(self):
        from datetime import datetime
        today = datetime.now()
        with sqlite3.connect(DB_NAME) as connect:
            cursor = connect.cursor()
            cursor.execute("""
                SELECT cs.cs_ID, cs.full_name,
                    sch.building || ' ' || sch.room,
                    sch.time_start, sch.time_end
                FROM cleaning_schedule sch
                JOIN cleaningStaff cs ON cs.cs_ID = sch.cs_ID
                WHERE CAST(sch.month AS INT) = ?
                AND CAST(sch.day   AS INT) = ?
                AND CAST(sch.year  AS INT) = ?
                ORDER BY sch.time_start
            """, (today.month, today.day, today.year))
            return cursor.fetchall()

    


# ══════════════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ══════════════════════════════════════════════════════════════════════
class main(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("1200x650")
        self.minsize(1150, 650)
        self.title("Dormi Admin Panel")

        self.db = Database()
        self.db.create_student_table()
        self.db.create_rooms_table()
        self.db.create_table_cleaning_staff()
        self.db.create_cleaning_schedule_table()
        self.db.migrate_students_table()
        
        self.db.seed_sample_students()

        self.all_pages   = []
        self.all_buttons = []

        # Will hold the cs_ID of whichever staff row is selected
        self._selected_cs_id = None

        self.main_build_layout()
        self.refresh_dashboard()

    # ── Layout ────────────────────────────────────────────────────────
    def main_build_layout(self):
        self.sidebar = tk.Frame(self, bg=sidebar_color, width=300)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="Dormi",       bg=sidebar_color, fg=font_color_sidebar,
                 font=("Arial", 14, "bold")).pack(anchor="w", padx=15, pady=(20, 0))
        tk.Label(self.sidebar, text="Admin panel", bg=sidebar_color, fg=font_color_sidebar,
                 font=("Arial", 9)).pack(anchor="w", padx=15, pady=(0, 20))

        content = tk.Frame(self, bg=content_color)
        content.pack(side="left", fill="both", expand=True)

        self.dashboard_page = tk.Frame(content, bg=content_color)
        self.students_page  = tk.Frame(content, bg=content_color)
        self.rooms_page     = tk.Frame(content, bg=content_color)
        self.cleaning_page  = tk.Frame(content, bg=content_color)
        

        self.build_dashboard_page(self.dashboard_page)
        self.build_students_page(self.students_page)
        self.build_rooms_page(self.rooms_page)
        self.build_cleaning_page(self.cleaning_page)
        

        self.all_pages = [
            self.dashboard_page, self.students_page, self.rooms_page,
            self.cleaning_page
        ]

        tk.Label(self.sidebar, text="MAIN", bg=sidebar_color, fg=font_color_sidebar,
                 font=("Arial", 8)).pack(anchor="w", padx=15, pady=(5, 2))

        self.dashboardButton = tk.Button(self.sidebar, text="  Dashboard",
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



        self.all_buttons = [
            self.dashboardButton, self.studentButton, self.roomsButton,
            self.cleaningButton
        ]

        self.dashboardButton.config(command=lambda: self.show_page(self.dashboard_page, self.dashboardButton))
        self.studentButton.config(  command=lambda: self.show_page(self.students_page,  self.studentButton))
        self.roomsButton.config(    command=lambda: self.show_page(self.rooms_page,     self.roomsButton))
        self.cleaningButton.config( command=lambda: self.show_page(self.cleaning_page,  self.cleaningButton))
        

        self.show_page(self.dashboard_page, self.dashboardButton)

        hover_color = "#BE9C7C"

        def bind_hover(btn):
            def on_enter(e):
                if btn.cget("bg") != active_color:
                    btn.config(bg=hover_color)
            def on_leave(e):
                if btn.cget("bg") != active_color:
                    btn.config(bg=sidebar_color)
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)

        for btn in self.all_buttons:
            bind_hover(btn)
        
        #LOGOUT BUTTON
        tk.Button(self.sidebar, text="⏻  Log Out",
          bg="#c0392b", fg="white", font=("Arial", 10),
          relief="flat", anchor="w", padx=10, pady=8,
          cursor="hand2", command=self.destroy).pack(
              side="bottom", fill="x", padx=10, pady=(0, 15))

    def refresh_dashboard(self):
        ts, tr, tro, tc = self.db.for_dashboard()
        self.tsNum.config(text=str(ts))
        self.trNum.config(text=str(tr))
        self.troNum.config(text=str(tro))
        self.tcNum.config(text=str(tc))

        # Recent student assignments # NEWLY ADDED ____________________________________________________________________________________--
        for row in self.treeStuAss.get_children():
            self.treeStuAss.delete(row)
        for row in self.db.get_assigned_students():
            self.treeStuAss.insert("", "end", values=row)

        # Today's cleaning assignments
        for row in self.treeCleanAss.get_children():
            self.treeCleanAss.delete(row)
        for row in self.db.get_todays_cleaning_assignments():
            self.treeCleanAss.insert("", "end", values=row)

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

        def make_card(parent, accent, emoji, num_attr, label_text):
            frame = tk.Frame(parent, width=200, height=150, bg="white",
                             highlightbackground="#d0c4b0", highlightthickness=1)
            frame.pack(side="left", padx=(0, 10), fill="x", expand=True)
            frame.pack_propagate(False)
            tk.Frame(frame, bg=accent, width=5).pack(side="left", fill="y")
            inner = tk.Frame(frame, bg="white")
            inner.pack(side="left", fill="both", expand=True)
            tk.Label(inner, text=emoji, font=("Arial", 24), bg="white", fg=accent).pack(anchor="w", padx=10, pady=(10, 0))
            num_lbl = tk.Label(inner, text="0", font=("Arial", 24, "bold"), bg="white", fg=accent)
            num_lbl.pack(anchor="w", padx=10)
            tk.Label(inner, text=label_text, font=("Arial", 13), bg="white", fg=accent).pack(anchor="w", padx=10, pady=(2, 0))
            return num_lbl

        self.tsNum  = make_card(cards_frame, "#8A5F41", "🧑",  "tsNum",  "Total students")
        self.trNum  = make_card(cards_frame, "#4A8C7A", "🛏️", "trNum",  "Total rooms")
        self.troNum = make_card(cards_frame, "#C48B2A", "🛌", "troNum", "Rooms occupied")
        self.tcNum  = make_card(cards_frame, "#A05C6A", "🧹",  "tcNum",  "Cleaning staff")

        tk.Label(page, text="Recent student assignments", bg=content_color,
                 font=("Arial", 12, "bold"), fg="black").pack(anchor="w", pady=5, padx=30)

        self.treeStuAss = ttk.Treeview(page, columns=("Student", "Building", "Room", "Status"), show="headings")
        for col, w in [("Student", 150), ("Building", 50), ("Room", 50), ("Status", 75)]:
            self.treeStuAss.heading(col, text=col)
            self.treeStuAss.column(col, width=w)
        self.treeStuAss.pack(fill="both", padx=20, pady=10)

        tk.Label(page, text="Cleaning assignments today", bg=content_color,
                 font=("Arial", 12, "bold"), fg="black").pack(anchor="w", pady=5, padx=30)

        self.treeCleanAss = ttk.Treeview(page, columns=("ID", "StaffName", "Room", "TimeStart", "TimeEnd"), show="headings")
        for col, w in [("ID", 50), ("StaffName", 150), ("Room", 50), ("TimeStart", 75), ("TimeEnd", 75)]:
            self.treeCleanAss.heading(col, text=col)
            self.treeCleanAss.column(col, width=w)
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

            def make_entry(parent, row, col, colspan=1, padx=(0, 0), width=None):
                border = tk.Frame(parent, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
                border.grid(row=row, column=col, columnspan=colspan, sticky="we",
                            padx=padx, pady=(0, 10))
                kw = dict(bg=WHITE, fg=BLACK, font=UNIFORM_FONT, relief="flat", bd=0)
                if width:
                    kw["width"] = width
                e = tk.Entry(border, **kw)
                e.pack(fill="x", padx=5, pady=3)
                return e

            tk.Label(midFrame, text="Student No.", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 2))
            e_no = make_entry(midFrame, 1, 0, colspan=3)

            for col, txt in [(0, "Last Name"), (1, "First Name"), (2, "M.I.")]:
                tk.Label(midFrame, text=txt, bg=WHITE, fg=FG_DARK,
                         font=UNIFORM_FONT).grid(row=2, column=col, sticky="w",
                                                 padx=((0, 6) if col == 0 else (6, 6) if col == 1 else (6, 0)),
                                                 pady=(0, 2))
            e_last  = make_entry(midFrame, 3, 0, padx=(0, 6))
            e_first = make_entry(midFrame, 3, 1, padx=(6, 6))
            e_mi    = make_entry(midFrame, 3, 2, padx=(6, 0), width=3)

            tk.Label(midFrame, text="Program", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).grid(row=4, column=0, sticky="w", padx=(0, 6), pady=(0, 2))
            tk.Label(midFrame, text="Status",  bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).grid(row=4, column=1, sticky="w", padx=6,      pady=(0, 2))
            e_program = make_entry(midFrame, 5, 0, padx=(0, 6))

            statusVar = tk.StringVar()
            statusDrop = ttk.Combobox(midFrame, textvariable=statusVar,
                                      values=["Active", "Inactive", "On Leave"],
                                      state="readonly", font=UNIFORM_FONT)
            statusDrop.grid(row=5, column=1, columnspan=2, sticky="we", padx=(6, 0), pady=(0, 10))
            statusDrop.current(0)

            tk.Label(midFrame, text="Contact", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).grid(row=6, column=0, columnspan=3, sticky="w", pady=(0, 2))
            e_contact = make_entry(midFrame, 7, 0, colspan=3)

            if prefill:
                e_no.insert(0,      prefill[0])
                e_program.insert(0, prefill[2])
                e_contact.insert(0, prefill[3])
                statusVar.set(      prefill[6])
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

                limits = [(no, 20, "Student No."), (last, 50, "Last Name"),
                          (first, 50, "First Name"), (mi, 2, "Middle Initial"),
                          (program, 10, "Program"), (contact, 15, "Contact")]
                for value, limit, lbl in limits:
                    if len(value) > limit:
                        err_label.config(text=f"{lbl} exceeds {limit} character limit.")
                        return

                for value, lbl in [(last, "Last Name"), (first, "First Name"),
                                   (mi, "Middle Initial"), (program, "Program")]:
                    if value and not re.match(r"^[A-Za-z\s]+$", value):
                        err_label.config(text=f"{lbl} must contain letters only.")
                        return

                if not no or not last or not first:
                    err_label.config(text="Student No., Last Name and First Name are required.")
                    return

                full_name = f"{first} {f'{mi}. ' if mi else ''}{last}".strip()

                if edit_item:
                    original_no = self.tree.item(edit_item, "values")[0]
                    old_values  = self.tree.item(edit_item, "values")
                    self.db.update_student(original_no, no, last, first, mi, program, status, contact)
                    self.tree.item(edit_item, values=(
                        no, full_name, program, contact,
                        old_values[4], old_values[5], status
                    ))
                else:
                    self.db.add_student(no, last, first, mi, program, status, contact)
                    self.tree.insert("", "end", values=(no, full_name, program, contact, "", "", status))

                update_count()
                self.refresh_dashboard()
                win.destroy()

            bottomFrame = tk.Frame(win, bg=content_color)
            bottomFrame.pack(fill="x", padx=15, pady=(0, 20))
            tk.Button(bottomFrame, text="Save",   font=UNIFORM_FONT, bg=BLACK, fg=WHITE,
                      relief="flat", padx=12, pady=0, cursor="hand2",
                      command=save).pack(side="right", padx=5)
            tk.Button(bottomFrame, text="Cancel", font=UNIFORM_FONT, fg="#c0392b",
                      relief="flat", padx=12, pady=0, cursor="hand2",
                      command=win.destroy).pack(side="right", padx=5)

        def delete_student():
            selected = self.tree.selection()
            if not selected:
                messagebox.showwarning("Selection Required", "Please click a student record from the table first.")
                return
            if messagebox_confirm("Delete this student? This cannot be undone."):
                student_no = self.tree.item(selected[0], "values")[0]
                self.db.remove_student_from_room(student_no)
                self.db.delete_student(student_no)
                self.tree.delete(selected[0])
                self.db.get_all_rooms(self.rooms_tree)
                update_count()
                self.refresh_dashboard()

        def edit_student():
            selected = self.tree.selection()
            if not selected:
                messagebox.showwarning("Selection Required", "Please click a student record from the table first.")
                return
            add_student_window(prefill=self.tree.item(selected[0], "values"), edit_item=selected[0])

        def assign_room():
            selected = self.tree.selection()
            if not selected:
                messagebox.showwarning("Selection Required", "Please click a student record from the table first.")
                return
            values = self.tree.item(selected[0], "values")

            win = tk.Toplevel()
            win.title("Assign Room")
            win.config(bg=content_color)
            win.geometry("360x400")
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
                     font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 12))

            tk.Label(midFrame, text="Building", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).grid(row=1, column=0, sticky="w", pady=(0, 4))
            buildingVar = tk.StringVar()
            buildingDrop = ttk.Combobox(midFrame, textvariable=buildingVar,
                                        values=self.db.get_distinct_buildings(),
                                        state="readonly", font=UNIFORM_FONT)
            buildingDrop.grid(row=2, column=0, sticky="we", pady=(0, 12))

            tk.Label(midFrame, text="Select Room", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).grid(row=3, column=0, sticky="w", pady=(0, 4))
            roomVar = tk.StringVar()
            roomDrop = ttk.Combobox(midFrame, textvariable=roomVar, values=[],
                                    state="readonly", font=UNIFORM_FONT)
            roomDrop.grid(row=4, column=0, sticky="we", pady=(0, 12))

            def on_building_change(event):
                rooms = self.db.get_rooms_by_building(buildingVar.get())
                roomDrop.config(values=rooms)
                if rooms:
                    roomDrop.current(0)
                else:
                    roomVar.set("")

            buildingDrop.bind("<<ComboboxSelected>>", on_building_change)

            tk.Label(midFrame, text="Status", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).grid(row=5, column=0, sticky="w", pady=(0, 4))
            statusVar2 = tk.StringVar()
            statusDrop2 = ttk.Combobox(midFrame, textvariable=statusVar2,
                                       values=["Active", "Inactive", "On Leave"],
                                       state="readonly", font=UNIFORM_FONT)
            statusDrop2.grid(row=6, column=0, sticky="we")
            statusVar2.set(values[6] if values[6] else "Active")

            def save_room():
                if not buildingVar.get() or not roomVar.get():
                    return
                self.db.assign_room_to_student(values[0], roomVar.get(), buildingVar.get())
                self.db.get_all_rooms(self.rooms_tree)
                self.tree.item(selected[0], values=(
                    values[0], values[1], values[2], values[3],
                    buildingVar.get(), roomVar.get(), statusVar2.get()
                ))
                self.refresh_dashboard()
                win.destroy()

            bottomFrame = tk.Frame(win, bg=content_color)
            bottomFrame.pack(fill="x", padx=15, pady=10)
            tk.Button(bottomFrame, text="Assign", font=UNIFORM_FONT, bg=BLACK, fg=WHITE,
                      relief="flat", padx=12, pady=5, cursor="hand2",
                      command=save_room).pack(side="right", padx=(5, 0))
            tk.Button(bottomFrame, text="Cancel", font=UNIFORM_FONT, fg="#c0392b",
                      relief="flat", padx=12, pady=5, cursor="hand2",
                      command=win.destroy).pack(side="right")

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
                      relief="flat", padx=14, pady=4, cursor="hand2",
                      command=confirm).pack(side="left", padx=6)
            tk.Button(btn_row, text="Cancel", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT,
                      relief="solid", bd=1, padx=14, pady=4, cursor="hand2",
                      command=win.destroy).pack(side="left", padx=6)
            win.grab_set()
            win.wait_window()
            return result[0]

        # topbar
        topbar = tk.Frame(page, bg=content_color)
        topbar.pack(fill="x", padx=28, pady=(20, 12))
        tk.Label(topbar, text="Students", bg=content_color, fg=FG_DARK,
                 font=("Segoe UI", 17, "bold")).pack(side="left")
        tk.Button(topbar, text="+ Add student", bg=WHITE, fg=FG_DARK,
                  font=UNIFORM_FONT, relief="solid", bd=1, padx=12, pady=5,
                  cursor="hand2", command=add_student_window).pack(side="right")

        card = tk.Frame(page, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="both", expand=True, padx=28, pady=(0, 20))

        filter_bar = tk.Frame(card, bg=WHITE)
        filter_bar.pack(fill="x", padx=16, pady=(14, 10))

        sw = tk.Frame(filter_bar, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        sw.pack(side="left", fill="x", expand=True, padx=(0, 8))
        tk.Label(sw, text="🔍", bg=WHITE, fg=FG_MUTED, font=UNIFORM_FONT).pack(side="left", padx=(8, 2), pady=6)
        search_entry = tk.Entry(sw, bg=WHITE, fg=FG_MUTED, font=UNIFORM_FONT,
                                relief="flat", bd=0, insertbackground=FG_DARK)
        search_entry.insert(0, "Search by ID or Name...")
        search_entry.pack(side="left", fill="x", expand=True, pady=7, padx=4)

        def on_fi(e):
            if search_entry.get() == "Search by ID or Name...":
                search_entry.delete(0, "end"); search_entry.config(fg=FG_DARK)
        def on_fo(e):
            if not search_entry.get().strip():
                search_entry.insert(0, "Search by ID or Name..."); search_entry.config(fg=FG_MUTED)
        search_entry.bind("<FocusIn>",  on_fi)
        search_entry.bind("<FocusOut>", on_fo)

        def do_search():
            q = search_entry.get().strip().lower()
            if q == "search by id or name...": q = ""
            for r in self.tree.get_children(): self.tree.delete(r)
            with sqlite3.connect(DB_NAME) as con:
                cur = con.cursor()
                cur.execute("""
                    SELECT student_no,
                        TRIM(first_name || ' ' || COALESCE(middle_initial || '. ', '') || last_name),
                        program, contact, building, room, status
                    FROM students WHERE LOWER(student_no) LIKE ? OR LOWER(first_name || ' ' || last_name) LIKE ?
                """, (f"%{q}%", f"%{q}%"))
                for r in cur.fetchall(): self.tree.insert("", "end", values=r)
            update_count()

        def clear_search():
            search_entry.delete(0, "end")
            search_entry.insert(0, "Search by ID or Name...")
            search_entry.config(fg=FG_MUTED)
            self.db.get_all_students(self.tree)
            update_count()

        tk.Label(sw, text="✕", bg=WHITE, fg=FG_MUTED, font=("Segoe UI", 9),
                 cursor="hand2").pack(side="right", padx=(2, 6))
        sw.winfo_children()[-1].bind("<Button-1>", lambda e: clear_search())
        search_entry.bind("<Return>", lambda e: do_search())
        tk.Button(filter_bar, text="Search", fg="BLACK", bg=content_color,
                  font=UNIFORM_FONT, relief="flat", padx=14, pady=6,
                  cursor="hand2", command=do_search).pack(side="left", padx=(0, 16))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Students.Treeview", background=WHITE, foreground=FG_DARK,
                        rowheight=36, fieldbackground=WHITE, borderwidth=0, font=UNIFORM_FONT)
        style.configure("Students.Treeview.Heading", background=HEADER_BG, foreground="#000000",
                        font=("Segoe UI", 9, "bold"), relief="flat", padding=(8, 6))
        style.map("Students.Treeview", background=[("selected", ROW_SEL)], foreground=[("selected", FG_DARK)])
        style.layout("Students.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

        tree_frame = tk.Frame(card, bg=WHITE)
        tree_frame.pack(fill="both", expand=True, padx=16)

        self.tree = ttk.Treeview(tree_frame,
                                 columns=("student_no", "name", "program", "contact", "building", "room", "status"),
                                 show="headings", style="Students.Treeview", selectmode="browse")
        for cid, heading, width, anchor in [
            ("student_no", "Student no.", 120, "w"), ("name", "Name", 190, "w"),
            ("program", "Program", 85, "center"), ("contact", "Contact", 120, "w"),
            ("building", "Building", 90, "center"), ("room", "Room", 70, "center"),
            ("status", "Status", 95, "center")
        ]:
            self.tree.heading(cid, text=heading, anchor=anchor)
            self.tree.column(cid, width=width, anchor=anchor, stretch=True)

        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=16, pady=(6, 0))
        action_bar = tk.Frame(card, bg=WHITE)
        action_bar.pack(fill="x", padx=16, pady=10)

        self.count_label = tk.Label(action_bar, text="0 students", bg=WHITE, fg=FG_MUTED, font=UNIFORM_FONT)
        self.count_label.pack(side="left", padx=(4, 0))

        def update_count():
            n = len(self.tree.get_children())
            self.count_label.config(text=f"{n} student{'s' if n != 1 else ''}")

        btn_cfg = dict(bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT,
                       relief="solid", bd=1, padx=14, pady=5, cursor="hand2")
        tk.Button(action_bar, text="✏  Edit",        command=edit_student,  **btn_cfg).pack(side="right", padx=4)
        tk.Button(action_bar, text="⊞  Assign room", command=assign_room,   **btn_cfg).pack(side="right", padx=4)
        tk.Button(action_bar, text="🗑  Delete",
                  bg=WHITE, fg="#c0392b", font=UNIFORM_FONT,
                  relief="solid", bd=1, padx=14, pady=5, cursor="hand2",
                  command=delete_student).pack(side="right", padx=4)

        tk.Label(card, text="ⓘ  Click a row to select before editing, assigning, or deleting.",
                 bg=WHITE, fg=FG_MUTED, font=("Segoe UI", 8), anchor="w").pack(fill="x", padx=20, pady=(0, 10))

        self.db.get_all_students(self.tree)
        update_count()

    # ── Rooms page ────────────────────────────────────────────────────
    def build_rooms_page(self, page):

        def rooms_confirm(msg):
            result = [False]
            win = tk.Toplevel()
            win.title("Confirm")
            win.config(bg=WHITE)
            win.geometry("320x130")
            win.resizable(False, False)
            tk.Label(win, text=msg, bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT, wraplength=280).pack(pady=16)
            btn_row = tk.Frame(win, bg=WHITE); btn_row.pack()
            def confirm():
                result[0] = True; win.destroy()
            tk.Button(btn_row, text="Delete", bg="#c0392b", fg=WHITE, font=UNIFORM_FONT,
                      relief="flat", padx=14, pady=4, cursor="hand2", command=confirm).pack(side="left", padx=6)
            tk.Button(btn_row, text="Cancel", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT,
                      relief="solid", bd=1, padx=14, pady=4, cursor="hand2",
                      command=win.destroy).pack(side="left", padx=6)
            win.grab_set(); win.wait_window(); return result[0]

        topbar = tk.Frame(page, bg=content_color)
        topbar.pack(fill="x", padx=28, pady=(20, 12))
        tk.Label(topbar, text="Rooms", bg=content_color, fg=FG_DARK,
                 font=("Segoe UI", 17, "bold")).pack(side="left")
        add_btn = tk.Button(topbar, text="+ Add room", bg=WHITE, fg=FG_DARK,
                            font=UNIFORM_FONT, relief="solid", bd=1, padx=12, pady=5, cursor="hand2")
        add_btn.pack(side="right")

        card = tk.Frame(page, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="both", expand=True, padx=28, pady=(0, 20))

        filter_bar = tk.Frame(card, bg=WHITE)
        filter_bar.pack(fill="x", padx=16, pady=(14, 10))

        sw = tk.Frame(filter_bar, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        sw.pack(side="left", fill="x", expand=True, padx=(0, 8))
        tk.Label(sw, text="🔍", bg=WHITE, fg=FG_MUTED, font=UNIFORM_FONT).pack(side="left", padx=(8, 2), pady=6)
        rsearch = tk.Entry(sw, bg=WHITE, fg=FG_MUTED, font=UNIFORM_FONT,
                           relief="flat", bd=0, insertbackground=FG_DARK)
        rsearch.insert(0, "Search by Room No. or Building...")
        rsearch.pack(side="left", fill="x", expand=True, pady=7, padx=4)

        def on_rfi(e):
            if rsearch.get() == "Search by Room No. or Building...":
                rsearch.delete(0, "end"); rsearch.config(fg=FG_DARK)
        def on_rfo(e):
            if not rsearch.get().strip():
                rsearch.insert(0, "Search by Room No. or Building..."); rsearch.config(fg=FG_MUTED)
        rsearch.bind("<FocusIn>",  on_rfi)
        rsearch.bind("<FocusOut>", on_rfo)

        def do_rsearch():
            q = rsearch.get().strip().lower()
            if q == "search by room no. or building...": q = ""
            for r in self.rooms_tree.get_children(): self.rooms_tree.delete(r)
            with sqlite3.connect(DB_NAME) as con:
                cur = con.cursor()
                cur.execute("""
                    SELECT room_id, room_number, building, room_type, capacity, occupants, status, last_cleaned
                    FROM rooms WHERE LOWER(room_number) LIKE ? OR LOWER(building) LIKE ?
                """, (f"%{q}%", f"%{q}%"))
                for r in cur.fetchall():
                    self.rooms_tree.insert("", "end", values=r[1:], tags=(r[0],))

        def clear_rsearch():
            rsearch.delete(0, "end")
            rsearch.insert(0, "Search by Room No. or Building...")
            rsearch.config(fg=FG_MUTED)
            self.db.get_all_rooms(self.rooms_tree)

        tk.Label(sw, text="✕", bg=WHITE, fg=FG_MUTED, font=("Segoe UI", 9),
                 cursor="hand2").pack(side="right", padx=(2, 6))
        sw.winfo_children()[-1].bind("<Button-1>", lambda e: clear_rsearch())
        rsearch.bind("<Return>", lambda e: do_rsearch())
        tk.Button(filter_bar, text="Search", fg="BLACK", bg=content_color,
                  font=UNIFORM_FONT, relief="flat", padx=14, pady=6,
                  cursor="hand2", command=do_rsearch).pack(side="left", padx=(0, 16))

        filter_frame = tk.Frame(card, bg=WHITE)
        filter_frame.pack(fill="x", padx=16, pady=(0, 8))
        tk.Label(filter_frame, text="Filter:", bg=WHITE, fg=FG_MUTED,
                 font=("Segoe UI", 9)).pack(side="left", padx=(0, 6))

        def filter_by_status(status_filter):
            for r in self.rooms_tree.get_children(): self.rooms_tree.delete(r)
            with sqlite3.connect(DB_NAME) as con:
                cur = con.cursor()
                if status_filter == "All":
                    cur.execute("SELECT room_id, room_number, building, room_type, capacity, occupants, status, last_cleaned FROM rooms")
                else:
                    cur.execute("SELECT room_id, room_number, building, room_type, capacity, occupants, status, last_cleaned FROM rooms WHERE status=?",
                                (status_filter,))
                for r in cur.fetchall():
                    self.rooms_tree.insert("", "end", values=r[1:], tags=(r[0],))

        for lbl, color, sv in [("All", FG_DARK, "All"), ("Vacant", "#27ae60", "Vacant"),
                                ("Occupied", "#8e44ad", "Occupied"), ("Maintenance", "#e67e22", "Under Maintenance")]:
            tk.Button(filter_frame, text=lbl, bg=WHITE, fg=color, font=("Segoe UI", 8),
                      relief="solid", bd=1, padx=10, pady=3, cursor="hand2",
                      command=lambda s=sv: filter_by_status(s)).pack(side="left", padx=3)

        style = ttk.Style()
        style.configure("Rooms.Treeview", background=WHITE, foreground=FG_DARK,
                        rowheight=36, fieldbackground=WHITE, borderwidth=0, font=UNIFORM_FONT)
        style.configure("Rooms.Treeview.Heading", background=HEADER_BG, foreground="#000000",
                        font=("Segoe UI", 9, "bold"), relief="flat", padding=(8, 6))
        style.map("Rooms.Treeview", background=[("selected", ROW_SEL)], foreground=[("selected", FG_DARK)])
        style.layout("Rooms.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

        tree_frame = tk.Frame(card, bg=WHITE)
        tree_frame.pack(fill="both", expand=True, padx=16)

        self.rooms_tree = ttk.Treeview(tree_frame,
                                       columns=("room_no", "Building", "type", "capacity", "occupants", "status"),
                                       show="headings", style="Rooms.Treeview", selectmode="browse")
        for cid, heading, width, anchor in [
            ("room_no", "Room No.", 90, "center"), ("Building", "Building", 70, "center"),
            ("type", "Type", 100, "center"), ("capacity", "Capacity", 80, "center"),
            ("occupants", "Occupants", 90, "center"), ("status", "Status", 120, "center")
        ]:
            self.rooms_tree.heading(cid, text=heading, anchor=anchor)
            self.rooms_tree.column(cid, width=width, anchor=anchor, stretch=True)

        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.rooms_tree.yview)
        self.rooms_tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.rooms_tree.pack(side="left", fill="both", expand=True)

        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=16, pady=(6, 0))
        action_bar = tk.Frame(card, bg=WHITE)
        action_bar.pack(fill="x", padx=16, pady=10)

        room_count_lbl = tk.Label(action_bar, text="0 rooms total", bg=WHITE, fg=FG_MUTED, font=UNIFORM_FONT)
        room_count_lbl.pack(side="left", padx=(4, 0))

        def update_room_count():
            n = len(self.rooms_tree.get_children())
            room_count_lbl.config(text=f"{n} room{'s' if n != 1 else ''} total")

        def add_room_window(prefill=None, edit_item=None):
            win = tk.Toplevel()
            win.title("Edit Room" if edit_item else "Add Room")
            win.config(bg=content_color)
            win.geometry("420x340")
            win.resizable(False, False)
            win.grab_set()

            upperFrame = tk.Frame(win, bg=content_color)
            upperFrame.pack(fill="x", padx=15, pady=12)
            tk.Label(upperFrame, text="Edit Room" if edit_item else "Add Room",
                     bg=content_color, fg=FG_DARK, font=("Segoe UI", 15, "bold")).pack(side="left")

            midFrame = tk.Frame(win, bg=WHITE, padx=15, pady=10,
                                bd=1, relief="solid", highlightbackground=BORDER)
            midFrame.pack(fill="both", expand=True, padx=15, pady=(5, 0))
            midFrame.columnconfigure(0, weight=1)
            midFrame.columnconfigure(1, weight=1)

            tk.Label(midFrame, text="Building",    bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).grid(row=0, column=0, sticky="w", padx=(0, 8), pady=(0, 2))
            tk.Label(midFrame, text="Room Number", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).grid(row=0, column=1, sticky="w", pady=(0, 2))
            tk.Label(midFrame, text="Room Type",   bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).grid(row=2, column=0, sticky="w", padx=(0, 8), pady=(0, 2))
            tk.Label(midFrame, text="Capacity",    bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).grid(row=2, column=1, sticky="w", pady=(0, 2))
            tk.Label(midFrame, text="Status",      bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).grid(row=4, column=0, columnspan=2, sticky="w", pady=(0, 2))

            buildingVar = tk.StringVar()
            buildingDrop = ttk.Combobox(midFrame, textvariable=buildingVar,
                                        values=["BLD-A", "BLD-B", "BLD-C"],
                                        state="readonly", font=UNIFORM_FONT)
            buildingDrop.grid(row=1, column=0, sticky="we", padx=(0, 8), pady=(0, 12))
            buildingDrop.current(0)

            nb = tk.Frame(midFrame, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
            nb.grid(row=1, column=1, sticky="we", pady=(0, 12))
            vcmd = (win.register(lambda P: (P.isdigit() or P == "") and len(P) <= 3), "%P")
            roomNumEntry = tk.Entry(nb, bg=WHITE, fg=BLACK, font=UNIFORM_FONT,
                                    relief="flat", bd=0, insertbackground=FG_DARK,
                                    validate="key", validatecommand=vcmd)
            roomNumEntry.pack(fill="x", padx=5, pady=3)

            typeVar = tk.StringVar()
            typeDrop = ttk.Combobox(midFrame, textvariable=typeVar,
                                    values=["Single", "Double", "Triple", "Suite"],
                                    state="readonly", font=UNIFORM_FONT)
            typeDrop.grid(row=3, column=0, sticky="we", padx=(0, 8), pady=(0, 12))
            typeDrop.current(0)

            capacityVar = tk.StringVar()
            capDrop = ttk.Combobox(midFrame, textvariable=capacityVar,
                                   values=["1", "2", "3", "4", "5", "6", "7", "8"],
                                   state="readonly", font=UNIFORM_FONT)
            capDrop.grid(row=3, column=1, sticky="we", pady=(0, 12))
            capDrop.current(0)

            statusVar = tk.StringVar()
            statusDrop = ttk.Combobox(midFrame, textvariable=statusVar,
                                      values=["Vacant", "Occupied", "Under Maintenance"],
                                      state="readonly", font=UNIFORM_FONT)
            statusDrop.grid(row=5, column=0, columnspan=2, sticky="we", pady=(0, 4))
            statusDrop.current(0)

            if prefill:
                buildingVar.set(prefill[1])
                roomNumEntry.insert(0, prefill[0])
                typeVar.set(prefill[2])
                capacityVar.set(str(prefill[3]))
                statusVar.set(prefill[5])

            err_label = tk.Label(win, text="", fg="#c0392b", bg=content_color, font=UNIFORM_FONT)
            err_label.pack()

            def save_room():
                room_no = roomNumEntry.get().strip()
                if not room_no:
                    err_label.config(text="Room number is required."); return
                if edit_item:
                    room_id = self.rooms_tree.item(edit_item, "tags")[0]
                    self.db.update_room(room_id, buildingVar.get(), room_no, typeVar.get(),
                                        int(capacityVar.get()), statusVar.get())
                else:
                    self.db.add_room(buildingVar.get(), room_no, typeVar.get(),
                                     int(capacityVar.get()), statusVar.get())
                self.db.get_all_rooms(self.rooms_tree)
                update_room_count()
                self.refresh_dashboard()
                win.destroy()

            bf = tk.Frame(win, bg=content_color)
            bf.pack(fill="x", padx=15, pady=15)
            tk.Button(bf, text="Save", font=UNIFORM_FONT, bg=BLACK, fg=WHITE,
                      relief="flat", padx=12, pady=5, cursor="hand2",
                      command=save_room).pack(side="right", padx=(5, 0))
            tk.Button(bf, text="Cancel", font=UNIFORM_FONT, fg="#c0392b",
                      relief="flat", padx=12, pady=5, cursor="hand2",
                      command=win.destroy).pack(side="right")

        def delete_room():
            selected = self.rooms_tree.selection()
            if not selected:
                messagebox.showwarning("Selection Required", "Please click a room from the table first."); return
            if rooms_confirm("Delete this room? This cannot be undone."):
                self.db.delete_room(self.rooms_tree.item(selected[0], "tags")[0])
                self.db.get_all_rooms(self.rooms_tree)
                update_room_count()
                self.refresh_dashboard()

        def edit_room():
            selected = self.rooms_tree.selection()
            if not selected:
                messagebox.showwarning("Selection Required", "Please click a room from the table first."); return
            add_room_window(prefill=self.rooms_tree.item(selected[0], "values"), edit_item=selected[0])

        def view_room_details():
            selected = self.rooms_tree.selection()
            if not selected:
                messagebox.showwarning("Selection Required", "Please click a room from the table first."); return
            values = self.rooms_tree.item(selected[0], "values")
            win = tk.Toplevel()
            win.title(f"Room {values[0]} — Details")
            win.config(bg=content_color)
            win.geometry("360x320")
            win.resizable(False, False)
            win.grab_set()
            upperFrame = tk.Frame(win, bg=content_color)
            upperFrame.pack(fill="x", padx=15, pady=12)
            tk.Label(upperFrame, text=f"Room {values[0]} Details", bg=content_color, fg=FG_DARK,
                     font=("Segoe UI", 15, "bold")).pack(side="left")
            midFrame = tk.Frame(win, bg=WHITE, padx=20, pady=20,
                                bd=1, relief="solid", highlightbackground=BORDER)
            midFrame.pack(fill="both", expand=True, padx=15, pady=5)
            midFrame.columnconfigure(0, weight=1)
            midFrame.columnconfigure(1, weight=2)
            for i, (lbl, val) in enumerate([
                ("Room Number", values[0]), ("Building", values[1]), ("Room Type", values[2]),
                ("Capacity", values[3]), ("Occupants", values[4]),
                ("Status", values[5]), ("Last Cleaned", values[6])
            ]):
                tk.Label(midFrame, text=lbl, bg=WHITE, fg=FG_MUTED, font=("Segoe UI", 9)).grid(row=i, column=0, sticky="w", pady=5)
                tk.Label(midFrame, text=val, bg=WHITE, fg=FG_DARK, font=("Segoe UI", 10, "bold")).grid(row=i, column=1, sticky="w", pady=5, padx=(10, 0))
            bf = tk.Frame(win, bg=content_color)
            bf.pack(fill="x", padx=15, pady=10)
            tk.Button(bf, text="Close", font=UNIFORM_FONT, bg=BLACK, fg=WHITE,
                      relief="flat", padx=12, pady=5, cursor="hand2",
                      command=win.destroy).pack(side="right")

        add_btn.config(command=add_room_window)
        btn_cfg = dict(bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT,
                       relief="solid", bd=1, padx=14, pady=5, cursor="hand2")
        tk.Button(action_bar, text="✏  Edit",         command=edit_room,         **btn_cfg).pack(side="right", padx=4)
        tk.Button(action_bar, text="⊞  View details", command=view_room_details, **btn_cfg).pack(side="right", padx=4)
        tk.Button(action_bar, text="🗑  Delete",
                  bg=WHITE, fg="#c0392b", font=UNIFORM_FONT,
                  relief="solid", bd=1, padx=14, pady=5, cursor="hand2",
                  command=delete_room).pack(side="right", padx=4)

        tk.Label(card, text="ⓘ  Click a row to select before editing, viewing details, or deleting.",
                 bg=WHITE, fg=FG_MUTED, font=("Segoe UI", 8), anchor="w").pack(fill="x", padx=20, pady=(0, 10))

        self.db.get_all_rooms(self.rooms_tree)
        update_room_count()

    # ══════════════════════════════════════════════════════════════════
    #  CLEANING PAGE  —  master-detail layout
    # ══════════════════════════════════════════════════════════════════
    def build_cleaning_page(self, page):
        """
        Top half  : master list of cleaning staff (ID, Name, Contact, Email, # assignments)
        Bottom half: schedule detail panel for the selected staff member
                     – one row per room assignment
                     – each row has its own ✕ remove button
                     – "Assign Cleaning" button in the detail header adds a new row
        """

        # ── shared state ──────────────────────────────────────────────
        selected_cs_id   = tk.StringVar()
        selected_cs_name = tk.StringVar()

        def validate_int(P):
            return P == "" or P.isdigit()

        def validate_str(P):
            return P == "" or P.isalpha() or " " in P

        # ── helpers ───────────────────────────────────────────────────
        def reload_master():
            self.db.get_all_cleaning_staff(self.cleaning_tree)

        def reload_detail():
            cs = selected_cs_id.get()
            if cs:
                self.db.get_schedules_for_staff(cs, self.schedule_tree)
            else:
                for r in self.schedule_tree.get_children():
                    self.schedule_tree.delete(r)
            update_detail_header()

        def update_detail_header():
            cs = selected_cs_id.get()
            if cs:
                name = selected_cs_name.get()
                detail_title_lbl.config(text=f"Schedule — {name}  ({cs})")
                detail_hint_lbl.config(text="Click a row then Remove to delete that assignment.")
            else:
                detail_title_lbl.config(text="Schedule — select a staff member above")
                detail_hint_lbl.config(text="Click a staff row above to load their schedule.")

        def on_staff_select(event):
            item = self.cleaning_tree.focus()
            if not item:
                return
            values = self.cleaning_tree.item(item, "values")
            selected_cs_id.set(values[0])
            selected_cs_name.set(values[1])
            reload_detail()

        # ── Add / Edit staff window ───────────────────────────────────
        def open_staff_window(prefill=None, edit_item=None):
            win = tk.Toplevel()
            win.title("Edit Cleaning Staff" if edit_item else "Add Cleaning Staff")
            win.config(bg=content_color)
            win.geometry("480x390")
            win.resizable(False, False)
            win.grab_set()

            vcmd_int = win.register(validate_int)
            vcmd_str = win.register(validate_str)

            upperFrame = tk.Frame(win, bg=content_color)
            upperFrame.pack(fill="x", padx=15, pady=12)
            tk.Label(upperFrame,
                     text="Edit Cleaning Staff" if edit_item else "Add Cleaning Staff",
                     bg=content_color, fg=FG_DARK,
                     font=("Segoe UI", 15, "bold")).pack(side="left")

            midFrame = tk.Frame(win, bg=WHITE, padx=15, pady=7,
                                bd=1, relief="solid", highlightbackground=BORDER)
            midFrame.pack(fill="x", padx=15, pady=5)
            midFrame.columnconfigure(0, weight=2)
            midFrame.columnconfigure(1, weight=2)
            midFrame.columnconfigure(2, weight=0)

            # Staff ID (full width, read-only when editing)
            tk.Label(midFrame, text="Cleaning Staff ID", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 2))
            idF = tk.Frame(midFrame, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
            idF.grid(row=1, column=0, columnspan=3, sticky="we", pady=(0, 15))
            idEntry = tk.Entry(idF, bg=WHITE, fg=BLACK, font=UNIFORM_FONT,
                               relief="flat", bd=0, insertbackground=FG_DARK,
                               state="readonly" if edit_item else "normal")
            idEntry.pack(fill="x", padx=5, pady=4)

            # Last / First / MI
            lnG = tk.Frame(midFrame, bg=WHITE); lnG.grid(row=2, column=0, sticky="we", padx=(0, 6), pady=(0, 15))
            tk.Label(lnG, text="Last Name", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).pack(anchor="w", pady=(0, 2))
            lnB = tk.Frame(lnG, bg=WHITE, highlightbackground=BORDER, highlightthickness=1); lnB.pack(fill="x")
            LN_Entry = tk.Entry(lnB, bg=WHITE, fg=BLACK, font=UNIFORM_FONT,
                                validate="key", validatecommand=(vcmd_str, "%P"),
                                relief="flat", bd=0, insertbackground=FG_DARK)
            LN_Entry.pack(fill="x", padx=5, pady=4)

            fnG = tk.Frame(midFrame, bg=WHITE); fnG.grid(row=2, column=1, sticky="we", padx=6, pady=(0, 15))
            tk.Label(fnG, text="First Name", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).pack(anchor="w", pady=(0, 2))
            fnB = tk.Frame(fnG, bg=WHITE, highlightbackground=BORDER, highlightthickness=1); fnB.pack(fill="x")
            FN_Entry = tk.Entry(fnB, bg=WHITE, fg=BLACK, font=UNIFORM_FONT,
                                validate="key", validatecommand=(vcmd_str, "%P"),
                                relief="flat", bd=0, insertbackground=FG_DARK)
            FN_Entry.pack(fill="x", padx=5, pady=4)

            miG = tk.Frame(midFrame, bg=WHITE); miG.grid(row=2, column=2, sticky="w", padx=(6, 0), pady=(0, 15))
            tk.Label(miG, text="M.I.", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).pack(anchor="w", pady=(0, 2))
            miB = tk.Frame(miG, bg=WHITE, highlightbackground=BORDER, highlightthickness=1); miB.pack()
            MI_Entry = tk.Entry(miB, bg=WHITE, fg=BLACK, font=UNIFORM_FONT,
                                validate="key", validatecommand=(vcmd_str, "%P"),
                                relief="flat", bd=0, insertbackground=FG_DARK, width=3)
            MI_Entry.pack(padx=5, pady=4)

            # Email / Contact
            emG = tk.Frame(midFrame, bg=WHITE); emG.grid(row=3, column=0, sticky="we", padx=(0, 6), pady=(0, 15))
            tk.Label(emG, text="Email", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).pack(anchor="w", pady=(0, 2))
            emB = tk.Frame(emG, bg=WHITE, highlightbackground=BORDER, highlightthickness=1); emB.pack(fill="x")
            emailEntry = tk.Entry(emB, bg=WHITE, fg=BLACK, font=UNIFORM_FONT,
                                  relief="flat", bd=0, insertbackground=FG_DARK)
            emailEntry.pack(fill="x", padx=5, pady=4)

            ctG = tk.Frame(midFrame, bg=WHITE); ctG.grid(row=3, column=1, columnspan=2, sticky="we", padx=(6, 0), pady=(0, 15))
            tk.Label(ctG, text="Contact Number", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).pack(anchor="w", pady=(0, 2))
            ctB = tk.Frame(ctG, bg=WHITE, highlightbackground=BORDER, highlightthickness=1); ctB.pack(fill="x")
            contactEntry = tk.Entry(ctB, bg=WHITE, fg=BLACK, font=UNIFORM_FONT,
                                    validate="key", validatecommand=(vcmd_int, "%P"),
                                    relief="flat", bd=0, insertbackground=FG_DARK)
            contactEntry.pack(fill="x", padx=5, pady=4)

            # Pre-fill for edit
            if prefill:
                idEntry.config(state="normal")
                idEntry.insert(0, prefill[0])
                idEntry.config(state="readonly")
                # Parse "Last, First MI" format
                raw = prefill[1]
                ln_seg, fn_seg, mi_seg = "", "", ""
                if "," in raw:
                    ln_seg, rest = raw.split(",", 1)
                    rest = rest.strip()
                    parts = rest.split()
                    mi_seg   = parts[-1] if len(parts) > 1 else ""
                    fn_seg   = " ".join(parts[:-1]) if len(parts) > 1 else rest
                LN_Entry.insert(0, ln_seg.strip())
                FN_Entry.insert(0, fn_seg.strip())
                MI_Entry.insert(0, mi_seg.strip())
                emailEntry.insert(0, prefill[3])
                contactEntry.insert(0, prefill[2])

            err_lbl = tk.Label(win, text="", fg="#c0392b", bg=content_color, font=UNIFORM_FONT)
            err_lbl.pack()

            def save():
                id_val      = idEntry.get().strip()
                last_val    = LN_Entry.get().strip()
                first_val   = FN_Entry.get().strip()
                mi_val      = MI_Entry.get().strip()
                email_val   = emailEntry.get().strip()
                contact_val = contactEntry.get().strip()

                if not id_val or not last_val or not first_val or not email_val or not contact_val:
                    err_lbl.config(text="All fields except M.I. are required."); return

                fullname_val = f"{last_val}, {first_val} {mi_val}".strip()

                try:
                    if edit_item:
                        self.db.update_cleaning_staff(id_val, last_val, first_val, mi_val,
                                                      email_val, contact_val, fullname_val)
                        # refresh name if this is the selected staff
                        if selected_cs_id.get() == id_val:
                            selected_cs_name.set(fullname_val)
                    else:
                        self.db.insert_cleaning_staff(id_val, last_val, first_val, mi_val,
                                                      email_val, contact_val, fullname_val)
                    reload_master()
                    update_detail_header()
                    self.refresh_dashboard()
                    win.destroy()
                except Exception as e:
                    err_lbl.config(text=f"Error: {e}")

            bf = tk.Frame(win, bg=content_color)
            bf.pack(fill="x", padx=15, pady=15)
            tk.Button(bf, text="Save", font=UNIFORM_FONT, bg=BLACK, fg=WHITE,
                      relief="flat", padx=12, pady=5, cursor="hand2",
                      command=save).pack(side="right", padx=(5, 0))
            tk.Button(bf, text="Cancel", fg="#c0392b", font=UNIFORM_FONT,
                      relief="flat", padx=12, pady=5, cursor="hand2",
                      command=win.destroy).pack(side="right")

        # ── Assign cleaning window ────────────────────────────────────
        def open_assign_window():
            cs = selected_cs_id.get()
            if not cs:
                messagebox.showwarning("Selection Required",
                                       "Please click a staff member above first.")
                return

            win = tk.Toplevel()
            win.title("Assign Cleaning")
            win.config(bg=content_color)
            win.geometry("420x380")
            win.resizable(False, False)
            win.grab_set()

            upperFrame = tk.Frame(win, bg=content_color)
            upperFrame.pack(fill="x", padx=15, pady=12)
            tk.Label(upperFrame, text=f"Assign Cleaning  —  {selected_cs_name.get()}",
                     bg=content_color, fg=FG_DARK,
                     font=("Segoe UI", 13, "bold")).pack(side="left")

            midFrame = tk.Frame(win, bg=WHITE, padx=15, pady=15,
                                bd=1, relief="solid", highlightbackground=BORDER)
            midFrame.pack(fill="both", expand=True, padx=15, pady=5)
            for col in range(6):
                midFrame.columnconfigure(col, weight=1, uniform="g")

            vcmd_int = midFrame.register(validate_int)

            # Building (cols 0-2) / Room (cols 3-5)
            tk.Label(midFrame, text="Building", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).grid(
                row=0, column=0, columnspan=3, sticky="w", pady=(0, 2))
            buildingVar = tk.StringVar()
            bldDrop = ttk.Combobox(midFrame, textvariable=buildingVar,
                                   values=self.db.get_distinct_buildings(),
                                   state="readonly", font=UNIFORM_FONT)
            bldDrop.grid(row=1, column=0, columnspan=3, sticky="we", pady=(0, 12), padx=(0, 6))
            if self.db.get_distinct_buildings():
                bldDrop.current(0)

            tk.Label(midFrame, text="Room", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).grid(
                row=0, column=3, columnspan=3, sticky="w", pady=(0, 2), padx=(6, 0))
            roomVar = tk.StringVar()
            roomDrop = ttk.Combobox(midFrame, textvariable=roomVar, values=[],
                                    state="readonly", font=UNIFORM_FONT)
            roomDrop.grid(row=1, column=3, columnspan=3, sticky="we", pady=(0, 12), padx=(6, 0))

            def on_bld_change(event):
                rooms = self.db.get_rooms_by_building(buildingVar.get())
                roomDrop.config(values=rooms)
                if rooms: roomDrop.current(0)
                else: roomVar.set("")

            bldDrop.bind("<<ComboboxSelected>>", on_bld_change)

            # Month (cols 0-1) / Day (cols 2-3) / Year (cols 4-5)
            for col_s, colspan, label, var_name in [
                (0, 2, "Month", "month"),
                (2, 2, "Day",   "day"),
                (4, 2, "Year",  "year"),
            ]:
                grp = tk.Frame(midFrame, bg=WHITE)
                grp.grid(row=2, column=col_s, columnspan=colspan, sticky="we",
                         padx=(0, 4) if col_s == 0 else (4, 4) if col_s == 2 else (4, 0),
                         pady=(0, 12))
                tk.Label(grp, text=label, bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).pack(anchor="w", pady=(0, 2))
                bdr = tk.Frame(grp, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
                bdr.pack(fill="x")
                ent = tk.Entry(bdr, bg=WHITE, fg=BLACK, font=UNIFORM_FONT,
                               validate="key", validatecommand=(vcmd_int, "%P"),
                               relief="flat", bd=0, insertbackground=FG_DARK)
                ent.pack(fill="x", padx=5, pady=4)
                # store as attribute so we can read them
                if var_name == "month": month_entry = ent
                elif var_name == "day": day_entry   = ent
                else:                  year_entry  = ent

            # Time start (cols 0-2) / Time end (cols 3-5)
            timeOptions = [
                "07:00 AM","07:30 AM","08:00 AM","08:30 AM","09:00 AM","09:30 AM",
                "10:00 AM","10:30 AM","11:00 AM","11:30 AM","12:00 PM","12:30 PM",
                "01:00 PM","01:30 PM","02:00 PM","02:30 PM","03:00 PM","03:30 PM",
                "04:00 PM","04:30 PM","05:00 PM","05:30 PM","06:00 PM","06:30 PM",
                "07:00 PM","07:30 PM","08:00 PM","08:30 PM","09:00 PM",
            ]

            tsF = tk.Frame(midFrame, bg=WHITE)
            tsF.grid(row=4, column=0, columnspan=3, sticky="we", padx=(0, 6))
            tk.Label(tsF, text="Time Start", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).pack(anchor="w", pady=(0, 2))
            tsVar = tk.StringVar()
            tsDrop = ttk.Combobox(tsF, textvariable=tsVar, values=timeOptions, state="readonly", font=UNIFORM_FONT)
            tsDrop.pack(fill="x", ipady=1); tsDrop.current(2)

            teF = tk.Frame(midFrame, bg=WHITE)
            teF.grid(row=4, column=3, columnspan=3, sticky="we", padx=(6, 0))
            tk.Label(teF, text="Time End", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).pack(anchor="w", pady=(0, 2))
            teVar = tk.StringVar()
            teDrop = ttk.Combobox(teF, textvariable=teVar, values=timeOptions, state="readonly", font=UNIFORM_FONT)
            teDrop.pack(fill="x", ipady=1); teDrop.current(4)

            err_lbl = tk.Label(win, text="", fg="#c0392b", bg=content_color, font=UNIFORM_FONT)
            err_lbl.pack(pady=(2, 0))

            def confirm_assign():
                building = buildingVar.get().strip()
                room     = roomVar.get().strip()
                month    = month_entry.get().strip()
                day      = day_entry.get().strip()
                year     = year_entry.get().strip()
                t_start  = tsVar.get().strip()
                t_end    = teVar.get().strip()

                if not building or not room:
                    err_lbl.config(text="Please select a building and room."); return
                if not month or not day or not year:
                    err_lbl.config(text="Please enter a complete date."); return
                if not t_start or not t_end:
                    err_lbl.config(text="Please select start and end times."); return

                try:
                    self.db.add_schedule(cs, building, room, month, day, year, t_start, t_end)
                    reload_detail()
                    reload_master()      # refresh assignment count
                    messagebox.showinfo("Success", "Cleaning assignment added.")
                    win.destroy()
                except Exception as e:
                    err_lbl.config(text=f"Error: {e}")

            bf = tk.Frame(win, bg=content_color)
            bf.pack(fill="x", padx=15, pady=15)
            tk.Button(bf, text="Confirm", font=UNIFORM_FONT, bg=BLACK, fg=WHITE,
                      relief="flat", padx=12, pady=5, cursor="hand2",
                      command=confirm_assign).pack(side="right", padx=(5, 0))
            tk.Button(bf, text="Cancel", fg="#c0392b", font=UNIFORM_FONT,
                      relief="flat", padx=12, pady=5, cursor="hand2",
                      command=win.destroy).pack(side="right")

        # ── Delete staff ──────────────────────────────────────────────
        def delete_staff():
            cs = selected_cs_id.get()
            if not cs:
                messagebox.showwarning("Selection Required",
                                       "Please click a staff member from the table first.")
                return
            if messagebox.askyesno("Confirm Delete",
                                   f"Delete staff {cs} and ALL their assignments?"):
                self.db.delete_cleaning_staff(cs)
                selected_cs_id.set("")
                selected_cs_name.set("")
                reload_master()
                reload_detail()
                self.refresh_dashboard()

        # ── Edit staff ────────────────────────────────────────────────
        def edit_staff():
            item = self.cleaning_tree.focus()
            if not item:
                messagebox.showwarning("Selection Required",
                                       "Please click a staff member from the table first.")
                return
            values = self.cleaning_tree.item(item, "values")
            open_staff_window(prefill=values, edit_item=item)

        # ── Remove one schedule row ───────────────────────────────────
        def remove_schedule():
            item = self.schedule_tree.selection()
            if not item:
                messagebox.showwarning("Selection Required",
                                       "Please click an assignment row to remove.")
                return
            sched_id = self.schedule_tree.item(item[0], "tags")[0]
            if messagebox.askyesno("Confirm", "Remove this assignment?"):
                self.db.delete_schedule(sched_id)
                reload_detail()
                reload_master()   # refresh count

        # ══════════════════════════════════════════════════════════════
        #  BUILD THE PAGE UI
        # ══════════════════════════════════════════════════════════════

        # ── Page top bar ──────────────────────────────────────────────
        topbar = tk.Frame(page, bg=content_color)
        topbar.pack(fill="x", padx=28, pady=(20, 8))
        tk.Label(topbar, text="Cleaning Staff", bg=content_color, fg=FG_DARK,
                 font=("Segoe UI", 17, "bold")).pack(side="left")
        tk.Button(topbar, text="+ Add Staff", command=lambda: open_staff_window(),
                  bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT, relief="solid", bd=1,
                  padx=12, pady=5, cursor="hand2").pack(side="right")

        # ══════════════════════════════════════════════════════════════
        #  MASTER PANEL  (top card)
        # ══════════════════════════════════════════════════════════════
        master_card = tk.Frame(page, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        master_card.pack(fill="x", padx=28, pady=(0, 6))

        # search bar
        sf_bar = tk.Frame(master_card, bg=WHITE)
        sf_bar.pack(fill="x", padx=16, pady=(10, 6))
        sw2 = tk.Frame(sf_bar, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        sw2.pack(side="left", fill="x", expand=True, padx=(0, 8))
        tk.Label(sw2, text="🔍", bg=WHITE, fg=FG_MUTED, font=UNIFORM_FONT).pack(side="left", padx=(8, 2), pady=5)
        cs_search = tk.Entry(sw2, bg=WHITE, fg=FG_MUTED, font=UNIFORM_FONT,
                             relief="flat", bd=0, insertbackground=FG_DARK)
        cs_search.insert(0, "Search by ID or Name...")
        cs_search.pack(side="left", fill="x", expand=True, pady=6, padx=4)

        def on_csfi(e):
            if cs_search.get() == "Search by ID or Name...":
                cs_search.delete(0, "end"); cs_search.config(fg=FG_DARK)
        def on_csfo(e):
            if not cs_search.get().strip():
                cs_search.insert(0, "Search by ID or Name..."); cs_search.config(fg=FG_MUTED)
        cs_search.bind("<FocusIn>",  on_csfi)
        cs_search.bind("<FocusOut>", on_csfo)

        def do_cs_search():
            q = cs_search.get().strip().lower()
            if q == "search by id or name...": q = ""
            for r in self.cleaning_tree.get_children(): self.cleaning_tree.delete(r)
            with sqlite3.connect(DB_NAME) as con:
                cur = con.cursor()
                cur.execute("""
                    SELECT cs.cs_ID, cs.full_name, cs.contact, cs.email,
                           COUNT(sch.id)
                    FROM cleaningStaff cs
                    LEFT JOIN cleaning_schedule sch ON cs.cs_ID = sch.cs_ID
                    WHERE LOWER(cs.cs_ID) LIKE ? OR LOWER(cs.full_name) LIKE ?
                    GROUP BY cs.cs_ID
                """, (f"%{q}%", f"%{q}%"))
                for r in cur.fetchall():
                    self.cleaning_tree.insert("", "end", values=r)

        def clear_cs_search():
            cs_search.delete(0, "end")
            cs_search.insert(0, "Search by ID or Name...")
            cs_search.config(fg=FG_MUTED)
            reload_master()

        tk.Label(sw2, text="✕", bg=WHITE, fg=FG_MUTED, font=("Segoe UI", 9),
                 cursor="hand2").pack(side="right", padx=(2, 6))
        sw2.winfo_children()[-1].bind("<Button-1>", lambda e: clear_cs_search())
        cs_search.bind("<Return>", lambda e: do_cs_search())
        tk.Button(sf_bar, text="Search", fg="BLACK", bg=content_color,
                  font=UNIFORM_FONT, relief="flat", padx=14, pady=5,
                  cursor="hand2", command=do_cs_search).pack(side="left", padx=(0, 8))

        # master treeview
        style = ttk.Style()
        style.theme_use("clam")
        for sname in ("CS.Master", "CS.Detail"):
            style.configure(f"{sname}.Treeview", background=WHITE, foreground=FG_DARK,
                            rowheight=34, fieldbackground=WHITE, borderwidth=0, font=UNIFORM_FONT)
            style.configure(f"{sname}.Treeview.Heading", background=HEADER_BG, foreground="#000000",
                            font=("Segoe UI", 9, "bold"), relief="flat", padding=(8, 6))
            style.map(f"{sname}.Treeview",
                      background=[("selected", ROW_SEL)],
                      foreground=[("selected", FG_DARK)])
            style.layout(f"{sname}.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

        master_tf = tk.Frame(master_card, bg=WHITE)
        master_tf.pack(fill="x", padx=16, pady=(0, 4))

        self.cleaning_tree = ttk.Treeview(
            master_tf,
            columns=("cs_id", "name", "contact", "email", "assignments"),
            show="headings",
            style="CS.Master.Treeview",
            selectmode="browse",
            height=5
        )
        for cid, heading, width, anchor in [
            ("cs_id",       "Staff ID",    90,  "w"),
            ("name",        "Name",       200,  "w"),
            ("contact",     "Contact",    120,  "w"),
            ("email",       "Email",      180,  "w"),
            ("assignments", "Assignments", 90,  "center"),
        ]:
            self.cleaning_tree.heading(cid, text=heading, anchor=anchor)
            self.cleaning_tree.column(cid, width=width, anchor=anchor, stretch=True)

        msb = ttk.Scrollbar(master_tf, orient="vertical", command=self.cleaning_tree.yview)
        self.cleaning_tree.configure(yscrollcommand=msb.set)
        msb.pack(side="right", fill="y")
        self.cleaning_tree.pack(side="left", fill="x", expand=True)
        self.cleaning_tree.bind("<ButtonRelease-1>", on_staff_select)

        # master action bar
        tk.Frame(master_card, bg=BORDER, height=1).pack(fill="x", padx=16)
        master_action = tk.Frame(master_card, bg=WHITE)
        master_action.pack(fill="x", padx=16, pady=8)

        btn_cfg = dict(bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT,
                       relief="solid", bd=1, padx=12, pady=4, cursor="hand2")
        tk.Button(master_action, text="✏  Edit staff",
                  command=edit_staff, **btn_cfg).pack(side="right", padx=4)
        tk.Button(master_action, text="🗑  Delete staff",
                  bg=WHITE, fg="#c0392b", font=UNIFORM_FONT,
                  relief="solid", bd=1, padx=12, pady=4, cursor="hand2",
                  command=delete_staff).pack(side="right", padx=4)
        tk.Label(master_action,
                 text="ⓘ  Click a staff row to load their cleaning schedule below.",
                 bg=WHITE, fg=FG_MUTED, font=("Segoe UI", 8)).pack(side="left")

        # ══════════════════════════════════════════════════════════════
        #  DETAIL PANEL  (bottom card — schedule for selected staff)
        # ══════════════════════════════════════════════════════════════
        detail_card = tk.Frame(page, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        detail_card.pack(fill="both", expand=True, padx=28, pady=(0, 20))

        # detail header row
        detail_hdr = tk.Frame(detail_card, bg=WHITE)
        detail_hdr.pack(fill="x", padx=16, pady=(10, 6))

        detail_title_lbl = tk.Label(detail_hdr, text="Schedule — select a staff member above",
                                    bg=WHITE, fg=FG_DARK, font=("Segoe UI", 11, "bold"))
        detail_title_lbl.pack(side="left")

        tk.Button(detail_hdr, text="+ Assign cleaning",
                  command=open_assign_window,
                  bg=sidebar_color, fg=WHITE, font=UNIFORM_FONT,
                  relief="flat", padx=12, pady=4, cursor="hand2").pack(side="right")

        tk.Frame(detail_card, bg=BORDER, height=1).pack(fill="x", padx=16)

        # detail treeview
        detail_tf = tk.Frame(detail_card, bg=WHITE)
        detail_tf.pack(fill="both", expand=True, padx=16, pady=(4, 0))

        self.schedule_tree = ttk.Treeview(
            detail_tf,
            columns=("#", "building", "room", "date", "time_start", "time_end"),
            show="headings",
            style="CS.Detail.Treeview",
            selectmode="browse",
            height=6   
        )
        for cid, heading, width, anchor in [
            ("#",          "#",          40,  "center"),
            ("building",   "Building",   90,  "center"),
            ("room",       "Room",       80,  "center"),
            ("date",       "Date",      110,  "center"),
            ("time_start", "Time Start", 110, "center"),
            ("time_end",   "Time End",   110, "center"),
        ]:
            self.schedule_tree.heading(cid, text=heading, anchor=anchor)
            self.schedule_tree.column(cid, width=width, anchor=anchor, stretch=True)

        dsb = ttk.Scrollbar(detail_tf, orient="vertical", command=self.schedule_tree.yview)
        self.schedule_tree.configure(yscrollcommand=dsb.set)
        dsb.pack(side="right", fill="y")
        self.schedule_tree.pack(side="left", fill="both", expand=True)

        # detail action bar
        tk.Frame(detail_card, bg=BORDER, height=1).pack(fill="x", padx=16, pady=(4, 0))
        detail_action = tk.Frame(detail_card, bg=WHITE)
        detail_action.pack(fill="x", padx=16, pady=8)

        detail_hint_lbl = tk.Label(detail_action,
                                   text="Click a staff row above to load their schedule.",
                                   bg=WHITE, fg=FG_MUTED, font=("Segoe UI", 8))
        detail_hint_lbl.pack(side="left")

        tk.Button(detail_action, text="✕  Remove assignment",
                  bg=WHITE, fg="#c0392b", font=UNIFORM_FONT,
                  relief="solid", bd=1, padx=12, pady=4, cursor="hand2",
                  command=remove_schedule).pack(side="right", padx=4)

        # ── initial load ──────────────────────────────────────────────
        reload_master()

    # ── Settings page ─────────────────────────────────────────────────
    


if __name__ == "__main__":
    app = main()
    app.mainloop()  
