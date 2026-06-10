import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
import customtkinter as ctk
import sqlite3
import re
import shutil
import os
from datetime import datetime

UNIFORM_FONT = ("Segoe UI", 10)
BOLD_BTN_FONT = ("Segoe UI", 10, "bold")

WHITE      = "#ffffff"
BLACK      = "#000000"
HEADER_BG  = "#8fd2e5"   
ROW_ALT    = "#f7f9fa"  
ROW_SEL    = "#49bbd8"   
BORDER     = "#1d9bb7"  
FG_DARK    = "#116e82"   
FG_MUTED   = "#64c3dc" 

GREEN_BTN  = "#27ae60"
GREEN_HOVER= "#219653"
RED_BTN    = "#c0392b"
RED_HOVER  = "#a83226"

font_color_sidebar = "#ffffff"   
sidebar_color      = "#17849c"
active_color       = "#23b3d3"   
content_color      = "#f7f9fa"   
black              = "#070707"   

DB_NAME = "dorm_management.db"

def auto_backup():
    """
    Copies dorm_management.db to a backups/ folder with a timestamp.
    Keeps only the 10 most recent backups — deletes the oldest ones.
    Called once on app startup.
    """
    if not os.path.exists(DB_NAME):
        return  # nothing to back up yet

    backup_dir = "backups"
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_path = os.path.join(backup_dir, f"dorm_backup_{timestamp}.db")

    shutil.copy2(DB_NAME, backup_path)

    all_backups = sorted(
        [f for f in os.listdir(backup_dir) if f.startswith("dorm_backup_")],
        reverse=True
    )
    for old_file in all_backups[10:]:
        os.remove(os.path.join(backup_dir, old_file))


