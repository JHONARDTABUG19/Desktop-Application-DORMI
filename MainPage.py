import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
import sqlite3
import re
import shutil
import os
from datetime import datetime

UNIFORM_FONT = ("Segoe UI", 10)
BOLD_BTN_FONT = ("Segoe UI", 10, "bold")

WHITE      = "#ffffff"
BLUE       = "#013f9c"
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

    # ── Keep only the 10 most recent backups ──────────────────────────
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

    # ── Dashboard ─────────────────────────────────────────────────────
    def for_dashboard(self):
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute("SELECT COUNT(*) FROM STUDENTS")
            total_students = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM ROOMS")
            total_rooms = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM CLEANING_STAFF")
            total_cleaning_staff = cur.fetchone()[0]
            return total_students, total_rooms, total_cleaning_staff

    # ── STUDENTS ──────────────────────────────────────────────────────
    def create_student_table(self):
        with sqlite3.connect(DB_NAME) as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS STUDENTS (
                    StudentNo      VARCHAR(255) PRIMARY KEY NOT NULL UNIQUE,
                    LastName       VARCHAR(255) NOT NULL,
                    FirstName      VARCHAR(255) NOT NULL,
                    MiddleInitial  VARCHAR(255),
                    Program         VARCHAR(255) NOT NULL,
                    Status          VARCHAR(255) NOT NULL,
                    Contact         VARCHAR(255) NOT NULL
                )
            """)
            con.commit()

    def add_student(self, StudentNo, last, first, mi, Program, Status, Contact):
        with sqlite3.connect(DB_NAME) as con:
            con.execute(
                "INSERT INTO STUDENTS VALUES (?, ?, ?, ?, ?, ?, ?)",
                (StudentNo, last, first, mi, Program, Status, Contact)
            )
            con.commit()

    def get_all_students(self, tree):
        for row in tree.get_children():
            tree.delete(row)
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute("""
                SELECT s.StudentNo,
                    TRIM(s.FirstName || ' ' || COALESCE(s.MiddleInitial || '. ', '') || s.LastName),
                    s.Program, s.Contact,
                    COALESCE(r.Building, ''), COALESCE(r.RoomNumber, ''),
                    s.Status,
                    COALESCE(ra.StartDate, ''), COALESCE(ra.EndDate, '')
                FROM STUDENTS s
                LEFT JOIN ROOM_ASSIGNMENTS ra
                    ON ra.StudentNo = s.StudentNo AND ra.AssignmentStatus = 'Active'
                LEFT JOIN ROOMS r ON r.RoomID = ra.RoomID
            """)
            for row in cur.fetchall():
                tree.insert("", "end", values=row)

    def update_student(self, original_no, StudentNo, last, first, mi, Program, Status, Contact):
        with sqlite3.connect(DB_NAME) as con:
            con.execute("""
                UPDATE STUDENTS
                SET StudentNo=?, LastName=?, FirstName=?, MiddleInitial=?,
                    Program=?, Status=?, Contact=?
                WHERE StudentNo=?
            """, (StudentNo, last, first, mi, Program, Status, Contact, original_no))
            # keep ROOM_ASSIGNMENTS pointing at the (possibly renumbered) student
            con.execute("UPDATE ROOM_ASSIGNMENTS SET StudentNo=? WHERE StudentNo=?",
                        (StudentNo, original_no))
            con.commit()

    def set_student_status(self, StudentNo, Status):
        with sqlite3.connect(DB_NAME) as con:
            con.execute("UPDATE STUDENTS SET Status=? WHERE StudentNo=?", (Status, StudentNo))
            con.commit()

    def delete_student(self, StudentNo):
        with sqlite3.connect(DB_NAME) as con:
            con.execute("DELETE FROM ROOM_ASSIGNMENTS WHERE StudentNo=?", (StudentNo,))
            con.execute("DELETE FROM STUDENTS WHERE StudentNo=?", (StudentNo,))
            con.commit()

    # ── Room Assignments (link table: StudentNo <-> RoomID) ─────────────
    def create_room_assignments_table(self):
        with sqlite3.connect(DB_NAME) as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS ROOM_ASSIGNMENTS (
                    AssignmentID     INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
                    StudentNo        VARCHAR(255) NOT NULL,
                    RoomID           INTEGER NOT NULL,
                    StartDate        VARCHAR(255) DEFAULT '',
                    EndDate          VARCHAR(255) DEFAULT '',
                    AssignmentStatus VARCHAR(255) NOT NULL DEFAULT 'Active',
                    FOREIGN KEY (StudentNo) REFERENCES STUDENTS(StudentNo),
                    FOREIGN KEY (RoomID) REFERENCES ROOMS(RoomID)
                )
            """)
            con.commit()

    def migrate_students_table(self):
        """
        One-time migration: moves Room/Building/RoomStartDate/RoomEndDate
        out of STUDENTS and into ROOM_ASSIGNMENTS (a StudentNo + RoomID
        link table), then rebuilds STUDENTS with only student-owned columns.
        Safe to call every startup -- it's a no-op once already migrated.
        """
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()

            cur.execute("PRAGMA table_info(STUDENTS)")
            existing_cols = [row[1] for row in cur.fetchall()]
            legacy_cols = {"Room", "Building", "RoomStartDate", "RoomEndDate"}
            has_legacy = legacy_cols.issubset(set(existing_cols))

            if not has_legacy:
                return  # already migrated

            # 1) carry any existing room assignments over to ROOM_ASSIGNMENTS
            cur.execute("""
                SELECT StudentNo, Building, Room, RoomStartDate, RoomEndDate
                FROM STUDENTS
                WHERE Room != '' AND Room IS NOT NULL
                  AND Building != '' AND Building IS NOT NULL
            """)
            legacy_assignments = cur.fetchall()

            for StudentNo, Building, Room, StartDate, EndDate in legacy_assignments:
                cur.execute("SELECT RoomID FROM ROOMS WHERE Building=? AND RoomNumber=?",
                            (Building, Room))
                room_row = cur.fetchone()
                if room_row:
                    cur.execute("""
                        INSERT INTO ROOM_ASSIGNMENTS (StudentNo, RoomID, StartDate, EndDate, AssignmentStatus)
                        VALUES (?, ?, ?, ?, 'Active')
                    """, (StudentNo, room_row[0], StartDate or "", EndDate or ""))

            # 2) rebuild STUDENTS without the legacy room columns
            cur.execute("""
                CREATE TABLE Students_new (
                    StudentNo      VARCHAR(255) PRIMARY KEY NOT NULL UNIQUE,
                    LastName       VARCHAR(255) NOT NULL,
                    FirstName      VARCHAR(255) NOT NULL,
                    MiddleInitial  VARCHAR(255),
                    Program         VARCHAR(255) NOT NULL,
                    Status          VARCHAR(255) NOT NULL,
                    Contact         VARCHAR(255) NOT NULL
                )
            """)
            cur.execute("""
                INSERT INTO Students_new (StudentNo, LastName, FirstName, MiddleInitial, Program, Status, Contact)
                SELECT StudentNo, LastName, FirstName, MiddleInitial, Program, Status, Contact FROM STUDENTS
            """)
            cur.execute("DROP TABLE STUDENTS")
            cur.execute("ALTER TABLE Students_new RENAME TO STUDENTS")

            con.commit()

    def update_expired_room_statuses(self):
        """
        For any active room assignment whose EndDate has passed:
          - marks the assignment 'Ended'
          - frees up the room (Occupants - 1, Status back to 'Vacant' if no longer full)
          - marks the student 'Inactive' if they were still 'Active'
        Expects EndDate in 'YYYY-MM-DD' format.
        """
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute("""
                SELECT AssignmentID, StudentNo, RoomID FROM ROOM_ASSIGNMENTS
                WHERE AssignmentStatus='Active'
                  AND EndDate IS NOT NULL AND EndDate != ''
                  AND date(EndDate) < date('now')
            """)
            expired = cur.fetchall()

            for assignment_id, student_no, room_id in expired:
                cur.execute("UPDATE ROOM_ASSIGNMENTS SET AssignmentStatus='Ended' WHERE AssignmentID=?",
                            (assignment_id,))
                cur.execute("UPDATE ROOMS SET Occupants = MAX(0, Occupants - 1) WHERE RoomID=?",
                            (room_id,))
                cur.execute("""UPDATE ROOMS SET Status='Vacant'
                               WHERE RoomID=? AND Occupants < Capacity AND Status='Occupied'""",
                            (room_id,))
                cur.execute("UPDATE STUDENTS SET Status='Inactive' WHERE StudentNo=? AND Status='Active'",
                            (student_no,))
            con.commit()

    def assign_room_to_student(self, StudentNo, Room, Building, RoomStartDate, RoomEndDate):
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()

            cur.execute("SELECT RoomID, Occupants, Capacity FROM ROOMS WHERE Building=? AND RoomNumber=?", (Building, Room))
            room_row = cur.fetchone()
            if not room_row:
                con.commit()
                return
            new_room_id, occupants, capacity = room_row
            
            if occupants >= capacity:
                con.commit()
                return

            # end any current active assignment for this student (frees their old room)
            cur.execute("""
                SELECT AssignmentID, RoomID FROM ROOM_ASSIGNMENTS
                WHERE StudentNo=? AND AssignmentStatus='Active'
            """, (StudentNo,))
            current = cur.fetchone()
            if current:
                old_assignment_id, old_room_id = current
                cur.execute("UPDATE ROOM_ASSIGNMENTS SET AssignmentStatus='Ended' WHERE AssignmentID=?",
                            (old_assignment_id,))
                cur.execute("UPDATE ROOMS SET Occupants = MAX(0, Occupants - 1) WHERE RoomID=?",
                            (old_room_id,))
                cur.execute("""UPDATE ROOMS SET Status='Vacant'
                               WHERE RoomID=? AND Occupants < Capacity AND Status='Occupied'""",
                            (old_room_id,))

            # create the new assignment row (StudentNo + RoomID composite link)
            cur.execute("""
                INSERT INTO ROOM_ASSIGNMENTS (StudentNo, RoomID, StartDate, EndDate, AssignmentStatus)
                VALUES (?, ?, ?, ?, 'Active')
            """, (StudentNo, new_room_id, RoomStartDate, RoomEndDate))

            cur.execute("UPDATE ROOMS SET Occupants = Occupants + 1 WHERE RoomID=?", (new_room_id,))
            cur.execute("""UPDATE ROOMS SET Status='Occupied'
                           WHERE RoomID=? AND Occupants >= Capacity""", (new_room_id,))

            con.commit()

    def remove_student_from_room(self, StudentNo):
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute("""
                SELECT AssignmentID, RoomID FROM ROOM_ASSIGNMENTS
                WHERE StudentNo=? AND AssignmentStatus='Active'
            """, (StudentNo,))
            row = cur.fetchone()
            if row:
                assignment_id, room_id = row
                cur.execute("UPDATE ROOMS SET Occupants = MAX(0, Occupants - 1) WHERE RoomID=?",
                            (room_id,))
                cur.execute("""UPDATE ROOMS SET Status='Vacant'
                               WHERE RoomID=? AND Occupants < Capacity AND Status='Occupied'""",
                            (room_id,))
                cur.execute("UPDATE ROOM_ASSIGNMENTS SET AssignmentStatus='Ended' WHERE AssignmentID=?",
                            (assignment_id,))
            con.commit()

    def seed_sample_students(self):
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute("SELECT COUNT(*) FROM STUDENTS")
            if cur.fetchone()[0] > 0:
                return
            sample = [
                ("2021-00001", "Reyes",      "Maria",    "S", "BSCS",  "Active",   "09171234567"),
                ("2021-00002", "Santos",     "Juan",     "D", "BSIT",  "Active",   "09189876543"),
                ("2021-00003", "Dela Cruz",  "Anna",     "L", "BSN",   "Active",   "09201112222"),
                ("2021-00004", "Garcia",     "Carlo",    "M", "BSEE",  "Inactive", "09333334444"),
                ("2021-00005", "Torres",     "Patricia", "R", "BSME",  "Inactive", "09455556666"),
                ("2022-00001", "Villanueva", "Miguel",   "A", "BSCS",  "Active",   "09567778888"),
                ("2022-00002", "Castillo",   "Sophia",   "B", "BSIT",  "Active",   "09689990000"),
                ("2022-00003", "Morales",    "Andres",   "C", "BSCE",  "Active",   "09701231234"),
                ("2022-00004", "Navarro",    "Isabella", "P", "BSN",   "Inactive", "09823454567"),
                ("2022-00005", "Mendoza",    "Luis",     "T", "BSBA",  "Active",   "09945677890"),
            ]
            cur.executemany(
                "INSERT OR IGNORE INTO STUDENTS VALUES (?, ?, ?, ?, ?, ?, ?)",
                sample
            )
            con.commit()

    # ── ROOMS ─────────────────────────────────────────────────────────
    def create_rooms_table(self):
        with sqlite3.connect(DB_NAME) as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS ROOMS (
                    RoomID      INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
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

    def add_room(self, Building, RoomNumber, Capacity, Status, Price=10000):
        with sqlite3.connect(DB_NAME) as con:
            con.execute(
                "INSERT INTO ROOMS (Building, RoomNumber, Capacity, Status, Price) VALUES (?, ?, ?, ?, ?)",
                (Building, RoomNumber, Capacity, Status, Price)
            )
            con.commit()

    def get_all_rooms(self, tree):
        for row in tree.get_children():
            tree.delete(row)
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute("SELECT RoomID, RoomNumber, Building, Capacity, Occupants, Status, Price FROM ROOMS")
            for row in cur.fetchall():
                tree.insert("", "end", values=row[1:], tags=(row[0],))

    def update_room(self, RoomID, Building, RoomNumber, Capacity, Status, Price=10000):
        with sqlite3.connect(DB_NAME) as con:
            con.execute("""
                UPDATE ROOMS SET Building=?, RoomNumber=?, Capacity=?, Status=?, Price=?
                WHERE RoomID=?
            """, (Building, RoomNumber, Capacity, Status, Price, RoomID))
            con.commit()

    def delete_room(self, RoomID):
        with sqlite3.connect(DB_NAME) as con:
            con.execute("DELETE FROM CLEANING_SCHEDULE WHERE RoomID=?", (RoomID,))
            con.execute("DELETE FROM ROOMS WHERE RoomID=?", (RoomID,))
            con.execute("DELETE FROM ROOMS WHERE RoomID=?", (RoomID,))
            con.commit()

    def get_distinct_buildings(self):
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute("SELECT DISTINCT Building FROM ROOMS ORDER BY Building")
            return [row[0] for row in cur.fetchall()]

    def get_rooms_by_building(self, Building):
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute("""
                SELECT RoomNumber FROM ROOMS
                WHERE Building=? AND Occupants <= Capacity AND Status != 'Under Maintenance'
                ORDER BY RoomNumber
            """, (Building,))
            return [row[0] for row in cur.fetchall()]

    # ── Cleaning Staff ────────────────────────────────────────────────
    def create_table_cleaning_staff(self):
        with sqlite3.connect(DB_NAME) as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS CLEANING_STAFF (
                    StaffID          VARCHAR(255) PRIMARY KEY NOT NULL UNIQUE,
                    LastName      VARCHAR(255) NOT NULL,
                    FirstName     VARCHAR(255) NOT NULL,
                    MiddleInitial VARCHAR(255),
                    Email          VARCHAR(255) UNIQUE NOT NULL,
                    Contact        VARCHAR(255) NOT NULL
                )
            """)
            con.commit()

    def insert_cleaning_staff(self, StaffID, last, first, mi, Email, Contact):
        with sqlite3.connect(DB_NAME) as con:
            con.execute(
                "INSERT INTO CLEANING_STAFF VALUES (?, ?, ?, ?, ?, ?)",
                (StaffID, last, first, mi, Email, Contact)
            )
            con.commit()

    def update_cleaning_staff(self, StaffID, last, first, mi, Email, Contact):
        with sqlite3.connect(DB_NAME) as con:
            con.execute("""
                UPDATE CLEANING_STAFF
                SET LastName=?, FirstName=?, MiddleInitial=?, Email=?, Contact=?
                WHERE StaffID=?
            """, (last, first, mi, Email, Contact, StaffID))
            con.commit()

    def delete_cleaning_staff(self, StaffID):
        with sqlite3.connect(DB_NAME) as con:
            con.execute("DELETE FROM CLEANING_STAFF WHERE StaffID=?", (StaffID,))
            # also remove all their schedules
            con.execute("DELETE FROM CLEANING_SCHEDULE WHERE StaffID=?", (StaffID,))
            con.commit()

    def get_all_cleaning_staff(self, tree):
        """Master list: one row per staff member with assignment count."""
        for row in tree.get_children():
            tree.delete(row)
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute("""
                        SELECT cs.StaffID, cs.LastName || ', ' || cs.FirstName, cs.Contact, cs.Email,
                            COUNT(sch.CleaningSchedID) AS assignments
                        FROM CLEANING_STAFF cs
                        LEFT JOIN CLEANING_SCHEDULE sch 
                            ON cs.StaffID = sch.StaffID
                            AND date(
                                printf('%04d-%02d-%02d', 
                                    CAST(sch.Year AS INT), 
                                    CAST(sch.Month AS INT), 
                                    CAST(sch.Day AS INT))
                            ) >= date('now')
                        GROUP BY cs.StaffID
                        ORDER BY cs.LastName || ', ' || cs.FirstName
                    """)

            for row in cur.fetchall():
                tree.insert("", "end", values=row)

    # ── Cleaning Schedule ─────────────────────────────────────────────
    def create_cleaning_schedule_table(self):
        with sqlite3.connect(DB_NAME) as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS CLEANING_SCHEDULE (
                    CleaningSchedID        INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
                    StaffID   VARCHAR(255) NOT NULL,
                    RoomID    INTEGER NOT NULL,
                    Month     VARCHAR(255) NOT NULL,
                    Day       VARCHAR(255) NOT NULL,
                    Year      VARCHAR(255) NOT NULL,
                    TimeStart VARCHAR(255) NOT NULL,
                    TimeEnd   VARCHAR(255) NOT NULL,
                    FOREIGN KEY (StaffID) REFERENCES CLEANING_STAFF(StaffID),
                    FOREIGN KEY (RoomID)  REFERENCES ROOMS(RoomID)
                )
            """)
            con.commit()

    def migrate_cleaning_schedule_table(self):
        """
        One-time migration: replaces Building + Room text columns in
        CLEANING_SCHEDULE with a single RoomID FK referencing ROOMS(RoomID).
        Safe to call every startup — no-op once already migrated.
        """
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()

            cur.execute("PRAGMA table_info(CLEANING_SCHEDULE)")
            cols = [row[1] for row in cur.fetchall()]
            if "Building" not in cols:
                return  # already migrated

            # Carry existing text-based rows over to RoomID references
            cur.execute("""
                SELECT CleaningSchedID, StaffID, Building, Room, Month, Day, Year, TimeStart, TimeEnd
                FROM CLEANING_SCHEDULE
            """)
            old_rows = cur.fetchall()

            cur.execute("""
                CREATE TABLE cleaning_schedule_new (
                    CleaningSchedID        INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
                    StaffID   VARCHAR(255) NOT NULL,
                    RoomID    INTEGER NOT NULL,
                    Month     VARCHAR(255) NOT NULL,
                    Day       VARCHAR(255) NOT NULL,
                    Year      VARCHAR(255) NOT NULL,
                    TimeStart VARCHAR(255) NOT NULL,
                    TimeEnd   VARCHAR(255) NOT NULL,
                    FOREIGN KEY (StaffID) REFERENCES CLEANING_STAFF(StaffID),
                    FOREIGN KEY (RoomID)  REFERENCES ROOMS(RoomID)
                )
            """)

            for row in old_rows:
                _, staff_id, building, room, month, day, year, ts, te = row
                cur.execute(
                    "SELECT RoomID FROM ROOMS WHERE Building=? AND RoomNumber=?",
                    (building, room)
                )
                room_row = cur.fetchone()
                if room_row:   # skip orphaned rows with no matching room
                    cur.execute("""
                        INSERT INTO cleaning_schedule_new
                            (StaffID, RoomID, Month, Day, Year, TimeStart, TimeEnd)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (staff_id, room_row[0], month, day, year, ts, te))

            cur.execute("DROP TABLE CLEANING_SCHEDULE")
            cur.execute("ALTER TABLE cleaning_schedule_new RENAME TO CLEANING_SCHEDULE")
            con.commit()

    def get_schedules_for_staff(self, StaffID, tree):
        """Detail panel: all schedule rows for one staff member, joined with ROOMS."""
        for row in tree.get_children():
            tree.delete(row)
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute("""
                SELECT sch.CleaningSchedID, r.Building, r.RoomNumber,
                       sch.Month || '/' || sch.Day || '/' || sch.Year,
                       sch.TimeStart, sch.TimeEnd
                FROM CLEANING_SCHEDULE sch
                JOIN ROOMS r ON r.RoomID = sch.RoomID
                WHERE sch.StaffID = ?
                ORDER BY sch.Year, sch.Month, sch.Day, sch.TimeStart
            """, (StaffID,))
            for i, row in enumerate(cur.fetchall(), start=1):
                sched_id = row[0]
                values   = (i,) + row[1:]    # prepend row number; store sched_id as tag
                tree.insert("", "end", values=values, tags=(sched_id,))

    def add_schedule(self, StaffID, Building, Room, Month, Day, Year, TimeStart, TimeEnd):
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute(
                "SELECT RoomID FROM ROOMS WHERE Building=? AND RoomNumber=?",
                (Building, Room)
            )
            room_row = cur.fetchone()
            if not room_row:
                raise ValueError(f"Room '{Room}' in building '{Building}' not found.")
            cur.execute("""
                INSERT INTO CLEANING_SCHEDULE
                    (StaffID, RoomID, Month, Day, Year, TimeStart, TimeEnd)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (StaffID, room_row[0], Month, Day, Year, TimeStart, TimeEnd))
            con.commit()

    def delete_schedule(self, sched_id):
        with sqlite3.connect(DB_NAME) as con:
            con.execute("DELETE FROM CLEANING_SCHEDULE WHERE CleaningSchedID=?", (sched_id,))
            con.commit()

    #============================================================
    #new add for dashboard

    def get_assigned_students(self):
        with sqlite3.connect(DB_NAME) as connect:
            cursor = connect.cursor()
            cursor.execute("""
                SELECT TRIM(s.FirstName || ' ' || s.LastName), r.Building, r.RoomNumber, s.Status
                FROM ROOM_ASSIGNMENTS ra
                JOIN STUDENTS s ON s.StudentNo = ra.StudentNo
                JOIN ROOMS r ON r.RoomID = ra.RoomID
                WHERE ra.AssignmentStatus = 'Active'
                ORDER BY r.Building, r.RoomNumber
            """)
            return cursor.fetchall()

    

    def get_todays_cleaning_assignments(self):
        with sqlite3.connect(DB_NAME) as connect:
            cursor = connect.cursor()
            cursor.execute("""
                SELECT cs.StaffID, cs.FirstName || ' ' || cs.LastName AS StaffName,
                    r.Building || ' ' || r.RoomNumber,
                    sch.TimeStart, sch.TimeEnd,
                    sch.Month || '/' || sch.Day || '/' || sch.Year
                FROM CLEANING_SCHEDULE sch
                JOIN CLEANING_STAFF cs ON cs.StaffID = sch.StaffID
                JOIN ROOMS r          ON r.RoomID   = sch.RoomID
                WHERE date(
                    printf('%04d-%02d-%02d',
                        CAST(sch.Year  AS INT),
                        CAST(sch.Month AS INT),
                        CAST(sch.Day   AS INT))
                ) >= date('now')
                ORDER BY sch.Year, sch.Month, sch.Day, sch.TimeStart
            """)
            return cursor.fetchall()
    
    def get_total_revenue_this_month(self):
        from datetime import datetime
        today = datetime.now()
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute("SELECT COALESCE(SUM(Price), 0) FROM ROOMS WHERE Occupants > 0")
            return cur.fetchone()[0]

    def get_total_available_slots(self):
        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute("SELECT COALESCE(SUM(Capacity - Occupants), 0) FROM ROOMS")
            return cur.fetchone()[0]
    


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
        auto_backup()
        self.db.create_student_table()
        self.db.create_rooms_table()
        self.db.create_table_cleaning_staff()
        self.db.create_cleaning_schedule_table()
        self.db.create_room_assignments_table()
        self.db.migrate_students_table()
        self.db.migrate_cleaning_schedule_table()
        self.db.update_expired_room_statuses()
        
        
        self.db.seed_sample_students()

        self.all_pages   = []
        self.all_buttons = []

        # Will hold the StaffID of whichever staff row is selected
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

        hover_color = "#153769"

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
        def confirm_logout():
            if messagebox.askyesno("Log Out", "Are you sure you want to log out?"):
                self.destroy()

        tk.Button(self.sidebar, text="⏻  Log Out",
        bg="#c0392b", fg="white", font=BOLD_BTN_FONT,
        relief="flat", anchor="w", padx=10, pady=8,
        cursor="hand2", command=confirm_logout).pack(
            side="bottom", fill="x", padx=10, pady=(0, 15))

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


        self.trevNum = make_card(cards_frame, "#A5AB2E", "💰", "trevNum", "Collection this month")
        self.tsNum  = make_card(cards_frame, "#8A5F41", "🧑",  "tsNum",  "Total Students")
        self.trNum  = make_card(cards_frame, "#4A8C7A", "🛏️", "trNum",  "Total Rooms")
        self.tcNum  = make_card(cards_frame, "#A05C6A", "🧹",  "tcNum",  "Cleaning staff")
        self.tavNum  = make_card(cards_frame, "#27ae60", "🏠", "tavNum",  "Can accommodate")

        tk.Label(page, text="Recent student assignments", bg=content_color,
                 font=("Arial", 12, "bold"), fg="black").pack(anchor="w", pady=5, padx=30)

    
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dashboard.Treeview",
                        background=WHITE,
                        foreground="#000000",
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
                foreground=[("selected", "#000000")])
        style.layout("Dashboard.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

        
        stu_frame = tk.Frame(page, bg=WHITE, highlightbackground="#d0c4b0", highlightthickness=1)
        stu_frame.pack(fill="both", padx=20, pady=10)
        self.treeStuAss = ttk.Treeview(stu_frame, columns=("Student", "Building", "Room", "Status"),
                                        show="headings", style="Dashboard.Treeview", height=5)
        for col, w, anchor in [("Student", 150, "w"), ("Building", 80, "center"),
                                ("Room", 80, "center"), ("Status", 90, "center")]:
            self.treeStuAss.heading(col, text=col, anchor=anchor)
            self.treeStuAss.column(col, width=w, anchor=anchor, stretch=True)
        self.treeStuAss.pack(fill="both", expand=True)

        tk.Label(page, text="Upcoming cleaning assignments", bg=content_color,
                 font=("Arial", 12, "bold"), fg="black").pack(anchor="w", pady=5, padx=30)

        clean_frame = tk.Frame(page, bg=WHITE, highlightbackground="#d0c4b0", highlightthickness=1)
        clean_frame.pack(fill="both", padx=20, pady=10)
        self.treeCleanAss = ttk.Treeview(clean_frame, columns=("ID", "StaffName", "Room", "TimeStart", "TimeEnd", "Date"),
                                        show="headings", style="Dashboard.Treeview", height=5)
        for col, w, anchor in [("ID", 80, "w"), ("StaffName", 180, "w"), ("Room", 100, "center"),
                                ("TimeStart", 100, "center"), ("TimeEnd", 100, "center"), ("Date", 100, "center")]:
            self.treeCleanAss.heading(col, text=col, anchor=anchor)
            self.treeCleanAss.column(col, width=w, anchor=anchor, stretch=True)
        self.treeCleanAss.pack(fill="both", expand=True)


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
                                      values=["Active", "Inactive"],
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
                Program = e_program.get().strip()
                Status  = statusVar.get()
                Contact = e_contact.get().strip()

                limits = [(no, 20, "Student No."), (last, 50, "Last Name"),
                          (first, 50, "First Name"), (mi, 2, "Middle Initial"),
                          (Program, 10, "Program"), (Contact, 11, "Contact")]
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
                    old_status  = old_values[6]

                    self.db.update_student(original_no, no, last, first, mi, Program, Status, Contact)

                    if old_status == "Active" and Status == "Inactive" and old_values[4] and old_values[5]:
                        self.db.remove_student_from_room(no)
                        self.db.get_all_rooms(self.rooms_tree)

                else:
                    self.db.add_student(no, last, first, mi, Program, Status, Contact)

                self.db.get_all_students(self.tree)
                update_count()
                self.refresh_dashboard()
                win.destroy()

            bottomFrame = tk.Frame(win, bg=content_color)
            bottomFrame.pack(fill="x", padx=15, pady=(0, 20))
            tk.Button(bottomFrame, text="Save",   font=BOLD_BTN_FONT, bg=GREEN_BTN, fg=WHITE,
                      relief="flat", padx=12, pady=0, cursor="hand2",
                      command=save).pack(side="right", padx=5)
            tk.Button(bottomFrame, text="Cancel", font=BOLD_BTN_FONT, bg=RED_BTN, fg=WHITE,
                      relief="flat", padx=12, pady=0, cursor="hand2",
                      command=win.destroy).pack(side="right", padx=5)

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
            win.geometry("360x500")
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
                ROOMS = self.db.get_rooms_by_building(buildingVar.get())
                roomDrop.config(values=ROOMS)
                if ROOMS:
                    roomDrop.current(0)
                else:
                    roomVar.set("")

            buildingDrop.bind("<<ComboboxSelected>>", on_building_change)

            tk.Label(midFrame, text="Status", bg=WHITE, fg=FG_DARK,
                     font=UNIFORM_FONT).grid(row=5, column=0, sticky="w", pady=(0, 4))
            statusVar2 = tk.StringVar()
            statusDrop2 = ttk.Combobox(midFrame, textvariable=statusVar2,
                                       values=["Active", "Inactive"],
                                       state="readonly", font=UNIFORM_FONT)
            statusDrop2.grid(row=6, column=0, sticky="we")
            statusVar2.set(values[6] if values[6] else "Active")

            def validate_date_input(P):
                # Allow only digits and dashes (for YYYY-MM-DD typing)
                return all(c.isdigit() or c == "-" for c in P)

            vcmd_date = (win.register(validate_date_input), "%P")

            tk.Label(midFrame, text="Start Date (YYYY-MM-DD)", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).grid(row=7, column=0, sticky="w", pady=(0, 4))
            startDateEntry = tk.Entry(midFrame, font=UNIFORM_FONT,
                                       validate="key", validatecommand=vcmd_date)
            startDateEntry.grid(row=8, column=0, sticky="we", padx=(0, 4))

            tk.Label(midFrame, text="End Date (YYYY-MM-DD)", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).grid(row=9, column=0, sticky="w", pady=(0, 4))
            endDateEntry = tk.Entry(midFrame, font=UNIFORM_FONT,
                                     validate="key", validatecommand=vcmd_date)
            endDateEntry.grid(row=10, column=0, sticky="we", padx=(0, 4), pady=(0, 12))

            def save_room():
                if not buildingVar.get() or not roomVar.get():
                    return
                self.db.assign_room_to_student(values[0], roomVar.get(), buildingVar.get(), startDateEntry.get(), endDateEntry.get())
                self.db.set_student_status(values[0], statusVar2.get())
                self.db.update_expired_room_statuses()
                self.db.get_all_rooms(self.rooms_tree)
                self.db.get_all_students(self.tree)
                self.refresh_dashboard()
                win.destroy()

            bottomFrame = tk.Frame(win, bg=content_color)
            bottomFrame.pack(fill="x", padx=15, pady=10)
            tk.Button(bottomFrame, text="Assign", font=BOLD_BTN_FONT, bg=GREEN_BTN, fg=WHITE,
                      relief="flat", padx=12, pady=5, cursor="hand2",
                      command=save_room).pack(side="right", padx=(5, 0))
            tk.Button(bottomFrame, text="Cancel", font=BOLD_BTN_FONT, bg=RED_BTN, fg=WHITE,
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
            tk.Button(btn_row, text="Delete", bg="#c0392b", fg=WHITE, font=BOLD_BTN_FONT,
                      relief="flat", padx=14, pady=4, cursor="hand2",
                      command=confirm).pack(side="left", padx=6)
            tk.Button(btn_row, text="Cancel", bg=BLUE, fg=WHITE, font=BOLD_BTN_FONT,
                      relief="solid", bd=0, padx=14, pady=4, cursor="hand2",
                      command=win.destroy).pack(side="left", padx=6)
            win.grab_set()
            win.wait_window()
            return result[0]

        # topbar
        topbar = tk.Frame(page, bg=content_color)
        topbar.pack(fill="x", padx=28, pady=(20, 12))
        tk.Label(topbar, text="Students", bg=content_color, fg=FG_DARK,
                 font=("Segoe UI", 17, "bold")).pack(side="left")
        tk.Button(topbar, text="+ Add student", bg=GREEN_BTN, fg=WHITE,
                  font=BOLD_BTN_FONT, relief="solid", bd=0, padx=12, pady=5,
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
            if q == "search by ID or name...": q = ""
            for r in self.tree.get_children(): self.tree.delete(r)
            with sqlite3.connect(DB_NAME) as con:
                cur = con.cursor()
                cur.execute("""
                    SELECT s.StudentNo,
                        TRIM(s.FirstName || ' ' || COALESCE(s.MiddleInitial || '. ', '') || s.LastName),
                        s.Program, s.Contact,
                        COALESCE(r.Building, ''), COALESCE(r.RoomNumber, ''),
                        s.Status,
                        COALESCE(ra.StartDate, ''), COALESCE(ra.EndDate, '')
                    FROM STUDENTS s
                    LEFT JOIN ROOM_ASSIGNMENTS ra
                        ON ra.StudentNo = s.StudentNo AND ra.AssignmentStatus = 'Active'
                    LEFT JOIN ROOMS r ON r.RoomID = ra.RoomID
                    WHERE LOWER(s.StudentNo) LIKE ? OR LOWER(s.FirstName || ' ' || s.LastName) LIKE ?
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
        style.configure("STUDENTS.Treeview", background=WHITE, foreground="#000000",
                        rowheight=36, fieldbackground=WHITE, borderwidth=0, font=UNIFORM_FONT)
        style.configure("STUDENTS.Treeview.Heading", background=HEADER_BG, foreground="#000000",
                        font=("Segoe UI", 9, "bold"), relief="flat", padding=(8, 6))
        style.map("STUDENTS.Treeview", background=[("selected", ROW_SEL)], foreground=[("selected", "#000000")])
        style.layout("STUDENTS.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

        tree_frame = tk.Frame(card, bg=WHITE)
        tree_frame.pack(fill="both", expand=True, padx=16)

        self.tree = ttk.Treeview(tree_frame,
                         columns=("StudentNo", "name", "Program", "Contact", "Building", "Room", "Status", "StartDate", "EndDate"),
                         displaycolumns=("StudentNo", "name", "Program", "Building", "Room", "StartDate", "EndDate", "Status"),
                         show="headings", style="STUDENTS.Treeview", selectmode="browse")
        for cid, heading, width, anchor in [
            ("StudentNo", "Student no.", 120, "w"), ("name", "Name", 190, "w"),
            ("Program", "Program", 100, "center"),
            ("Building", "Building", 100, "center"), ("Room", "Room", 80, "center"),("StartDate", "Start", 100, "center"), 
            ("EndDate", "End", 100, "center"), ("Status", "Status", 100, "center")
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

        self.count_label = tk.Label(action_bar, text="0 Students", bg=WHITE, fg=FG_MUTED, font=UNIFORM_FONT)
        self.count_label.pack(side="left", padx=(4, 0))

        def update_count():
            n = len(self.tree.get_children())
            self.count_label.config(text=f"{n} student{'s' if n != 1 else ''}")

        def move_out_student():
            selected = self.tree.selection()
            if not selected:
                messagebox.showwarning("Selection Required", "Please click a student record from the table first.")
                return
            values = self.tree.item(selected[0], "values")
            StudentNo = values[0]
            Name = values[1]
            # Check if student has an active room assignment
            if not values[4] and not values[5]:
                messagebox.showinfo("No Room Assigned", f"{Name} is not currently assigned to any room.")
                return
            if messagebox_confirm(f"Move out {Name} from their current room? This will clear their room assignment."):
                self.db.remove_student_from_room(StudentNo)
                self.db.get_all_students(self.tree)
                self.db.get_all_rooms(self.rooms_tree)
                self.refresh_dashboard()

        btn_cfg = dict(bg=BLUE, fg=WHITE, font=BOLD_BTN_FONT,
                       relief="solid", bd=0, padx=14, pady=5, cursor="hand2")
        tk.Button(action_bar, text="✏  Edit",        command=edit_student,  **btn_cfg).pack(side="right", padx=4)
        tk.Button(action_bar, text="⊞  Assign Room", command=assign_room,
                  bg=GREEN_BTN, fg=WHITE, font=BOLD_BTN_FONT,
                       relief="solid", bd=0, padx=14, pady=5, cursor="hand2").pack(side="right", padx=4)
        tk.Button(action_bar, text="🚪  Move Out",
                  bg="#e67e22", fg=WHITE, font=BOLD_BTN_FONT,
                  relief="solid", bd=0, padx=14, pady=5, cursor="hand2",
                  command=move_out_student).pack(side="right", padx=4)
        tk.Button(action_bar, text="🗑  Delete",
                  bg=RED_BTN, fg=WHITE, font=BOLD_BTN_FONT,
                  relief="solid", bd=0, padx=14, pady=5, cursor="hand2",
                  command=delete_student).pack(side="right", padx=4)

        tk.Label(card, text="ⓘ  Click a row to select before editing, assigning, moving out, or deleting.",
                 bg=WHITE, fg=FG_MUTED, font=("Segoe UI", 8), anchor="w").pack(fill="x", padx=20, pady=(0, 10))

        self.db.update_expired_room_statuses()
        self.db.get_all_students(self.tree)
        update_count()

    # ── ROOMS page ────────────────────────────────────────────────────
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
            tk.Button(btn_row, text="Delete", bg="#c0392b", fg=WHITE, font=BOLD_BTN_FONT,
                      relief="flat", padx=14, pady=4, cursor="hand2", command=confirm).pack(side="left", padx=6)
            tk.Button(btn_row, text="Cancel", bg=WHITE, fg=FG_DARK, font=BOLD_BTN_FONT,
                      relief="solid", bd=1, padx=14, pady=4, cursor="hand2",
                      command=win.destroy).pack(side="left", padx=6)
            win.grab_set(); win.wait_window(); return result[0]

        topbar = tk.Frame(page, bg=content_color)
        topbar.pack(fill="x", padx=28, pady=(20, 12))
        tk.Label(topbar, text="Rooms", bg=content_color, fg=FG_DARK,
                 font=("Segoe UI", 17, "bold")).pack(side="left")
        add_btn = tk.Button(topbar, text="+ Add Room", bg=GREEN_BTN, fg=WHITE,
                            font=BOLD_BTN_FONT, relief="solid", bd=0, padx=12, pady=5, cursor="hand2")
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
                rsearch.delete(0, "end"); rsearch.config(fg="#000000")
        def on_rfo(e):
            if not rsearch.get().strip():
                rsearch.insert(0, "Search by Room No. or Building..."); rsearch.config(fg="#000000")
        rsearch.bind("<FocusIn>",  on_rfi)
        rsearch.bind("<FocusOut>", on_rfo)

        def do_rsearch():
            q = rsearch.get().strip().lower()
            if q == "search by Room no. or Building...": q = ""
            for r in self.rooms_tree.get_children(): self.rooms_tree.delete(r)
            with sqlite3.connect(DB_NAME) as con:
                cur = con.cursor()
                cur.execute("""
                    SELECT RoomID, RoomNumber, Building, Capacity, Occupants, Status, Price
                    FROM ROOMS WHERE LOWER(RoomNumber) LIKE ? OR LOWER(Building) LIKE ?
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
                    cur.execute("SELECT RoomID, RoomNumber, Building, Capacity, Occupants, Status, Price FROM ROOMS")
                else:
                    cur.execute("SELECT RoomID, RoomNumber, Building, Capacity, Occupants, Status, Price FROM ROOMS WHERE Status=?",
                                (status_filter,))
                for r in cur.fetchall():
                    self.rooms_tree.insert("", "end", values=r[1:], tags=(r[0],))

        for lbl, color, sv in [("All", FG_DARK, "All"), ("Vacant", "#27ae60", "Vacant"),
                                ("Occupied", "#8e44ad", "Occupied"), ("Maintenance", "#e67e22", "Under Maintenance")]:
            tk.Button(filter_frame, text=lbl, bg=WHITE, fg=color, font=("Segoe UI", 8),
                      relief="solid", bd=1, padx=10, pady=3, cursor="hand2",
                      command=lambda s=sv: filter_by_status(s)).pack(side="left", padx=3)

        style = ttk.Style()
        style.configure("ROOMS.Treeview", background=WHITE, foreground="#000000",
                        rowheight=36, fieldbackground=WHITE, borderwidth=0, font=UNIFORM_FONT)
        style.configure("ROOMS.Treeview.Heading", background=HEADER_BG, foreground="#000000",
                        font=("Segoe UI", 9, "bold"), relief="flat", padding=(8, 6))
        style.map("ROOMS.Treeview", background=[("selected", ROW_SEL)], foreground=[("selected", "#000000")])
        style.layout("ROOMS.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

        tree_frame = tk.Frame(card, bg=WHITE)
        tree_frame.pack(fill="both", expand=True, padx=16)

        self.rooms_tree = ttk.Treeview(tree_frame,
                                       columns=("room_no", "Building", "Capacity", "Occupants", "Status", "Price"),
                                       show="headings", style="ROOMS.Treeview", selectmode="browse")
        for cid, heading, width, anchor in [
            ("room_no", "Room No.", 90, "center"), ("Building", "Building", 70, "center"),
            ("Capacity", "Capacity", 80, "center"),
            ("Occupants", "Occupants", 90, "center"), ("Status", "Status", 120, "center"), ("Price", "Price", 100, "center")
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

        room_count_lbl = tk.Label(action_bar, text="0 Rooms total", bg=WHITE, fg=FG_MUTED, font=UNIFORM_FONT)
        room_count_lbl.pack(side="left", padx=(4, 0))

        def update_room_count():
            n = len(self.rooms_tree.get_children())
            room_count_lbl.config(text=f"{n} Room{'s' if n != 1 else ''} total")

        def add_room_window(prefill=None, edit_item=None):
            win = tk.Toplevel()
            win.title("Edit Room" if edit_item else "Add Room")
            win.config(bg=content_color)
            win.geometry("420x340")
            win.resizable(False, False)
            win.grab_set()

            upperFrame = tk.Frame(win, bg=content_color)
            upperFrame.pack(fill="x", padx=15, pady=(9,5))
            tk.Label(upperFrame, text="Edit Room" if edit_item else "Add Room",
                     bg=content_color, fg=FG_DARK, font=("Segoe UI", 15, "bold")).pack(side="left")

            midFrame = tk.Frame(win, bg=WHITE, padx=15, pady=10,
                                bd=1, relief="solid", highlightbackground=BORDER)
            midFrame.pack(fill="both", expand=True, padx=15)
            
            midFrame.columnconfigure(0, weight=1)
            midFrame.columnconfigure(1, weight=1)

            # Row 0 — labels
            tk.Label(midFrame, text="Building",     bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).grid(row=0, column=0, sticky="w", padx=(0,6), pady=(0,2))
            tk.Label(midFrame, text="Room Number",  bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).grid(row=0, column=1, sticky="w", padx=(6,0), pady=(0,2))

            # Row 1 — Building drop | Room number entry
            buildingVar = tk.StringVar()
            buildingDrop = ttk.Combobox(midFrame, textvariable=buildingVar,
                                        values=["BLD-A", "BLD-B", "BLD-C"],
                                        state="readonly", font=UNIFORM_FONT)
            buildingDrop.grid(row=1, column=0, sticky="we", padx=(0,6), pady=(0,12))
            buildingDrop.current(0)

            nb = tk.Frame(midFrame, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
            nb.grid(row=1, column=1, sticky="we", padx=(6,0), pady=(0,12))
            vcmd = (win.register(lambda P: (P.isdigit() or P == "") and len(P) <= 3), "%P")
            roomNumEntry = tk.Entry(nb, bg=WHITE, fg=BLACK, font=UNIFORM_FONT,
                                    relief="flat", bd=0, insertbackground=FG_DARK,
                                    validate="key", validatecommand=vcmd)
            roomNumEntry.pack(fill="x", padx=5, pady=3)

            # Row 2 — labels
            tk.Label(midFrame, text="Capacity", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).grid(row=2, column=0, sticky="w", padx=(0,6), pady=(0,2))
            tk.Label(midFrame, text="Status",   bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).grid(row=2, column=1, sticky="w", padx=(6,0), pady=(0,2))

            # Row 3 — Capacity drop | Status drop
            capacityVar = tk.StringVar()
            capDrop = ttk.Combobox(midFrame, textvariable=capacityVar,
                                values=["1","2","3","4","5","6","7","8"],
                                state="readonly", font=UNIFORM_FONT)
            capDrop.grid(row=3, column=0, sticky="we", padx=(0,6), pady=(0,12))
            capDrop.current(0)

            statusVar = tk.StringVar()
            statusDrop = ttk.Combobox(midFrame, textvariable=statusVar,
                                    values=["Vacant", "Occupied", "Under Maintenance"],
                                    state="readonly", font=UNIFORM_FONT)
            statusDrop.grid(row=3, column=1, sticky="we", padx=(6,0), pady=(0,12))
            statusDrop.current(0)

            # Row 4 — Price label (right column only)
            tk.Label(midFrame, text="Price", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).grid(row=4, column=1, sticky="w", padx=(6,0), pady=(0,2))

            # Row 5 — Price entry (right column only, readonly)
            priceF = tk.Frame(midFrame, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
            priceF.grid(row=5, column=1, sticky="we", padx=(6,0), pady=(0,12))
            vcmd_price = (win.register(lambda P: P == "" or P.isdigit()), "%P")
            priceEntry = tk.Entry(priceF, bg=WHITE, fg=BLACK, font=UNIFORM_FONT,
                                relief="flat", bd=0, insertbackground=FG_DARK,
                                validate="key", validatecommand=vcmd_price)
            priceEntry.pack(fill="x", padx=5, pady=3)
            priceEntry.insert(0, "10000")


            if prefill:
                buildingVar.set(prefill[1])
                roomNumEntry.insert(0, prefill[0])
                capacityVar.set(str(prefill[2]))
                statusVar.set(prefill[4])
                priceEntry.delete(0, "end")
                priceEntry.insert(0, str(int(float(prefill[5]))))

            err_label = tk.Label(win, text="", fg="#c0392b", bg=content_color, font=UNIFORM_FONT)
            err_label.pack()

            def save_room():
                room_no = roomNumEntry.get().strip()
                if not room_no:
                    err_label.config(text="Room number is required."); return
                price = priceEntry.get().strip()
                if not price:
                    err_label.config(text="Price is required."); return

                if edit_item:
                    RoomID = self.rooms_tree.item(edit_item, "tags")[0]
                    self.db.update_room(RoomID, buildingVar.get(), room_no,
                                        int(capacityVar.get()), statusVar.get(), int(price))
                else:
                    self.db.add_room(buildingVar.get(), room_no,
                                     int(capacityVar.get()), statusVar.get(), int(price))
                self.db.get_all_rooms(self.rooms_tree)
                update_room_count()
                self.refresh_dashboard()
                win.destroy()

            bf = tk.Frame(win, bg=content_color)
            bf.pack(fill="x", padx=15, pady=15)
            tk.Button(bf, text="Save", font=BOLD_BTN_FONT, bg=GREEN_BTN, fg=WHITE,
                      relief="flat", padx=12, pady=5, cursor="hand2",
                      command=save_room).pack(side="right", padx=(5, 0))
            tk.Button(bf, text="Cancel", font=BOLD_BTN_FONT, bg=RED_BTN, fg=WHITE,
                      relief="flat", padx=12, pady=5, cursor="hand2",
                      command=win.destroy).pack(side="right")

        def delete_room():
            selected = self.rooms_tree.selection()
            if not selected:
                messagebox.showwarning("Selection Required", "Please click a Room from the table first."); return
            if rooms_confirm("Delete this Room? This cannot be undone."):
                self.db.delete_room(self.rooms_tree.item(selected[0], "tags")[0])
                self.db.get_all_rooms(self.rooms_tree)
                update_room_count()
                self.refresh_dashboard()

        def edit_room():
            selected = self.rooms_tree.selection()
            if not selected:
                messagebox.showwarning("Selection Required", "Please click a Room from the table first."); return
            add_room_window(prefill=self.rooms_tree.item(selected[0], "values"), edit_item=selected[0])

        def view_room_details():
            selected = self.rooms_tree.selection()
            if not selected:
                messagebox.showwarning("Selection Required", "Please click a Room from the table first."); return
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
                ("Room Number", values[0]), ("Building", values[1]),
                ("Capacity", values[2]), ("Occupants", values[3]),
                ("Status", values[4]), ("Last Cleaned", values[5])
            ]):
                tk.Label(midFrame, text=lbl, bg=WHITE, fg=FG_MUTED, font=("Segoe UI", 9)).grid(row=i, column=0, sticky="w", pady=5)
                tk.Label(midFrame, text=val, bg=WHITE, fg=FG_DARK, font=("Segoe UI", 10, "bold")).grid(row=i, column=1, sticky="w", pady=5, padx=(10, 0))
            bf = tk.Frame(win, bg=content_color)
            bf.pack(fill="x", padx=15, pady=10)
            tk.Button(bf, text="Close", font=UNIFORM_FONT, bg=BLACK, fg=WHITE,
                      relief="flat", padx=12, pady=5, cursor="hand2",
                      command=win.destroy).pack(side="right")

        add_btn.config(command=add_room_window)
        btn_cfg = dict(bg=BLUE, fg=WHITE, font=BOLD_BTN_FONT,
                       relief="solid", bd=0, padx=14, pady=5, cursor="hand2")
        tk.Button(action_bar, text="✏  Edit",         command=edit_room,         **btn_cfg).pack(side="right", padx=4)
        tk.Button(action_bar, text="⊞  View details", command=view_room_details, **btn_cfg).pack(side="right", padx=4)
        tk.Button(action_bar, text="🗑  Delete",
                  bg=RED_BTN, fg=WHITE, font=BOLD_BTN_FONT,
                  relief="solid", bd=0, padx=14, pady=5, cursor="hand2",
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
                     – one row per Room assignment
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
        
        def validate_range(P, max_limit):
            # 1. Allow the user to completely clear the box (blank string)
            if P == "":
                return True
                
            # 2. Check if the typed characters are actually digits
            if P.isdigit():
                # Convert the text to an integer and check the limit
                if int(P) <= int(max_limit):
                    return True
                    
            # Reject anything else (letters, symbols, or numbers too high)
            return False

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
                                                      email_val, contact_val)
                    reload_master()
                    update_detail_header()
                    self.refresh_dashboard()
                    win.destroy()
                except Exception as e:
                    err_lbl.config(text=f"Error: {e}")

            bf = tk.Frame(win, bg=content_color)
            bf.pack(fill="x", padx=15, pady=15)
            tk.Button(bf, text="Save", font=BOLD_BTN_FONT, bg=GREEN_BTN, fg=WHITE,
                      relief="flat", padx=12, pady=5, cursor="hand2",
                      command=save).pack(side="right", padx=(5, 0))
            tk.Button(bf, text="Cancel", font=BOLD_BTN_FONT, bg=RED_BTN, fg=WHITE,
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

            vcmd_range = win.register(validate_range)

            # Building (cols 0-2) / Room (cols 3-5)
            tk.Label(midFrame, text="Building", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).grid(
                row=0, column=0, columnspan=3, sticky="w", pady=(0, 2))
            buildingVar = tk.StringVar()
            bldDrop = ttk.Combobox(midFrame, textvariable=buildingVar,
                                   values=self.db.get_distinct_buildings(),
                                   state="readonly", font=UNIFORM_FONT)
            bldDrop.grid(row=1, column=0, columnspan=3, sticky="we", pady=(0, 12), padx=(0, 6))
            # if self.db.get_distinct_buildings():
            #     bldDrop.current(0)

            tk.Label(midFrame, text="Room", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).grid(
                row=0, column=3, columnspan=3, sticky="w", pady=(0, 2), padx=(6, 0))
            roomVar = tk.StringVar()
            roomDrop = ttk.Combobox(midFrame, textvariable=roomVar, values=[],
                                    state="readonly", font=UNIFORM_FONT)
            roomDrop.grid(row=1, column=3, columnspan=3, sticky="we", pady=(0, 12), padx=(6, 0))

            def on_bld_change(event):
                ROOMS = self.db.get_rooms_by_building(buildingVar.get())
                roomDrop.config(values=ROOMS)
                if ROOMS: roomDrop.current(0)
                else: roomVar.set("")

            bldDrop.bind("<<ComboboxSelected>>", on_bld_change)

            # Date (YYYY-MM-DD) — single field, same style as Assign Room dialog
            tk.Label(midFrame, text="Date (YYYY-MM-DD)", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).grid(
                row=2, column=0, columnspan=6, sticky="w", pady=(0, 2))

            def validate_date_input(P):
                return all(c.isdigit() or c == "-" for c in P)

            vcmd_date = (win.register(validate_date_input), "%P")

            date_entry = tk.Entry(midFrame, bg=WHITE, fg=BLACK, font=UNIFORM_FONT,
                                   relief="flat", bd=0, insertbackground=FG_DARK,
                                   highlightbackground=BORDER, highlightthickness=1,
                                   validate="key", validatecommand=vcmd_date)
            date_entry.grid(row=3, column=0, columnspan=6, sticky="we", pady=(0, 12), ipady=4, padx=2)

            # Time start (cols 0-2) / Time end (cols 3-5)
# ── TIME OPTIONS GENERATION ───────────────────────────────────
            timeOptions = [
                "07:00 AM", "07:30 AM", "08:00 AM", "08:30 AM", "09:00 AM", "09:30 AM",
                "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM", "12:00 PM", "12:30 PM",
                "01:00 PM", "01:30 PM", "02:00 PM", "02:30 PM", "03:00 PM", "03:30 PM",
                "04:00 PM", "04:30 PM", "05:00 PM", "05:30 PM", "06:00 PM", "06:30 PM",
                "07:00 PM", "07:30 PM", "08:00 PM", "08:30 PM", "09:00 PM"
            ]

            # ── TIME START DROPDOWN (Column 0) ────────────────────────────
            timeStartFrame = tk.Frame(midFrame, bg=WHITE)
            timeStartFrame.grid(row=4, column=0, columnspan=3, sticky="we", padx=(0, 6))
                
            tk.Label(timeStartFrame, text="Time Start", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).pack(anchor="w", pady=(0, 2))
                
            timeStartSelection = tk.StringVar()
            timeStartDropdown = ttk.Combobox(timeStartFrame, textvariable=timeStartSelection, 
                                                 values=timeOptions, state="readonly", font=UNIFORM_FONT)
            timeStartDropdown.pack(fill="x", ipady=1)

            # ── TIME END DROPDOWN (Column 3) ──────────────────────────────
            timeEndFrame = tk.Frame(midFrame, bg=WHITE)
            timeEndFrame.grid(row=4, column=3, columnspan=3, sticky="we", padx=(6, 0))
                
            tk.Label(timeEndFrame, text="Time Should End", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).pack(anchor="w", pady=(0, 2))
                
            timeEndSelection = tk.StringVar()
            timeEndDropdown = ttk.Combobox(timeEndFrame, textvariable=timeEndSelection, 
                                               values=[], state="disabled", font=UNIFORM_FONT) # Initialized as disabled and empty
            timeEndDropdown.pack(fill="x", ipady=1)

            err_lbl = tk.Label(win, text="", fg="#c0392b", bg=content_color, font=UNIFORM_FONT)
            err_lbl.pack(pady=(2, 0))


                # ── FILTER AND ENABLE LOGIC ───────────────────────────────────
            def update_end_times(event=None):
                selected_start = timeStartDropdown.get()
                if not selected_start:
                    return
                    
                # Find the index position of the chosen start time in our list
                start_index = timeOptions.index(selected_start)
                    
                # Slice the list to grab only the elements AFTER the start_index
                allowed_end_times = timeOptions[start_index + 1:]
                    
                if allowed_end_times:
                    # Enable the dropdown, load the valid times, and set the first valid option
                    timeEndDropdown.config(state="readonly", values=allowed_end_times)
                    timeEndDropdown.current(0)
                else:
                    # Edge case: if they picked 09:00 PM, there are no valid end times left
                    timeEndDropdown.config(state="disabled", values=["No valid times"])
                    timeEndSelection.set("No valid times")

            # Bind the function to trigger immediately when a start time is chosen
            timeStartDropdown.bind("<<ComboboxSelected>>", update_end_times)

            def confirm_assign():
                Building = buildingVar.get().strip()
                Room     = roomVar.get().strip()
                date_str = date_entry.get().strip()
                t_start  = timeStartSelection.get().strip()
                t_end    = timeEndSelection.get().strip()

                if not Building or not Room:
                    err_lbl.config(text="Please select a Building and Room."); return
                if not date_str:
                    err_lbl.config(text="Please enter a date (YYYY-MM-DD)."); return
                if not t_start or not t_end:
                    err_lbl.config(text="Please select start and end times."); return

                try:
                    parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    err_lbl.config(text="Date must be in YYYY-MM-DD format."); return

                if parsed_date.year < 2026:
                    err_lbl.config(text="Year must be 2026 or later."); return

                Month = str(parsed_date.month)
                Day   = str(parsed_date.day)
                Year  = str(parsed_date.year)

                try:
                    self.db.add_schedule(cs, Building, Room, Month, Day, Year, t_start, t_end)
                    reload_detail()
                    reload_master()      # refresh assignment count
                    self.refresh_dashboard()
                    messagebox.showinfo("Success", "Cleaning assignment added.")
                    win.destroy()
                except Exception as e:
                    err_lbl.config(text=f"Error: {e}")

            bf = tk.Frame(win, bg=content_color)
            bf.pack(fill="x", padx=15, pady=15)
            tk.Button(bf, text="Confirm", font=BOLD_BTN_FONT, bg=GREEN_BTN, fg=WHITE,
                      relief="flat", padx=12, pady=5, cursor="hand2",
                      command=confirm_assign).pack(side="right", padx=(5, 0))
            tk.Button(bf, text="Cancel", font=BOLD_BTN_FONT, bg=RED_BTN, fg=WHITE,
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
        tk.Label(topbar, text="Cleaning Staff", bg=content_color, fg="#000000",
                 font=("Segoe UI", 17, "bold")).pack(side="left")
        tk.Button(topbar, text="+ Add Staff", command=lambda: open_staff_window(),
                  bg=GREEN_BTN, fg=WHITE, font=BOLD_BTN_FONT, relief="solid", bd=0,
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
            if q == "search by ID or name...": q = ""
            for r in self.cleaning_tree.get_children(): self.cleaning_tree.delete(r)
            with sqlite3.connect(DB_NAME) as con:
                cur = con.cursor()
                cur.execute("""
                    SELECT cs.StaffID, cs.FirstName || ' ' || cs.LastName AS FullName, cs.Contact, cs.Email,
                           COUNT(sch.CleaningSchedID)
                    FROM CLEANING_STAFF cs
                    LEFT JOIN CLEANING_SCHEDULE sch ON cs.StaffID = sch.StaffID
                    WHERE LOWER(cs.StaffID) LIKE ? OR LOWER(cs.FirstName || ' ' || cs.LastName) LIKE ?
                    GROUP BY cs.StaffID
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
            style.configure(f"{sname}.Treeview", background=WHITE, foreground="#000000",
                            rowheight=34, fieldbackground=WHITE, borderwidth=0, font=UNIFORM_FONT)
            style.configure(f"{sname}.Treeview.Heading", background=HEADER_BG, foreground="#000000",
                            font=("Segoe UI", 9, "bold"), relief="flat", padding=(8, 6))
            style.map(f"{sname}.Treeview",
                      background=[("selected", ROW_SEL)],
                      foreground=[("selected", "#000000")])
            style.layout(f"{sname}.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

        master_tf = tk.Frame(master_card, bg=WHITE)
        master_tf.pack(fill="x", padx=16, pady=(0, 4))

        self.cleaning_tree = ttk.Treeview(
            master_tf,
            columns=("cs_id", "name", "Contact", "Email", "assignments"),
            show="headings",
            style="CS.Master.Treeview",
            selectmode="browse",
            height=5
        )
        for cid, heading, width, anchor in [
            ("cs_id",       "Staff ID",    90,  "w"),
            ("name",        "Name",       200,  "w"),
            ("Contact",     "Contact",    120,  "w"),
            ("Email",       "Email",      180,  "w"),
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

        btn_cfg = dict(bg=BLUE, fg=WHITE, font=BOLD_BTN_FONT,
                       relief="solid", bd=0, padx=12, pady=4, cursor="hand2")
        tk.Button(master_action, text="✏  Edit Staff",
                  command=edit_staff, **btn_cfg).pack(side="right", padx=4)
        tk.Button(master_action, text="🗑  Delete Staff",
                  bg=RED_BTN, fg=WHITE, font=BOLD_BTN_FONT,
                  relief="solid", bd=0, padx=12, pady=4, cursor="hand2",
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

        tk.Button(detail_hdr, text="+ Assign Cleaning",
                  command=open_assign_window,
                  bg=GREEN_BTN, fg=WHITE, font=BOLD_BTN_FONT,
                  relief="flat", padx=12, pady=4, cursor="hand2").pack(side="right")

        tk.Frame(detail_card, bg=BORDER, height=1).pack(fill="x", padx=16)

        # detail treeview
        detail_tf = tk.Frame(detail_card, bg=WHITE)
        detail_tf.pack(fill="both", expand=True, padx=16, pady=(4, 0))

        self.schedule_tree = ttk.Treeview(
            detail_tf,
            columns=("#", "Building", "Room", "date", "TimeStart", "TimeEnd"),
            show="headings",
            style="CS.Detail.Treeview",
            selectmode="browse",
            height=6   
        )
        for cid, heading, width, anchor in [
            ("#",          "#",          40,  "center"),
            ("Building",   "Building",   90,  "center"),
            ("Room",       "Room",       80,  "center"),
            ("date",       "Date",      110,  "center"),
            ("TimeStart", "Time Start", 110, "center"),
            ("TimeEnd",   "Time End",   110, "center"),
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
                  bg=RED_BTN, fg=WHITE, font=BOLD_BTN_FONT,
                  relief="solid", bd=0, padx=12, pady=4, cursor="hand2",
                  command=remove_schedule).pack(side="right", padx=4)

        # ── initial load ──────────────────────────────────────────────
        reload_master()

    # ── Settings page ─────────────────────────────────────────────────
    
if __name__ == "__main__":
    app = main()
    app.mainloop()