# ══════════════════════════════════════════════════════════════════════
#  DATABASE LAYER
# ══════════════════════════════════════════════════════════════════════
class Database:
    def for_dashboard(self):
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute("SELECT COUNT(*) FROM Students")
            total_students = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM Rooms")
            total_rooms = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM CleaningStaff")
            total_cleaning_staff = cur.fetchone()[0]
            return total_students, total_rooms, total_cleaning_staff

    def create_student_table(self):
        with sqlite3.connect(DB_NAME) as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS Students (
                    StudentNo      VARCHAR(255) PRIMARY KEY,
                    LastName       VARCHAR(255) NOT NULL,
                    FirstName      VARCHAR(255) NOT NULL,
                    MiddleInitial  VARCHAR(255),
                    Program         VARCHAR(255) NOT NULL,
                    Status          VARCHAR(255) NOT NULL,
                    Contact         VARCHAR(255) NOT NULL,
                    Room            VARCHAR(255) DEFAULT '',
                    Building        VARCHAR(255) DEFAULT ''
                )
            """)
            con.commit()

    def add_student(self, StudentNo, last, first, mi, Program, Status, Contact):
        with sqlite3.connect(DB_NAME) as con:
            con.execute(
                "INSERT INTO Students VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (StudentNo, last, first, mi, Program, Status, Contact, "", "")
            )
            con.commit()

    def get_all_students(self, tree):
        for row in tree.get_children():
            tree.delete(row)
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute("""
                SELECT StudentNo,
                    TRIM(FirstName || ' ' || COALESCE(MiddleInitial || '. ', '') || LastName),
                    Program, Contact, Building, Room, Status
                FROM Students
            """)
            for row in cur.fetchall():
                tree.insert("", "end", values=row)

    def update_student(self, original_no, StudentNo, last, first, mi, Program, Status, Contact):
        with sqlite3.connect(DB_NAME) as con:
            con.execute("""
                UPDATE Students
                SET StudentNo=?, LastName=?, FirstName=?, MiddleInitial=?,
                    Program=?, Status=?, Contact=?
                WHERE StudentNo=?
            """, (StudentNo, last, first, mi, Program, Status, Contact, original_no))
            con.commit()

    def delete_student(self, StudentNo):
        with sqlite3.connect(DB_NAME) as con:
            con.execute("DELETE FROM Students WHERE StudentNo=?", (StudentNo,))
            con.commit()

    def migrate_students_table(self):
        with sqlite3.connect(DB_NAME) as con:
            try:
                con.execute("ALTER TABLE Students ADD COLUMN Room VARCHAR(255) DEFAULT ''")
                con.execute("ALTER TABLE Students ADD COLUMN Building VARCHAR(255) DEFAULT ''")
                con.commit()
            except Exception:
                pass

    def assign_room_to_student(self, StudentNo, Room, Building):
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute("UPDATE Students SET Room=?, Building=? WHERE StudentNo=?",
                        (Room, Building, StudentNo))
            cur.execute("UPDATE Rooms SET Occupants = Occupants + 1 WHERE RoomNumber=? AND Building=?",
                        (Room, Building))
            cur.execute("""UPDATE Rooms SET Status='Occupied'
                           WHERE RoomNumber=? AND Building=? AND Occupants >= Capacity""",
                        (Room, Building))
            con.commit()

    def remove_student_from_room(self, StudentNo):
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute("SELECT Room, Building FROM Students WHERE StudentNo=?", (StudentNo,))
            row = cur.fetchone()
            if row and row[0] and row[1]:
                Room, Building = row
                cur.execute("UPDATE Rooms SET Occupants = MAX(0, Occupants - 1) WHERE RoomNumber=? AND Building=?",
                            (Room, Building))
                cur.execute("""UPDATE Rooms SET Status='Vacant'
                               WHERE RoomNumber=? AND Building=? AND Occupants < Capacity AND Status='Occupied'""",
                            (Room, Building))
                cur.execute("UPDATE Students SET Room='', Building='' WHERE StudentNo=?", (StudentNo,))
            con.commit()

    def seed_sample_students(self):
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute("SELECT COUNT(*) FROM Students")
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
                "INSERT OR IGNORE INTO Students VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [(s[0], s[1], s[2], s[3], s[4], s[5], s[6], "", "") for s in sample]
            )
            con.commit()

    def create_rooms_table(self):
        with sqlite3.connect(DB_NAME) as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS Rooms (
                    RoomID      INTEGER PRIMARY KEY AUTOINCREMENT,
                    Building     VARCHAR(255) NOT NULL,
                    RoomNumber  VARCHAR(255) NOT NULL,
                    Price        REAL DEFAULT 10000,
                    Capacity     INTEGER NOT NULL,
                    Occupants    INTEGER DEFAULT 0,
                    Status       VARCHAR(255) NOT NULL,
                    LastCleaned VARCHAR(255) DEFAULT '—'
                )
            """)
            con.commit()

    def add_room(self, Building, RoomNumber, Capacity, Status):
        with sqlite3.connect(DB_NAME) as con:
            con.execute(
                "INSERT INTO Rooms (Building, RoomNumber, Capacity, Status, Price) VALUES (?, ?, ?, ?, ?)",
                (Building, RoomNumber, Capacity, Status, 10000)
            )
            con.commit()

    def get_all_rooms(self, tree):
        for row in tree.get_children():
            tree.delete(row)
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute("SELECT RoomID, RoomNumber, Building, Capacity, Occupants, Status, Price FROM Rooms")
            for row in cur.fetchall():
                tree.insert("", "end", values=row[1:], tags=(row[0],))

    def update_room(self, RoomID, Building, RoomNumber, Capacity, Status):
        with sqlite3.connect(DB_NAME) as con:
            con.execute("""
                UPDATE Rooms SET Building=?, RoomNumber=?, Capacity=?, Status=?
                WHERE RoomID=?
            """, (Building, RoomNumber, Capacity, Status, RoomID))
            con.commit()

    def delete_room(self, RoomID):
        with sqlite3.connect(DB_NAME) as con:
            con.execute("DELETE FROM Rooms WHERE RoomID=?", (RoomID,))
            con.commit()

    def get_distinct_buildings(self):
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute("SELECT DISTINCT Building FROM Rooms ORDER BY Building")
            return [row[0] for row in cur.fetchall()]

    def get_rooms_by_building(self, Building):
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute("""
                SELECT RoomNumber FROM Rooms
                WHERE Building=? AND Occupants <= Capacity AND Status != 'Under Maintenance'
                ORDER BY RoomNumber
            """, (Building,))
            return [row[0] for row in cur.fetchall()]

    def create_table_cleaning_staff(self):
        with sqlite3.connect(DB_NAME) as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS CleaningStaff (
                    StaffID          VARCHAR(255) PRIMARY KEY,
                    LastName      VARCHAR(255) NOT NULL,
                    FirstName     VARCHAR(255) NOT NULL,
                    MiddleInitial VARCHAR(255),
                    Email          VARCHAR(255) UNIQUE NOT NULL,
                    Contact        VARCHAR(255) NOT NULL,
                    FullName      VARCHAR(255) NOT NULL
                )
            """)
            con.commit()

    def insert_cleaning_staff(self, StaffID, last, first, mi, Email, Contact, FullName):
        with sqlite3.connect(DB_NAME) as con:
            con.execute(
                "INSERT INTO CleaningStaff VALUES (?, ?, ?, ?, ?, ?, ?)",
                (StaffID, last, first, mi, Email, Contact, FullName)
            )
            con.commit()

    def update_cleaning_staff(self, StaffID, last, first, mi, Email, Contact, FullName):
        with sqlite3.connect(DB_NAME) as con:
            con.execute("""
                UPDATE CleaningStaff
                SET LastName=?, FirstName=?, MiddleInitial=?, Email=?, Contact=?, FullName=?
                WHERE StaffID=?
            """, (last, first, mi, Email, Contact, FullName, StaffID))
            con.commit()

    def delete_cleaning_staff(self, StaffID):
        with sqlite3.connect(DB_NAME) as con:
            con.execute("DELETE FROM CleaningStaff WHERE StaffID=?", (StaffID,))
            con.execute("DELETE FROM cleaning_schedule WHERE StaffID=?", (StaffID,))
            con.commit()

    def get_all_cleaning_staff(self, tree):
        for row in tree.get_children():
            tree.delete(row)
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute("""
                        SELECT cs.StaffID, cs.FullName, cs.Contact, cs.Email,
                            COUNT(sch.Id) AS assignments
                        FROM CleaningStaff cs
                        LEFT JOIN cleaning_schedule sch 
                            ON cs.StaffID = sch.StaffID
                            AND date(
                                printf('%04d-%02d-%02d', 
                                    CAST(sch.Year AS INT), 
                                    CAST(sch.Month AS INT), 
                                    CAST(sch.Day AS INT))
                            ) >= date('now')
                        GROUP BY cs.StaffID
                        ORDER BY cs.FullName
                    """)
            for row in cur.fetchall():
                tree.insert("", "end", values=row)

    def create_cleaning_schedule_table(self):
        with sqlite3.connect(DB_NAME) as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS cleaning_schedule (
                    Id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    StaffID      VARCHAR(255) NOT NULL,
                    Building   VARCHAR(255) NOT NULL,
                    Room       VARCHAR(255) NOT NULL,
                    Month      VARCHAR(255) NOT NULL,
                    Day        VARCHAR(255) NOT NULL,
                    Year       VARCHAR(255) NOT NULL,
                    TimeStart VARCHAR(255) NOT NULL,
                    TimeEnd   VARCHAR(255) NOT NULL
                )
            """)
            con.commit()

    def get_schedules_for_staff(self, StaffID, tree):
        for row in tree.get_children():
            tree.delete(row)
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute("""
                SELECT Id, Building, Room,
                       Month || '/' || Day || '/' || Year,
                       TimeStart, TimeEnd
                FROM cleaning_schedule
                WHERE StaffID=?
                ORDER BY Year, Month, Day, TimeStart
            """, (StaffID,))
            for i, row in enumerate(cur.fetchall(), start=1):
                sched_id = row[0]
                values   = (i,) + row[1:]    
                tree.insert("", "end", values=values, tags=(sched_id,))

    def add_schedule(self, StaffID, Building, Room, Month, Day, Year, TimeStart, TimeEnd):
        with sqlite3.connect(DB_NAME) as con:
            con.execute("""
                INSERT INTO cleaning_schedule (StaffID, Building, Room, Month, Day, Year, TimeStart, TimeEnd)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (StaffID, Building, Room, Month, Day, Year, TimeStart, TimeEnd))
            con.commit()

    def delete_schedule(self, sched_id):
        with sqlite3.connect(DB_NAME) as con:
            con.execute("DELETE FROM cleaning_schedule WHERE Id=?", (sched_id,))
            con.commit()

    def get_assigned_students(self):
        with sqlite3.connect(DB_NAME) as connect:
            cursor = connect.cursor()
            cursor.execute("""
                SELECT FirstName || ' ' || LastName, Building, Room, Status
                FROM Students
                WHERE Room != '' AND Room IS NOT NULL
                ORDER BY Building, Room
            """)
            return cursor.fetchall()

    def get_todays_cleaning_assignments(self):
        today = datetime.now()
        with sqlite3.connect(DB_NAME) as connect:
            cursor = connect.cursor()
            cursor.execute("""
                SELECT cs.StaffID, cs.FullName,
                    sch.Building || ' ' || sch.Room,
                    sch.TimeStart, sch.TimeEnd
                FROM cleaning_schedule sch
                JOIN CleaningStaff cs ON cs.StaffID = sch.StaffID
                WHERE CAST(sch.Month AS INT) = ?
                AND CAST(sch.Day   AS INT) = ?
                AND CAST(sch.Year  AS INT) = ?
                ORDER BY sch.TimeStart
            """, (today.month, today.day, today.year))
            return cursor.fetchall()
    
    def get_total_revenue_this_month(self):
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute("SELECT COALESCE(SUM(Price), 0) FROM Rooms WHERE Occupants > 0")
            return cur.fetchone()[0]

    def get_total_available_slots(self):
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute("SELECT COALESCE(SUM(Capacity - Occupants), 0) FROM Rooms")
            return cur.fetchone()[0]


# ══════════════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ══════════════════════════════════════════════════════════════════════
class main(ctk.CTk):  
    def __init__(self):
        super().__init__()
        self.geometry("1200x650")
        self.minsize(1150, 650)
        self.title("Dormi Admin Panel")

        self.db = Database()
        auto_backup()
        self.db.create_student_table()
        self.db.create_rooms_table()
        self.db.create_table_cleaning_staff()
        self.db.create_cleaning_schedule_table()
        self.db.migrate_students_table()
        self.db.seed_sample_students()

        self.all_pages   = []
        self.all_buttons = []
        self._selected_cs_id = None

        self.main_build_layout()
        self.refresh_dashboard()

    def main_build_layout(self):
        self.sidebar = ctk.CTkFrame(self, fg_color=sidebar_color, width=300, corner_radius=15)
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10) 
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="Dormi",       bg=sidebar_color, fg=font_color_sidebar,
                 font=("Arial", 14, "bold")).pack(anchor="w", padx=15, pady=(20, 0))
        tk.Label(self.sidebar, text="Admin panel", bg=sidebar_color, fg=font_color_sidebar,
                 font=("Arial", 9)).pack(anchor="w", padx=15, pady=(0, 20))

        content = ctk.CTkFrame(self, fg_color=content_color, corner_radius=15)
        content.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)

        self.dashboard_page = ctk.CTkFrame(content, fg_color=content_color, corner_radius=15)
        self.students_page  = ctk.CTkFrame(content, fg_color=content_color, corner_radius=15)
        self.rooms_page     = ctk.CTkFrame(content, fg_color=content_color, corner_radius=15)
        self.cleaning_page  = ctk.CTkFrame(content, fg_color=content_color, corner_radius=15)
        
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

        self.dashboardButton = ctk.CTkButton(self.sidebar, text="Dashboard",
                                             fg_color=active_color, text_color=font_color_sidebar,
                                             font=("Arial", 12, "bold"), corner_radius=10,
                                             anchor="w", height=40, hover_color="#23b3d3")
        self.dashboardButton.pack(fill="x", padx=15, pady=4)

        tk.Label(self.sidebar, text="MANAGE", bg=sidebar_color, fg=font_color_sidebar,
                 font=("Arial", 8)).pack(anchor="w", padx=15, pady=(10, 2))

        self.studentButton = ctk.CTkButton(self.sidebar, text="Students",
                                           fg_color="transparent", text_color=font_color_sidebar,
                                           font=("Arial", 12), corner_radius=10,
                                           anchor="w", height=40, hover_color="#BE9C7C")
        self.studentButton.pack(fill="x", padx=15, pady=4)

        self.roomsButton = ctk.CTkButton(self.sidebar, text="Rooms",
                                         fg_color="transparent", text_color=font_color_sidebar,
                                         font=("Arial", 12), corner_radius=10,
                                         anchor="w", height=40, hover_color="#BE9C7C")
        self.roomsButton.pack(fill="x", padx=15, pady=4)

        self.cleaningButton = ctk.CTkButton(self.sidebar, text="Cleaning staff",
                                            fg_color="transparent", text_color=font_color_sidebar,
                                            font=("Arial", 12), corner_radius=10,
                                            anchor="w", height=40, hover_color="#BE9C7C")
        self.cleaningButton.pack(fill="x", padx=15, pady=4)

        self.all_buttons = [
            self.dashboardButton, self.studentButton, self.roomsButton,
            self.cleaningButton
        ]

        self.dashboardButton.configure(command=lambda: self.show_page(self.dashboard_page, self.dashboardButton))
        self.studentButton.configure(  command=lambda: self.show_page(self.students_page,  self.studentButton))
        self.roomsButton.configure(    command=lambda: self.show_page(self.rooms_page,     self.roomsButton))
        self.cleaningButton.configure( command=lambda: self.show_page(self.cleaning_page,  self.cleaningButton))
        
        self.show_page(self.dashboard_page, self.dashboardButton)
        
        ctk.CTkButton(self.sidebar, text="⏻  Log Out",
                      fg_color="#c0392b", text_color="white", font=("Arial", 12, "bold"),
                      corner_radius=10, height=40, hover_color="#e74c3c",
                      command=self.destroy).pack(side="bottom", fill="x", padx=15, pady=15)

    def refresh_dashboard(self):
        ts, tr, tc = self.db.for_dashboard()
        self.tsNum.config(text=str(ts))
        self.trNum.config(text=str(tr))
        self.tcNum.config(text=str(tc))
        self.trevNum.config(text=f"₱{self.db.get_total_revenue_this_month():,.0f}")
        self.tavNum.config(text=str(self.db.get_total_available_slots()))

        for row in self.treeStuAss.get_children():
            self.treeStuAss.delete(row)
        for row in self.db.get_assigned_students():
            self.treeStuAss.insert("", "end", values=row)

        for row in self.treeCleanAss.get_children():
            self.treeCleanAss.delete(row)
        for row in self.db.get_todays_cleaning_assignments():
            self.treeCleanAss.insert("", "end", values=row)

    def show_page(self, page, active_btn):
        for p in self.all_pages:
            p.pack_forget()
        for btn in self.all_buttons:
            btn.configure(fg_color="transparent")
        page.pack(fill="both", expand=True)
        active_btn.configure(fg_color=active_color)

    def build_dashboard_page(self, page):
        tk.Label(page, text="Dashboard", bg=content_color, fg="black",
                 font=("Arial", 16, "bold")).pack(anchor="w", pady=20, padx=20)

        cards_frame = ctk.CTkFrame(page, fg_color=content_color, corner_radius=15)
        cards_frame.pack(fill="x", padx=30, pady=10)

        def make_card(parent, accent, emoji, num_attr, label_text):
            frame = ctk.CTkFrame(parent, width=200, height=150, fg_color="white", corner_radius=15)
            frame.pack(side="left", padx=(0, 10), fill="x", expand=True)
            frame.pack_propagate(False)
            ctk.CTkFrame(frame, fg_color=accent, width=5, corner_radius=15).pack(side="left", fill="y")
            inner = ctk.CTkFrame(frame, fg_color="white", corner_radius=15)
            inner.pack(side="left", fill="both", expand=True)
            tk.Label(inner, text=emoji, font=("Arial", 24), bg="white", fg=accent).pack(anchor="w", padx=10, pady=(10, 0))
            num_lbl = tk.Label(inner, text="0", font=("Arial", 24, "bold"), bg="white", fg=accent)
            num_lbl.pack(anchor="w", padx=10)
            tk.Label(inner, text=label_text, font=("Arial", 13), bg="white", fg=accent).pack(anchor="w", padx=10, pady=(2, 0))
            return num_lbl

        self.tsNum  = make_card(cards_frame, "#8A5F41", "🧑",  "tsNum",  "Total Students")
        self.trNum  = make_card(cards_frame, "#4A8C7A", "🛏️", "trNum",  "Total Rooms")
        self.tcNum  = make_card(cards_frame, "#A05C6A", "🧹",  "tcNum",  "Cleaning staff")
        self.trevNum = make_card(cards_frame, "#A5AB2E", "💰", "trevNum", "Revenue this month")
        self.tavNum  = make_card(cards_frame, "#27ae60", "🏠", "tavNum",  "Can accommodate")

        tk.Label(page, text="Recent student assignments", bg=content_color,
                 font=("Arial", 12, "bold"), fg="black").pack(anchor="w", pady=5, padx=30)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dashboard.Treeview",
                        background=WHITE,
                        foreground=FG_DARK,
                        rowheight=36,
                        fieldbackground=WHITE,
                        borderwidth=0,
                        font=UNIFORM_FONT)
        style.configure("Dashboard.Treeview.Heading",
                        background=HEADER_BG,
                        foreground="#000000",
                        font=("Segoe UI", 9, "bold"),
                        relief="flat",
                        padding=(8, 6))
        style.map("Dashboard.Treeview",
                background=[("selected", ROW_SEL)],
                foreground=[("selected", FG_DARK)])
        style.layout("Dashboard.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

        stu_frame = ctk.CTkFrame(page, fg_color=WHITE, corner_radius=15, border_width=1, border_color=BORDER)
        stu_frame.pack(fill="both", padx=20, pady=10)
        self.treeStuAss = ttk.Treeview(stu_frame, columns=("Student", "Building", "Room", "Status"),
                                        show="headings", style="Dashboard.Treeview", height=5)
        for col, w, anchor in [("Student", 150, "w"), ("Building", 80, "center"),
                                ("Room", 80, "center"), ("Status", 90, "center")]:
            self.treeStuAss.heading(col, text=col, anchor=anchor)
            self.treeStuAss.column(col, width=w, anchor=anchor, stretch=True)
        self.treeStuAss.pack(fill="both", expand=True, padx=5, pady=5)

        tk.Label(page, text="Cleaning assignments today", bg=content_color,
                 font=("Arial", 12, "bold"), fg="black").pack(anchor="w", pady=5, padx=30)

        clean_frame = ctk.CTkFrame(page, fg_color=WHITE, corner_radius=15, border_width=1, border_color=BORDER)
        clean_frame.pack(fill="both", padx=20, pady=10)
        self.treeCleanAss = ttk.Treeview(clean_frame, columns=("ID", "StaffName", "Room", "TimeStart", "TimeEnd"),
                                        show="headings", style="Dashboard.Treeview", height=5)
        for col, w, anchor in [("ID", 80, "w"), ("StaffName", 180, "w"), ("Room", 100, "center"),
                                ("TimeStart", 100, "center"), ("TimeEnd", 100, "center")]:
            self.treeCleanAss.heading(col, text=col, anchor=anchor)
            self.treeCleanAss.column(col, width=w, anchor=anchor, stretch=True)
        self.treeCleanAss.pack(fill="both", expand=True, padx=5, pady=5)

    def build_students_page(self, page):
        def reload_master():
            self.db.get_all_students(self.tree)

        def add_student_window(prefill=None, edit_item=None):
            win = tk.Toplevel()
            win.title("Edit Student" if edit_item else "Add Student")
            win.config(bg=content_color)
            win.geometry("520x440")
            win.resizable(False, False)
            win.grab_set()

            upperFrame = ctk.CTkFrame(win, fg_color=content_color, corner_radius=15)
            upperFrame.pack(fill="x", padx=15, pady=12)
            tk.Label(upperFrame,
                     text="Edit Student" if edit_item else "Add Student",
                     bg=content_color, fg=FG_DARK,
                     font=("Segoe UI", 15, "bold")).pack(side="left")

            midFrame = ctk.CTkFrame(win, fg_color=WHITE, corner_radius=15, border_width=1, border_color=BORDER)
            midFrame.pack(fill="both", expand=True, padx=15, pady=5)
            midFrame.columnconfigure(0, weight=2)
            midFrame.columnconfigure(1, weight=2)
            midFrame.columnconfigure(2, weight=0)

            tk.Label(midFrame, text="Student No.", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 2))
            e_no = ctk.CTkEntry(midFrame, fg_color=WHITE, text_color=BLACK, font=UNIFORM_FONT, corner_radius=8, height=32)
            e_no.grid(row=1, column=0, columnspan=3, sticky="we", padx=10, pady=(0, 10))

            for col, txt in [(0, "Last Name"), (1, "First Name"), (2, "M.I.")]:
                tk.Label(midFrame, text=txt, bg=WHITE, fg=FG_DARK,
                         font=UNIFORM_FONT).grid(row=2, column=col, sticky="w",
                                                 padx=(10 if col == 0 else 6, 6), pady=(0, 2))
            e_last  = ctk.CTkEntry(midFrame, fg_color=WHITE, text_color=BLACK, font=UNIFORM_FONT, corner_radius=8, height=32)
            e_last.grid(row=3, column=0, sticky="we", padx=(10, 6), pady=(0, 10))
            
            e_first = ctk.CTkEntry(midFrame, fg_color=WHITE, text_color=BLACK, font=UNIFORM_FONT, corner_radius=8, height=32)
            e_first.grid(row=3, column=1, sticky="we", padx=6, pady=(0, 10))
            
            e_mi    = ctk.CTkEntry(midFrame, fg_color=WHITE, text_color=BLACK, font=UNIFORM_FONT, corner_radius=8, width=45, height=32)
            e_mi.grid(row=3, column=2, sticky="we", padx=(6, 10), pady=(0, 10))

            tk.Label(midFrame, text="Program", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).grid(row=4, column=0, sticky="w", padx=10, pady=(0, 2))
            tk.Label(midFrame, text="Status",  bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).grid(row=4, column=1, sticky="w", padx=6, pady=(0, 2))
            
            e_program = ctk.CTkEntry(midFrame, fg_color=WHITE, text_color=BLACK, font=UNIFORM_FONT, corner_radius=8, height=32)
            e_program.grid(row=5, column=0, sticky="we", padx=(10, 6), pady=(0, 10))

            statusVar = tk.StringVar()
            statusDrop = ttk.Combobox(midFrame, textvariable=statusVar,
                                      values=["Active", "Inactive", "On Leave"],
                                      state="readonly", font=UNIFORM_FONT)
            statusDrop.grid(row=5, column=1, columnspan=2, sticky="we", padx=(6, 10), pady=(0, 10))
            statusDrop.current(0)

            tk.Label(midFrame, text="Contact", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).grid(row=6, column=0, columnspan=3, sticky="w", padx=10, pady=(0, 2))
            e_contact = ctk.CTkEntry(midFrame, fg_color=WHITE, text_color=BLACK, font=UNIFORM_FONT, corner_radius=8, height=32)
            e_contact.grid(row=7, column=0, columnspan=3, sticky="we", padx=10, pady=(0, 15))

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
                Program = e_program.get().strip()
                Status  = statusVar.get()
                Contact = e_contact.get().strip()

                limits = [(no, 20, "Student No."), (last, 50, "Last Name"),
                          (first, 50, "First Name"), (mi, 2, "Middle Initial"),
                          (Program, 10, "Program"), (Contact, 15, "Contact")]
                for value, limit, lbl in limits:
                    if len(value) > limit:
                        err_label.config(text=f"{lbl} exceeds {limit} character limit.")
                        return

                for value, lbl in [(last, "Last Name"), (first, "First Name"),
                                   (mi, "Middle Initial"), (Program, "Program")]:
                    if value and not re.match(r"^[A-Za-z\s]+$", value):
                        err_label.config(text=f"{lbl} must contain letters only.")
                        return

                if not no or not last or not first:
                    err_label.config(text="Student No., Last Name and First Name are required.")
                    return

                FullName = f"{first} {f'{mi}. ' if mi else ''}{last}".strip()

                if edit_item:
                    original_no = self.tree.item(edit_item, "values")[0]
                    old_values  = self.tree.item(edit_item, "values")
                    self.db.update_student(original_no, no, last, first, mi, Program, Status, Contact)
                    self.tree.item(edit_item, values=(
                        no, FullName, Program, Contact,
                        old_values[4], old_values[5], Status
                    ))
                else:
                    self.db.add_student(no, last, first, mi, Program, Status, Contact)
                    self.tree.insert("", "end", values=(no, FullName, Program, Contact, "", "", Status))

                self.refresh_dashboard()
                win.destroy()

            bottomFrame = ctk.CTkFrame(win, fg_color=content_color, corner_radius=15)
            bottomFrame.pack(fill="x", padx=15, pady=(5, 20))
            
            ctk.CTkButton(bottomFrame, text="Save", font=BOLD_BTN_FONT, fg_color=GREEN_BTN, text_color=WHITE,
                          corner_radius=8, width=90, height=35, hover_color=GREEN_HOVER, command=save).pack(side="right", padx=5)
            ctk.CTkButton(bottomFrame, text="Cancel", font=BOLD_BTN_FONT, fg_color="transparent", text_color="#c0392b",
                          border_width=1, border_color="#c0392b", corner_radius=8, width=90, height=35, hover_color="#fde8e7", command=win.destroy).pack(side="right", padx=5)

        def delete_student():
            selected = self.tree.selection()
            if not selected:
                messagebox.showwarning("Selection Required", "Please click a student record from the table first.")
                return
            if messagebox_confirm("Delete this student? This cannot be undone."):
                StudentNo = self.tree.item(selected[0], "values")[0]
                self.db.remove_student_from_room(StudentNo)
                self.db.delete_student(StudentNo)
                self.tree.delete(selected[0])
                self.db.get_all_rooms(self.rooms_tree)
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
            win.geometry("380x420")
            win.resizable(False, False)
            win.grab_set()

            upperFrame = ctk.CTkFrame(win, fg_color=content_color, corner_radius=15)
            upperFrame.pack(fill="x", padx=15, pady=12)
            tk.Label(upperFrame, text="Assign Room", bg=content_color, fg=FG_DARK, font=("Segoe UI", 15, "bold")).pack(side="left")

            midFrame = ctk.CTkFrame(win, fg_color=WHITE, corner_radius=15, border_width=1, border_color=BORDER)
            midFrame.pack(fill="both", expand=True, padx=15, pady=5)
            midFrame.columnconfigure(0, weight=1)

            tk.Label(midFrame, text=f"Student: {values[1]}", bg=WHITE, fg=FG_DARK, font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 12))
            tk.Label(midFrame, text="Building", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).grid(row=1, column=0, sticky="w", padx=15, pady=(0, 4))

            buildingVar = tk.StringVar()
            buildingDrop = ttk.Combobox(midFrame, textvariable=buildingVar, values=self.db.get_distinct_buildings(), state="readonly", font=UNIFORM_FONT)
            buildingDrop.grid(row=2, column=0, sticky="we", padx=15, pady=(0, 12))

            tk.Label(midFrame, text="Select Room", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).grid(row=3, column=0, sticky="w", padx=15, pady=(0, 4))

            roomVar = tk.StringVar()
            roomDrop = ttk.Combobox(midFrame, textvariable=roomVar, values=[], state="readonly", font=UNIFORM_FONT)
            roomDrop.grid(row=4, column=0, sticky="we", padx=15, pady=(0, 12))

            def on_building_change(event):
                Rooms = self.db.get_rooms_by_building(buildingVar.get())
                roomDrop.config(values=Rooms)
                if Rooms:
                    roomDrop.current(0)
                else:
                    roomVar.set("")

            buildingDrop.bind("<<ComboboxSelected>>", on_building_change)

            tk.Label(midFrame, text="Status", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).grid(row=5, column=0, sticky="w", padx=15, pady=(0, 4))

            statusVar2 = tk.StringVar()
            statusDrop2 = ttk.Combobox(midFrame, textvariable=statusVar2, values=["Active", "Inactive", "On Leave"], state="readonly", font=UNIFORM_FONT)
            statusDrop2.grid(row=6, column=0, sticky="we", padx=15, pady=(0, 15))
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

            bottomFrame = ctk.CTkFrame(win, fg_color=content_color, corner_radius=15)
            bottomFrame.pack(fill="x", padx=15, pady=10)
            
            ctk.CTkButton(bottomFrame, text="Assign", font=BOLD_BTN_FONT, fg_color=GREEN_BTN, text_color=WHITE,
                          corner_radius=8, width=90, height=35, hover_color=GREEN_HOVER, command=save_room).pack(side="right", padx=(5, 0))
            ctk.CTkButton(bottomFrame, text="Cancel", font=BOLD_BTN_FONT, fg_color="transparent", text_color="#c0392b",
                          border_width=1, border_color="#c0392b", corner_radius=8, width=90, height=35, command=win.destroy).pack(side="right")

        def remove_room():
            selected = self.tree.selection()
            if not selected:
                messagebox.showwarning("Selection Required", "Please click a student record from the table first.")
                return
            values = self.tree.item(selected[0], "values")
            if not values[4] or not values[5]:
                messagebox.showinfo("No Assignment", "This student is not currently assigned to any room.")
                return
            if messagebox.askyesno("Unassign Room", f"Remove room assignment for {values[1]}?"):
                self.db.remove_student_from_room(values[0])
                self.db.get_all_rooms(self.rooms_tree)
                self.tree.item(selected[0], values=(
                    values[0], values[1], values[2], values[3],
                    "", "", values[6]
                ))
                self.refresh_dashboard()

        def messagebox_confirm(msg):
            result = [False]
            win = tk.Toplevel()
            win.title("Confirm")
            win.config(bg=WHITE)
            win.geometry("320x140")
            win.resizable(False, False)

            tk.Label(win, text=msg, bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT, wraplength=280).pack(pady=16)
            btn_row = ctk.CTkFrame(win, fg_color=WHITE, corner_radius=15)
            btn_row.pack()

            def confirm():
                result[0] = True
                win.destroy()

            ctk.CTkButton(btn_row, text="Delete", fg_color=RED_BTN, text_color=WHITE, font=BOLD_BTN_FONT, corner_radius=6, width=80, height=30, hover_color=RED_HOVER, command=confirm).pack(side="left", padx=6)
            ctk.CTkButton(btn_row, text="Cancel", fg_color="transparent", text_color=FG_DARK, border_width=1, border_color=BORDER, font=BOLD_BTN_FONT, corner_radius=6, width=80, height=30, command=win.destroy).pack(side="left", padx=6)
            win.grab_set()
            win.wait_window()
            return result[0]

        topbar = ctk.CTkFrame(page, fg_color=content_color, corner_radius=15)
        topbar.pack(fill="x", padx=28, pady=(20, 0))

        tk.Label(topbar, text="Students Directory", bg=content_color, fg=BLACK,
                 font=("Arial", 16, "bold")).pack(side="left", pady=(15, 15))

        filter_bar = ctk.CTkFrame(page, fg_color=content_color, corner_radius=15)
        filter_bar.pack(fill="x", padx=28, pady=(0, 20))

        search_entry = ctk.CTkEntry(filter_bar, fg_color=WHITE, text_color=BLACK, font=UNIFORM_FONT,
                                   placeholder_text=" 🔍  Search students...", corner_radius=10, height=36)
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        def run_search(e=None):
            q = search_entry.get().strip().lower()
            self.db.get_all_students(self.tree)
            if q:
                for row in self.tree.get_children():
                    val = self.tree.item(row, "values")
                    if q not in val[0].lower() and q not in val[1].lower() and q not in val[2].lower():
                        self.tree.delete(row)

        search_entry.bind("<KeyRelease>", run_search)

        ctk.CTkButton(filter_bar, text="＋ Add Student", fg_color=GREEN_BTN, text_color=WHITE, font=BOLD_BTN_FONT,
                      corner_radius=10, height=36, hover_color=GREEN_HOVER, command=add_student_window).pack(side="right")

        card = ctk.CTkFrame(page, fg_color=WHITE, corner_radius=15, border_width=1, border_color=BORDER)
        card.pack(fill="both", expand=True, padx=28, pady=(0, 20))

        tf = ctk.CTkFrame(card, fg_color=WHITE, corner_radius=15)
        tf.pack(fill="both", expand=True, padx=10, pady=(10, 10))

        self.tree = ttk.Treeview(tf, columns=("ID", "Name", "Program", "Contact", "Building", "Room", "Status"),
                                 show="headings", style="Custom.Treeview")

        for col, w, anchor in [("ID", 100, "w"), ("Name", 180, "w"), ("Program", 80, "center"),
                                ("Contact", 110, "center"), ("Building", 100, "center"),
                                ("Room", 80, "center"), ("Status", 90, "center")]:
            self.tree.heading(col, text=col, anchor=anchor)
            self.tree.column(col, width=w, anchor=anchor, stretch=True)

        sb = ttk.Scrollbar(tf, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        action_bar = tk.Frame(card, bg=WHITE)
        action_bar.pack(fill="x", padx=16, pady=(0, 15))

        ctk.CTkButton(action_bar, text="✏️ Edit", fg_color="transparent", text_color=FG_DARK, font=BOLD_BTN_FONT,
                      border_width=1, border_color=BORDER, corner_radius=8, height=32).pack(side="left", padx=(0, 6))
        ctk.CTkButton(action_bar, text="🛏️ Assign Room", fg_color=GREEN_BTN, text_color=WHITE, font=BOLD_BTN_FONT,
                      corner_radius=8, height=32, hover_color=GREEN_HOVER, command=assign_room).pack(side="left", padx=6)
        ctk.CTkButton(action_bar, text="✕ Unassign", fg_color=RED_BTN, text_color=WHITE, font=BOLD_BTN_FONT,
                      corner_radius=8, height=32, hover_color=RED_HOVER, command=remove_room).pack(side="left", padx=6)
        ctk.CTkButton(action_bar, text="🗑️ Delete", fg_color=RED_BTN, text_color=WHITE, font=BOLD_BTN_FONT,
                      corner_radius=8, height=32, hover_color=RED_HOVER, command=delete_student).pack(side="right")

        reload_master()

    def build_rooms_page(self, page):
        def reload_rooms():
            self.db.get_all_rooms(self.rooms_tree)

        def add_room_window(prefill=None, edit_item=None):
            win = tk.Toplevel()
            win.title("Edit Room" if edit_item else "Add Room")
            win.config(bg=content_color)
            win.geometry("420x360")
            win.resizable(False, False)
            win.grab_set()

            upperFrame = ctk.CTkFrame(win, fg_color=content_color, corner_radius=15)
            upperFrame.pack(fill="x", padx=15, pady=12)
            tk.Label(upperFrame, text="Edit Room" if edit_item else "Add Room", bg=content_color, fg=FG_DARK, font=("Segoe UI", 15, "bold")).pack(side="left")

            midFrame = ctk.CTkFrame(win, fg_color=WHITE, corner_radius=15, border_width=1, border_color=BORDER)
            midFrame.pack(fill="both", expand=True, padx=15, pady=5)
            midFrame.columnconfigure(0, weight=1)

            tk.Label(midFrame, text="Building Name", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).grid(row=0, column=0, sticky="w", padx=15, pady=(10, 2))
            e_build = ctk.CTkEntry(midFrame, fg_color=WHITE, text_color=BLACK, font=UNIFORM_FONT, corner_radius=8, height=32)
            e_build.grid(row=1, column=0, sticky="we", padx=15, pady=(0, 10))

            tk.Label(midFrame, text="Room Number", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).grid(row=2, column=0, sticky="w", padx=15, pady=(0, 2))
            e_room = ctk.CTkEntry(midFrame, fg_color=WHITE, text_color=BLACK, font=UNIFORM_FONT, corner_radius=8, height=32)
            e_room.grid(row=3, column=0, sticky="we", padx=15, pady=(0, 10))

            tk.Label(midFrame, text="Capacity", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).grid(row=4, column=0, sticky="w", padx=15, pady=(0, 2))
            e_cap = ctk.CTkEntry(midFrame, fg_color=WHITE, text_color=BLACK, font=UNIFORM_FONT, corner_radius=8, height=32)
            e_cap.grid(row=5, column=0, sticky="we", padx=15, pady=(0, 10))

            statusVar = tk.StringVar()
            statusDrop = ttk.Combobox(midFrame, textvariable=statusVar, values=["Vacant", "Occupied", "Under Maintenance"], state="readonly", font=UNIFORM_FONT)
            statusDrop.grid(row=7, column=0, sticky="we", padx=15, pady=(0, 15))
            statusDrop.current(0)

            if prefill:
                e_room.insert(0, prefill[0])
                e_build.insert(0, prefill[1])
                e_cap.insert(0, prefill[2])
                statusVar.set(prefill[4])

            err_label = tk.Label(win, text="", fg="#c0392b", bg=content_color, font=UNIFORM_FONT)
            err_label.pack()

            def save():
                build = e_build.get().strip()
                room  = e_room.get().strip()
                cap   = e_cap.get().strip()
                stat  = statusVar.get()

                if not build or not room or not cap:
                    err_label.config(text="All fields are required.")
                    return
                try:
                    cap_int = int(cap)
                except ValueError:
                    err_label.config(text="Capacity must be an integer.")
                    return

                if edit_item:
                    RoomID = self.rooms_tree.item(edit_item, "tags")[0]
                    self.db.update_room(RoomID, build, room, cap_int, stat)
                else:
                    self.db.add_room(build, room, cap_int, stat)

                reload_rooms()
                self.refresh_dashboard()
                win.destroy()

            bottomFrame = ctk.CTkFrame(win, fg_color=content_color, corner_radius=15)
            bottomFrame.pack(fill="x", padx=15, pady=(5, 20))
            
            ctk.CTkButton(bottomFrame, text="Save", font=BOLD_BTN_FONT, fg_color=GREEN_BTN, text_color=WHITE, corner_radius=8, width=90, height=35, hover_color=GREEN_HOVER, command=save).pack(side="right", padx=5)
            ctk.CTkButton(bottomFrame, text="Cancel", font=BOLD_BTN_FONT, fg_color="transparent", text_color="#c0392b", border_width=1, border_color="#c0392b", corner_radius=8, width=90, height=35, command=win.destroy).pack(side="right", padx=5)

        def delete_room():
            selected = self.rooms_tree.selection()
            if not selected:
                messagebox.showwarning("Selection Required", "Please click a room record from the table first.")
                return
            if messagebox.askyesno("Delete Room", "Are you sure you want to delete this room record?"):
                RoomID = self.rooms_tree.item(selected[0], "tags")[0]
                self.db.delete_room(RoomID)
                self.rooms_tree.delete(selected[0])
                self.refresh_dashboard()

        def edit_room():
            selected = self.rooms_tree.selection()
            if not selected:
                messagebox.showwarning("Selection Required", "Please click a room record from the table first.")
                return
            add_room_window(prefill=self.rooms_tree.item(selected[0], "values"), edit_item=selected[0])

        topbar = ctk.CTkFrame(page, fg_color=content_color, corner_radius=15)
        topbar.pack(fill="x", padx=28, pady=(20, 0))
        
        tk.Label(topbar, text="Rooms Directory", bg=content_color, fg=BLACK, font=("Arial", 16, "bold")).pack(side="left", pady=(15, 15))

        filter_bar = ctk.CTkFrame(page, fg_color=content_color, corner_radius=15)
        filter_bar.pack(fill="x", padx=28, pady=(0, 20))

        search_entry = ctk.CTkEntry(filter_bar, fg_color=WHITE, text_color=BLACK, font=UNIFORM_FONT,
                                   placeholder_text=" 🔍  Search rooms...", corner_radius=10, height=36)
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        def run_search(e=None):
            q = search_entry.get().strip().lower()
            reload_rooms()
            if q:
                for row in self.rooms_tree.get_children():
                    val = self.rooms_tree.item(row, "values")
                    if q not in val[0].lower() and q not in val[1].lower():
                        self.rooms_tree.delete(row)

        search_entry.bind("<KeyRelease>", run_search)

        ctk.CTkButton(filter_bar, text="＋ Add Room", fg_color=GREEN_BTN, text_color=WHITE, font=BOLD_BTN_FONT,
                      corner_radius=10, height=36, hover_color=GREEN_HOVER, command=add_room_window).pack(side="right")

        card = ctk.CTkFrame(page, fg_color=WHITE, corner_radius=15, border_width=1, border_color=BORDER)
        card.pack(fill="both", expand=True, padx=28, pady=(0, 20))

        tf = ctk.CTkFrame(card, fg_color=WHITE, corner_radius=15)
        tf.pack(fill="both", expand=True, padx=10, pady=(10, 10))

        self.rooms_tree = ttk.Treeview(tf, columns=("RoomNumber", "Building", "Capacity", "Occupants", "Status", "Price"), show="headings", style="Custom.Treeview")
        for col, w, anchor in [("RoomNumber", 100, "center"), ("Building", 150, "w"), ("Capacity", 90, "center"), ("Occupants", 90, "center"), ("Status", 120, "center"), ("Price", 100, "e")]:
            self.rooms_tree.heading(col, text=col, anchor=anchor)
            self.rooms_tree.column(col, width=w, anchor=anchor, stretch=True)

        sb = ttk.Scrollbar(tf, orient="vertical", command=self.rooms_tree.yview)
        self.rooms_tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.rooms_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        action_bar = tk.Frame(card, bg=WHITE)
        action_bar.pack(fill="x", padx=16, pady=(0, 15))

        ctk.CTkButton(action_bar, text="✏️ Edit", fg_color="transparent", text_color=FG_DARK, font=BOLD_BTN_FONT, border_width=1, border_color=BORDER, corner_radius=8, height=32, command=edit_room).pack(side="left", padx=(0, 6))
        ctk.CTkButton(action_bar, text="🗑️ Delete", fg_color=RED_BTN, text_color=WHITE, font=BOLD_BTN_FONT, corner_radius=8, height=32, hover_color=RED_HOVER, command=delete_room).pack(side="right")

        reload_rooms()

    def build_cleaning_page(self, page):
        def reload_master():
            self.db.get_all_cleaning_staff(self.staff_tree)
            self.schedule_tree.delete(*self.schedule_tree.get_children())
            self._selected_cs_id = None

        def load_details(event):
            selected = self.staff_tree.selection()
            if not selected:
                return
            values = self.staff_tree.item(selected[0], "values")
            self._selected_cs_id = values[0]
            self.db.get_schedules_for_staff(self._selected_cs_id, self.schedule_tree)

        def add_staff_window(prefill=None, edit_item=None):
            win = tk.Toplevel()
            win.title("Edit Staff Member" if edit_item else "Add Staff Member")
            win.config(bg=content_color)
            win.geometry("420x420")
            win.resizable(False, False)
            win.grab_set()

            upperFrame = ctk.CTkFrame(win, fg_color=content_color, corner_radius=15)
            upperFrame.pack(fill="x", padx=15, pady=12)
            tk.Label(upperFrame, text="Edit Staff Member" if edit_item else "Add Staff Member", bg=content_color, fg=FG_DARK, font=("Segoe UI", 15, "bold")).pack(side="left")

            midFrame = ctk.CTkFrame(win, fg_color=WHITE, corner_radius=15, border_width=1, border_color=BORDER)
            midFrame.pack(fill="both", expand=True, padx=15, pady=5)
            midFrame.columnconfigure(0, weight=1)

            tk.Label(midFrame, text="Staff ID Number", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).grid(row=0, column=0, sticky="w", padx=15, pady=(10, 2))
            e_id = ctk.CTkEntry(midFrame, fg_color=WHITE, text_color=BLACK, font=UNIFORM_FONT, corner_radius=8, height=32)
            e_id.grid(row=1, column=0, sticky="we", padx=15, pady=(0, 8))

            tk.Label(midFrame, text="First Name", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).grid(row=2, column=0, sticky="w", padx=15, pady=(0, 2))
            e_first = ctk.CTkEntry(midFrame, fg_color=WHITE, text_color=BLACK, font=UNIFORM_FONT, corner_radius=8, height=32)
            e_first.grid(row=3, column=0, sticky="we", padx=15, pady=(0, 8))

            tk.Label(midFrame, text="Last Name", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).grid(row=4, column=0, sticky="w", padx=15, pady=(0, 2))
            e_last = ctk.CTkEntry(midFrame, fg_color=WHITE, text_color=BLACK, font=UNIFORM_FONT, corner_radius=8, height=32)
            e_last.grid(row=5, column=0, sticky="we", padx=15, pady=(0, 8))

            tk.Label(midFrame, text="Contact / Phone", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).grid(row=6, column=0, sticky="w", padx=15, pady=(0, 2))
            e_phone = ctk.CTkEntry(midFrame, fg_color=WHITE, text_color=BLACK, font=UNIFORM_FONT, corner_radius=8, height=32)
            e_phone.grid(row=7, column=0, sticky="we", padx=15, pady=(0, 8))

            tk.Label(midFrame, text="Email Address", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).grid(row=8, column=0, sticky="w", padx=15, pady=(0, 2))
            e_email = ctk.CTkEntry(midFrame, fg_color=WHITE, text_color=BLACK, font=UNIFORM_FONT, corner_radius=8, height=32)
            e_email.grid(row=9, column=0, sticky="we", padx=15, pady=(0, 15))

            if prefill:
                e_id.insert(0, prefill[0])
                e_phone.insert(0, prefill[2])
                e_email.insert(0, prefill[3])
                parts = prefill[1].split()
                if len(parts) >= 1: e_first.insert(0, parts[0])
                if len(parts) >= 2: e_last.insert(0, parts[-1])

            err_label = tk.Label(win, text="", fg="#c0392b", bg=content_color, font=UNIFORM_FONT)
            err_label.pack()

            def save():
                s_id  = e_id.get().strip()
                first = e_first.get().strip()
                last  = e_last.get().strip()
                phone = e_phone.get().strip()
                email = e_email.get().strip()

                if not s_id or not first or not last or not phone or not email:
                    err_label.config(text="All fields are required.")
                    return

                full = f"{first} {last}"
                if edit_item:
                    self.db.update_cleaning_staff(s_id, last, first, "", email, phone, full)
                else:
                    self.db.insert_cleaning_staff(s_id, last, first, "", email, phone, full)

                reload_master()
                self.refresh_dashboard()
                win.destroy()

            bottomFrame = ctk.CTkFrame(win, fg_color=content_color, corner_radius=15)
            bottomFrame.pack(fill="x", padx=15, pady=(5, 20))
            
            ctk.CTkButton(bottomFrame, text="Save Staff", font=BOLD_BTN_FONT, fg_color=GREEN_BTN, text_color=WHITE, corner_radius=8, width=95, height=35, hover_color=GREEN_HOVER, command=save).pack(side="right", padx=5)
            ctk.CTkButton(bottomFrame, text="Cancel", font=BOLD_BTN_FONT, fg_color="transparent", text_color="#c0392b", border_width=1, border_color="#c0392b", corner_radius=8, width=95, height=35, command=win.destroy).pack(side="right", padx=5)

        def delete_staff():
            selected = self.staff_tree.selection()
            if not selected:
                messagebox.showwarning("Selection Required", "Please click a staff member from the top table first.")
                return
            if messagebox.askyesno("Remove Staff Member", "Delete this staff record? All their assigned schedules will be wiped out."):
                values = self.staff_tree.item(selected[0], "values")
                self.db.delete_cleaning_staff(values[0])
                reload_master()
                self.refresh_dashboard()

        def add_schedule_window():
            if not self._selected_cs_id:
                messagebox.showwarning("Selection Required", "Please click a staff member from the top table first.")
                return

            win = tk.Toplevel()
            win.title("Assign Cleaning Task")
            win.config(bg=content_color)
            win.geometry("400x420")
            win.resizable(False, False)
            win.grab_set()

            upperFrame = ctk.CTkFrame(win, fg_color=content_color, corner_radius=15)
            upperFrame.pack(fill="x", padx=15, pady=12)
            tk.Label(upperFrame, text="Assign Cleaning Task", bg=content_color, fg=FG_DARK, font=("Segoe UI", 15, "bold")).pack(side="left")

            midFrame = ctk.CTkFrame(win, fg_color=WHITE, corner_radius=15, border_width=1, border_color=BORDER)
            midFrame.pack(fill="both", expand=True, padx=15, pady=5)
            midFrame.columnconfigure(0, weight=1)

            tk.Label(midFrame, text="Select Building", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).grid(row=0, column=0, sticky="w", padx=15, pady=(10, 2))
            b_var = tk.StringVar()
            b_drop = ttk.Combobox(midFrame, textvariable=b_var, values=self.db.get_distinct_buildings(), state="readonly", font=UNIFORM_FONT)
            b_drop.grid(row=1, column=0, sticky="we", padx=15, pady=(0, 10))

            tk.Label(midFrame, text="Select Room", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).grid(row=2, column=0, sticky="w", padx=15, pady=(0, 2))
            r_var = tk.StringVar()
            r_drop = ttk.Combobox(midFrame, textvariable=r_var, values=[], state="readonly", font=UNIFORM_FONT)
            r_drop.grid(row=3, column=0, sticky="we", padx=15, pady=(0, 10))

            b_drop.bind("<<ComboboxSelected>>", lambda e: r_drop.config(values=self.db.get_rooms_by_building(b_var.get())))

            tk.Label(midFrame, text="Date (MM/DD/YYYY)", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).grid(row=4, column=0, sticky="w", padx=15, pady=(0, 2))
            e_date = ctk.CTkEntry(midFrame, fg_color=WHITE, text_color=BLACK, font=UNIFORM_FONT, corner_radius=8, height=32)
            e_date.grid(row=5, column=0, sticky="we", padx=15, pady=(0, 10))
            e_date.insert(0, datetime.now().strftime("%m/%d/%Y"))

            tk.Label(midFrame, text="Shift Hours (Start — End)", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).grid(row=6, column=0, sticky="w", padx=15, pady=(0, 2))
            time_f = tk.Frame(midFrame, bg=WHITE)
            time_f.grid(row=7, column=0, sticky="we", padx=15, pady=(0, 15))
            time_f.columnconfigure(0, weight=1)
            time_f.columnconfigure(1, weight=1)
            
            e_t1 = ctk.CTkEntry(time_f, fg_color=WHITE, text_color=BLACK, font=UNIFORM_FONT, corner_radius=8, height=32)
            e_t1.grid(row=0, column=0, padx=(0, 4), pady=3, sticky="we")
            e_t1.insert(0, "08:00 AM")
            
            e_t2 = ctk.CTkEntry(time_f, fg_color=WHITE, text_color=BLACK, font=UNIFORM_FONT, corner_radius=8, height=32)
            e_t2.grid(row=0, column=1, padx=(4, 0), pady=3, sticky="we")
            e_t2.insert(0, "10:00 AM")

            err_label = tk.Label(win, text="", fg="#c0392b", bg=content_color, font=UNIFORM_FONT)
            err_label.pack()

            def save_sched():
                b = b_var.get()
                r = r_var.get()
                d_str = e_date.get().strip()
                t1 = e_t1.get().strip()
                t2 = e_t2.get().strip()

                if not b or not r or not d_str or not t1 or not t2:
                    err_label.config(text="All configuration inputs are required.")
                    return
                parts = d_str.split("/")
                if len(parts) != 3:
                    err_label.config(text="Date format must be MM/DD/YYYY.")
                    return

                self.db.add_schedule(self._selected_cs_id, b, r, parts[0], parts[1], parts[2], t1, t2)
                self.db.get_schedules_for_staff(self._selected_cs_id, self.schedule_tree)
                self.refresh_dashboard()
                win.destroy()

            bottomFrame = ctk.CTkFrame(win, fg_color=content_color, corner_radius=15)
            bottomFrame.pack(fill="x", padx=15, pady=(5, 20))
            
            ctk.CTkButton(bottomFrame, text="Assign Task", font=BOLD_BTN_FONT, fg_color=GREEN_BTN, text_color=WHITE, corner_radius=8, width=95, height=35, hover_color=GREEN_HOVER, command=save_sched).pack(side="right", padx=5)
            ctk.CTkButton(bottomFrame, text="Cancel", font=BOLD_BTN_FONT, fg_color="transparent", text_color="#c0392b", border_width=1, border_color="#c0392b", corner_radius=8, width=95, height=35, command=win.destroy).pack(side="right", padx=5)

        def remove_schedule():
            selected = self.schedule_tree.selection()
            if not selected:
                messagebox.showwarning("Selection Required", "Please click a task line from the lower schedule view.")
                return
            if messagebox.askyesno("Remove Task Line", "Delete this shift allocation line permanently?"):
                sched_id = self.schedule_tree.item(selected[0], "tags")[0]
                self.db.delete_schedule(sched_id)
                self.db.get_schedules_for_staff(self._selected_cs_id, self.schedule_tree)
                self.refresh_dashboard()

        topbar = ctk.CTkFrame(page, fg_color=content_color, corner_radius=15)
        topbar.pack(fill="x", padx=28, pady=(20, 0))
        
        tk.Label(topbar, text="Cleaning Services & Utility Logs", bg=content_color, fg=BLACK, font=("Arial", 16, "bold")).pack(side="left", pady=(15, 15))

        master_card = ctk.CTkFrame(page, fg_color=WHITE, corner_radius=15, border_color=BORDER, border_width=1)
        master_card.pack(fill="both", expand=True, padx=28, pady=(0, 10))

        m_bar = tk.Frame(master_card, bg=WHITE)
        m_bar.pack(fill="x", padx=16, pady=(12, 4))
        tk.Label(m_bar, text="Staff Directory", bg=WHITE, fg=FG_DARK, font=("Segoe UI", 11, "bold")).pack(side="left")
        
        ctk.CTkButton(m_bar, text="＋ Register Staff", fg_color=GREEN_BTN, text_color=WHITE, font=BOLD_BTN_FONT, corner_radius=8, height=28, hover_color=GREEN_HOVER, command=add_staff_window).pack(side="right")
        ctk.CTkButton(m_bar, text="🗑️ Unregister", fg_color=RED_BTN, text_color=WHITE, font=BOLD_BTN_FONT, corner_radius=8, height=28, hover_color=RED_HOVER, command=delete_staff).pack(side="right", padx=6)

        master_tf = ctk.CTkFrame(master_card, fg_color=WHITE, corner_radius=15)
        master_tf.pack(fill="both", expand=True, padx=10, pady=(4, 12))

        self.staff_tree = ttk.Treeview(master_tf, columns=("ID", "Name", "Phone", "Email", "ActiveTasks"), show="headings", style="Custom.Treeview", height=6)
        for col, w, anchor in [("ID", 90, "w"), ("Name", 180, "w"), ("Phone", 120, "center"), ("Email", 200, "w"), ("ActiveTasks", 110, "center")]:
            self.staff_tree.heading(col, text=col, anchor=anchor)
            self.staff_tree.column(col, width=w, anchor=anchor, stretch=True)

        msb = ttk.Scrollbar(master_tf, orient="vertical", command=self.staff_tree.yview)
        self.staff_tree.configure(yscrollcommand=msb.set)
        msb.pack(side="right", fill="y")
        self.staff_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.staff_tree.bind("<<TreeviewSelect>>", load_details)

        detail_card = ctk.CTkFrame(page, fg_color=WHITE, corner_radius=15, border_color=BORDER, border_width=1)
        detail_card.pack(fill="both", expand=True, padx=28, pady=(0, 20))

        d_bar = tk.Frame(detail_card, bg=WHITE)
        d_bar.pack(fill="x", padx=16, pady=(12, 4))
        tk.Label(d_bar, text="Assigned Maintenance Duties", bg=WHITE, fg=FG_DARK, font=("Segoe UI", 11, "bold")).pack(side="left")
        
        ctk.CTkButton(d_bar, text="＋ Assign Task Shift", fg_color=GREEN_BTN, text_color=WHITE, font=BOLD_BTN_FONT, corner_radius=8, height=28, hover_color=GREEN_HOVER, command=add_schedule_window).pack(side="right")

        detail_tf = ctk.CTkFrame(detail_card, fg_color=WHITE, corner_radius=15)
        detail_tf.pack(fill="both", expand=True, padx=10, pady=(4, 10))

        self.schedule_tree = ttk.Treeview(detail_tf, columns=("No", "Building", "Room", "Date", "Start", "End"), show="headings", style="Custom.Treeview", height=6)
        for col, w, anchor in [("No", 50, "center"), ("Building", 140, "w"), ("Room", 90, "center"), ("Date", 110, "center"), ("Start", 100, "center"), ("End", 100, "center")]:
            self.schedule_tree.heading(col, text=col, anchor=anchor)
            self.schedule_tree.column(col, width=w, anchor=anchor, stretch=True)

        dsb = ttk.Scrollbar(detail_tf, orient="vertical", command=self.schedule_tree.yview)
        self.schedule_tree.configure(yscrollcommand=dsb.set)
        dsb.pack(side="right", fill="y")
        self.schedule_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        detail_action = tk.Frame(detail_card, bg=WHITE)
        detail_action.pack(fill="x", padx=16, pady=(0, 15))

        detail_hint_lbl = tk.Label(detail_action, text="Click a staff row above to load their schedule.", bg=WHITE, fg=FG_MUTED, font=("Segoe UI", 8))
        detail_hint_lbl.pack(side="left")

        ctk.CTkButton(detail_action, text="✕  Remove assignment", fg_color=RED_BTN, text_color=WHITE, font=BOLD_BTN_FONT,
                      corner_radius=8, height=32, hover_color=RED_HOVER, command=remove_schedule).pack(side="right")

        reload_master()

    
if __name__ == "__main__":
    ctk.set_appearance_mode("System")  
    ctk.set_default_color_theme("blue") 

    root = main()
    root.mainloop()
