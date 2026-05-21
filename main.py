import tkinter as tk
import tkinter.ttk as ttk
from tkinter import *

UNIFORM_FONT = ("Segoe UI", 10)

WHITE      = "#ffffff"
BLACK      = "#000000"
HEADER_BG  = "#eae8f0"
ROW_ALT    = "#f7f6fb"
ROW_SEL    = "#dcd8f0"
BORDER     = "#dde0ee"
FG_DARK    = "#1a1a2e"
FG_MUTED   = "#9aa3c2"

font_color_sidebar = "white"
sidebar_color = "#8A5F41"
active_color = "#A77F60"
content_color = "#F3E4C9"
black = "#070707"

def main(login_root=None):
    if login_root:
        login_root.withdraw()
    root = tk.Tk()
    root.geometry("1200x650")
    root.minsize(1150, 650)
    root.title("Dormi Admin Panel")
    
    # ── Page content functions ──────────────────────────────
    def build_dashboard_page(page):
        tk.Label(page, text="Dashboard", bg=content_color, fg="black",
                 font=("Arial", 16, "bold")).pack(anchor="w", pady=20, padx=20)
    
        # --- Cards row container ---
        cards_frame = tk.Frame(page, bg=content_color)
        cards_frame.pack(fill="x", padx=30, pady=10)
    
        totalstudents_Lframe = tk.LabelFrame(cards_frame, width=200, height=150, bg="white")
        totalstudents_Lframe.pack(side="left", padx=(0, 10), fill="x", expand=True)
        totalstudents_Lframe.pack_propagate(False)

        tk.Label(totalstudents_Lframe, text="🧑", font=("Arial", 24), bg="white", fg="brown").pack(anchor="w", padx=10, pady=5)
        tsNum = tk.Label(totalstudents_Lframe, text="0", font=("Arial", 24, "bold"), bg="white", fg="black")
        tsNum.pack(anchor="w", padx=10, pady=5)
        tk.Label(totalstudents_Lframe, text="Total students", font=("Arial", 15), bg="white", fg="black").pack(anchor="w", padx=10, pady=(5, 0))
    
        totalrooms_Lframe = tk.LabelFrame(cards_frame, width=200, height=150, bg="white")
        totalrooms_Lframe.pack(side="left", padx=10, fill="x", expand=True)
        totalrooms_Lframe.pack_propagate(False)

        tk.Label(totalrooms_Lframe, text="🛏️", font=("Arial", 24), bg="white", fg="Green").pack(anchor="w", padx=10, pady=5)
        trNum = tk.Label(totalrooms_Lframe, text="0", font=("Arial", 24, "bold"), bg="white", fg="black")
        trNum.pack(anchor="w", padx=10, pady=5)
        tk.Label(totalrooms_Lframe, text="Total rooms", font=("Arial", 15), bg="white", fg="black").pack(anchor="w", padx=10, pady=(5, 0))
    
        totalroomsoccupied_Lframe = tk.LabelFrame(cards_frame, width=200, height=150, bg="white")
        totalroomsoccupied_Lframe.pack(side="left", padx=10, fill="x", expand=True)
        totalroomsoccupied_Lframe.pack_propagate(False)

        tk.Label(totalroomsoccupied_Lframe, text="🛏️", font=("Arial", 24), bg="white", fg="violet").pack(anchor="w", padx=10, pady=5)
        troNum = tk.Label(totalroomsoccupied_Lframe, text="0", font=("Arial", 24, "bold"), bg="white", fg="black")
        troNum.pack(anchor="w", padx=10, pady=5)
        tk.Label(totalroomsoccupied_Lframe, text="Rooms occupied", font=("Arial", 15), bg="white", fg="black").pack(anchor="w", padx=10, pady=(5, 0))
    
        totalcleaning_Lframe = tk.LabelFrame(cards_frame, width=200, height=150, bg="white")
        totalcleaning_Lframe.pack(side="left", padx=(10, 0), fill="x", expand=True)
        totalcleaning_Lframe.pack_propagate(False)

        tk.Label(totalcleaning_Lframe, text="🧹", font=("Arial", 24), bg="white", fg="brown").pack(anchor="w", padx=10, pady=5)
        tcNum = tk.Label(totalcleaning_Lframe, text="0", font=("Arial", 24, "bold"), bg="white", fg="black")
        tcNum.pack(anchor="w", padx=10, pady=5)
        tk.Label(totalcleaning_Lframe, text="Cleaning tasks", font=("Arial", 15), bg="white", fg="black").pack(anchor="w", padx=10, pady=(5, 0))
    
        #start of Treeview for student assignments and cleaning assignments    
    
        tk.Label(page, text="Recent student assignments", bg=content_color, font=("Arial", 12, "bold"), fg="black").pack(anchor="w", pady=5, padx=30)
    
        treeStuAss = ttk.Treeview(page, columns=("Student", "Room", "Start Date", "Status"), show="headings")
    
        treeStuAss.heading("Student", text="Student Name")
        treeStuAss.heading("Room",   text="Room")
        treeStuAss.heading("Start Date", text="Start Date")
        treeStuAss.heading("Status", text="Status")
    
        treeStuAss.column("Student",width=150)
        treeStuAss.column("Room",width=50)
        treeStuAss.column("Start Date",width=75)
        treeStuAss.column("Status", width=75)
    
        treeStuAss.pack(fill="both",padx=(20, 20), pady=10)
    
        tk.Label(page, text="Cleaning assignments today", bg=content_color,font=("Arial", 12, "bold"), fg="black").pack(anchor="w", pady=5, padx=30)
    
        treeCleanAss = ttk.Treeview(page, columns=("ID", "StaffName", "Room", "TimeStart", "TimeEnd"), show="headings")
    
        treeCleanAss.heading("ID", text="ID")
        treeCleanAss.heading("StaffName", text="Staff Name")
        treeCleanAss.heading("Room", text="Room")
        treeCleanAss.heading("TimeStart", text="Time Start")
        treeCleanAss.heading("TimeEnd", text="Time End")
      
        treeCleanAss.column("ID",width=50)
        treeCleanAss.column("StaffName",width=150)
        treeCleanAss.column("Room",width=50)
        treeCleanAss.column("TimeStart",width=75)
        treeCleanAss.column("TimeEnd", width=75)
    
        treeCleanAss.pack(fill="both",padx=(20,20), pady=10)
    
    def build_students_page(page):

        # ── Add Student window ────────────────────────────────
        def add_student_window():
            win = Toplevel()
            win.title("Add Student")
            win.config(bg=content_color)
            win.geometry("440x420")
            win.resizable(False, False)

            titleFrame = tk.Frame(win, bg=content_color)
            titleFrame.pack(fill="x", padx=15, pady=12)
            tk.Label(titleFrame, text="Add Student", bg=content_color, fg=FG_DARK,
                     font=("Segoe UI", 15, "bold")).pack(side="left")

            formCard = tk.Frame(win, bg=WHITE, padx=15, pady=15,
                                bd=1, relief="solid", highlightbackground=BORDER)
            formCard.pack(fill="both", expand=True, padx=15, pady=5)
            formCard.columnconfigure(0, weight=1)
            formCard.columnconfigure(1, weight=1)

            def make_entry(parent, label, row, col, colspan=1):
                tk.Label(parent, text=label, bg=WHITE, fg=FG_DARK,
                         font=UNIFORM_FONT).grid(row=row, column=col, columnspan=colspan,
                                                  sticky="w", pady=(0, 2))
                border = tk.Frame(parent, bg=WHITE,
                                  highlightbackground=BORDER, highlightthickness=1)
                border.grid(row=row + 1, column=col, columnspan=colspan,
                            sticky="we", pady=(0, 12),
                            padx=(0, 8) if colspan == 1 and col == 0 else (8, 0) if col == 1 else 0)
                entry = tk.Entry(border, bg=WHITE, fg=BLACK, font=UNIFORM_FONT,
                                 relief="flat", bd=0, insertbackground=FG_DARK)
                entry.pack(fill="x", padx=5, pady=3)
                return entry

            def make_combo(parent, label, row, col, options, colspan=1):
                tk.Label(parent, text=label, bg=WHITE, fg=FG_DARK,
                         font=UNIFORM_FONT).grid(row=row, column=col, columnspan=colspan,
                                                  sticky="w", pady=(0, 2))
                var = tk.StringVar()
                combo = ttk.Combobox(parent, textvariable=var, values=options,
                                     state="readonly", font=UNIFORM_FONT)
                combo.grid(row=row + 1, column=col, columnspan=colspan,
                           sticky="we", pady=(0, 12),
                           padx=(0, 8) if col == 0 and colspan == 1 else (8, 0) if col == 1 else 0)
                combo.current(0)
                return var

            studentno_entry = make_entry(formCard, "Student No.", row=0, col=0, colspan=2)
            name_entry      = make_entry(formCard, "Full Name",   row=2, col=0, colspan=2)
            program_var     = make_combo(formCard, "Program",     row=4, col=0,
                                         options=["BSIT", "BSCS", "BSN", "BSED", "BSBA"])
            status_var      = make_combo(formCard, "Status",      row=4, col=1,
                                         options=["Active", "Upcoming", "No room"])
            room_entry      = make_entry(formCard, "Room",        row=6, col=0)
            contact_entry   = make_entry(formCard, "Contact",     row=6, col=1)

            bottomFrame = tk.Frame(win, bg=content_color)
            bottomFrame.pack(fill="x", padx=15, pady=12)

            def save_student():
                values = (
                    studentno_entry.get(),
                    name_entry.get(),
                    program_var.get(),
                    room_entry.get(),
                    status_var.get(),
                    contact_entry.get(),
                )
                tree.insert("", "end", values=values)
                win.destroy()

            cancelBtn = tk.Button(bottomFrame, text="Cancel", fg="#c0392b", font=UNIFORM_FONT)
            cancelBtn.pack(side="right", padx=(5, 0))
            saveBtn = tk.Button(bottomFrame, text="Save Student", font=UNIFORM_FONT,
                                command=save_student)
            saveBtn.pack(side="right")

        # ── Top bar ─────────────────────────────────────────
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
    
        # ── Card ────────────────────────────────────────────
        card = tk.Frame(page, bg=WHITE,
                        highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="both", expand=True, padx=28, pady=(0, 20))
    
        # ── Search bar ──────────────────────────────────────
        search_wrap = tk.Frame(card, bg=WHITE,
                               highlightbackground=BORDER, highlightthickness=1)
        search_wrap.pack(fill="x", padx=16, pady=(14, 10))
    
        tk.Label(search_wrap, text="🔍", bg=WHITE, fg=FG_MUTED,
                 font=UNIFORM_FONT).pack(side="left", padx=(8, 2), pady=6)
    
        search_entry = tk.Entry(search_wrap, bg=WHITE, fg=FG_MUTED,
                                font=UNIFORM_FONT, relief="flat", bd=0,
                                insertbackground=FG_DARK)
        search_entry.insert(0, "Search by name or student number...")
        search_entry.pack(side="left", fill="x", expand=True, pady=7, padx=4)
    
        # ── Treeview style ───────────────────────────────────
        style = ttk.Style()
        style.theme_use("clam")
    
        style.configure("Students.Treeview",
                        background=WHITE,
                        foreground=FG_DARK,
                        rowheight=36,
                        fieldbackground=WHITE,
                        borderwidth=0,
                        font=UNIFORM_FONT)
    
        style.configure("Students.Treeview.Heading",
                        background=HEADER_BG,
                        foreground="#555577",
                        font=("Segoe UI", 9, "bold"),
                        relief="flat",
                        padding=(8, 6))
    
        style.map("Students.Treeview",
                  background=[("selected", ROW_SEL)],
                  foreground=[("selected", FG_DARK)])
    
        style.layout("Students.Treeview", [
            ("Treeview.treearea", {"sticky": "nswe"})
        ])
    
        # ── Treeview ─────────────────────────────────────────
        columns = ("student_no", "name", "program", "room", "status", "contact")
    
        tree_frame = tk.Frame(card, bg=WHITE)
        tree_frame.pack(fill="both", expand=True, padx=16)
    
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
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
            tree.heading(cid, text=heading, anchor=anchor)
            tree.column(cid,  width=width,  anchor=anchor, stretch=True)
    
    
    
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)
    
        # ── Separator ────────────────────────────────────────
        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=16, pady=(6, 0))
    
        # ── Action bar ───────────────────────────────────────
        action_bar = tk.Frame(card, bg=WHITE)
        action_bar.pack(fill="x", padx=16, pady=10)
    
        tk.Label(action_bar, text="5 students", bg=WHITE, fg=FG_MUTED,
                 font=UNIFORM_FONT).pack(side="left", padx=(4, 0))
    
        btn_cfg = dict(bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT,
                       relief="solid", bd=1, padx=14, pady=5, cursor="hand2")
    
        tk.Button(action_bar, text="✏  Edit",         **btn_cfg).pack(side="right", padx=4)
        tk.Button(action_bar, text="⊞  Assign room",  **btn_cfg).pack(side="right", padx=4)
        tk.Button(action_bar, text="🗑  Delete",
                  bg=WHITE, fg="#c0392b", font=UNIFORM_FONT,
                  relief="solid", bd=1, padx=14, pady=5,
                  cursor="hand2").pack(side="right", padx=4)
    
        # ── Hint ─────────────────────────────────────────────
        tk.Label(card,
                 text="ⓘ  Click a row to select before editing, assigning, or deleting.",
                 bg=WHITE, fg=FG_MUTED, font=("Segoe UI", 8),
                 anchor="w").pack(fill="x", padx=20, pady=(0, 10))
    
    
    def build_students_page(page):

        # ── Add Student window ───────────────────────────────
        def add_student_window(prefill=None, edit_item=None):
            win = Toplevel()
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

            # Student No & Name
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

            # Pre-fill if editing
            if prefill:
                e_no.insert(0, prefill[0])
                e_name.insert(0, prefill[1])
                e_program.insert(0, prefill[2])
                e_room.insert(0, prefill[3])
                statusVar.set(prefill[4])
                e_contact.insert(0, prefill[5])

            # Error label
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
                    tree.item(edit_item, values=(no, name, program, room, status, contact))
                else:
                    tree.insert("", "end", values=(no, name, program, room, status, contact))

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

        # ── Delete selected ──────────────────────────────────
        def delete_student():
            selected = tree.selection()
            if not selected:
                messagebox("Select a student first.", "No Selection")
                return
            if messagebox_confirm("Delete this student? This cannot be undone."):
                tree.delete(selected[0])
                update_count()

        # ── Edit selected ────────────────────────────────────
        def edit_student():
            selected = tree.selection()
            if not selected:
                messagebox("Select a student first.", "No Selection")
                return
            values = tree.item(selected[0], "values")
            add_student_window(prefill=values, edit_item=selected[0])

        # ── Assign Room window ───────────────────────────────
        def assign_room():
            selected = tree.selection()
            if not selected:
                messagebox("Select a student first.", "No Selection")
                return
            values = tree.item(selected[0], "values")

            win = Toplevel()
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
                tree.item(selected[0], values=new_vals)
                win.destroy()

            bottomFrame = tk.Frame(win, bg=content_color)
            bottomFrame.pack(fill="x", padx=15, pady=10)
            tk.Button(bottomFrame, text="Assign", font=UNIFORM_FONT,
                      bg=BLACK, fg=WHITE, relief="flat", padx=12, pady=5,
                      cursor="hand2", command=save_room).pack(side="right", padx=(5,0))
            tk.Button(bottomFrame, text="Cancel", font=UNIFORM_FONT,
                      fg="#c0392b", relief="flat", padx=12, pady=5,
                      cursor="hand2", command=win.destroy).pack(side="right")

        # ── Simple helpers ───────────────────────────────────
        def messagebox(msg, title="Info"):
            win = Toplevel()
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
            win = Toplevel()
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

        def update_count():
            count = len(tree.get_children())
            count_label.config(text=f"{count} student{'s' if count != 1 else ''}")

        # ── Top bar ──────────────────────────────────────────
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

        # ── Card ─────────────────────────────────────────────
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

        tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
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
            tree.heading(cid, text=heading, anchor=anchor)
            tree.column(cid,  width=width,  anchor=anchor, stretch=True)

        # Sample data — remove when DB is connected
        sample_students = [
            ("2021-0001", "Juan dela Cruz",   "BSCS",   "101", "Active",   "09171234567"),
            ("2021-0002", "Maria Santos",     "BSIT",   "102", "Active",   "09181234567"),
            ("2021-0003", "Jose Reyes",       "BSECE",  "103", "On Leave", "09191234567"),
            ("2021-0004", "Ana Garcia",       "BSCS",   "104", "Active",   "09201234567"),
            ("2021-0005", "Pedro Villanueva", "BSIT",   "",    "Inactive", "09211234567"),
        ]
        for row in sample_students:
            tree.insert("", "end", values=row)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)

        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=16, pady=(6, 0))

        action_bar = tk.Frame(card, bg=WHITE)
        action_bar.pack(fill="x", padx=16, pady=10)

        count_label = tk.Label(action_bar, text="5 students", bg=WHITE, fg=FG_MUTED,
                               font=UNIFORM_FONT)
        count_label.pack(side="left", padx=(4, 0))

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

    def build_rooms_page(page):

        def add_room_window():
            win = Toplevel()
            win.title("Add Room")
            win.config(bg=content_color)
            win.geometry("420x340")
            win.resizable(False, False)

            upperFrame = tk.Frame(win, bg=content_color)
            upperFrame.pack(fill="x", padx=15, pady=12)
            tk.Label(upperFrame, text="Add Room", bg=content_color, fg=FG_DARK,
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

            bottomFrame = tk.Frame(win, bg=content_color)
            bottomFrame.pack(fill="x", padx=15, pady=15)
            tk.Button(bottomFrame, text="Save Room", font=UNIFORM_FONT,
                      bg=BLACK, fg=WHITE, relief="flat", padx=12, pady=5,
                      cursor="hand2").pack(side="right", padx=(5, 0))
            tk.Button(bottomFrame, text="Cancel", font=UNIFORM_FONT,
                      fg="#c0392b", relief="flat", padx=12, pady=5,
                      cursor="hand2", command=win.destroy).pack(side="right")

        # ── Top bar ─────────────────────────────────────────
        topbar = tk.Frame(page, bg=content_color)
        topbar.pack(fill="x", padx=28, pady=(20, 12))

        tk.Label(topbar, text="Rooms", bg=content_color, fg=FG_DARK,
                 font=("Segoe UI", 17, "bold")).pack(side="left")
        tk.Button(topbar, text="+ Add room", bg=WHITE, fg=FG_DARK,
                  font=UNIFORM_FONT, relief="solid", bd=1,
                  padx=12, pady=5, cursor="hand2",
                  command=add_room_window).pack(side="right")

        # ── Card ────────────────────────────────────────────
        card = tk.Frame(page, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="both", expand=True, padx=28, pady=(0, 20))

        # ── Search bar ──────────────────────────────────────
        search_wrap = tk.Frame(card, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        search_wrap.pack(fill="x", padx=16, pady=(14, 10))
        tk.Label(search_wrap, text="🔍", bg=WHITE, fg=FG_MUTED,
                 font=UNIFORM_FONT).pack(side="left", padx=(8, 2), pady=6)
        search_entry = tk.Entry(search_wrap, bg=WHITE, fg=FG_MUTED,
                                font=UNIFORM_FONT, relief="flat", bd=0,
                                insertbackground=FG_DARK)
        search_entry.insert(0, "Search by room number or type...")
        search_entry.pack(side="left", fill="x", expand=True, pady=7, padx=4)

        # ── Filter buttons ───────────────────────────────────
        filter_frame = tk.Frame(card, bg=WHITE)
        filter_frame.pack(fill="x", padx=16, pady=(0, 8))
        tk.Label(filter_frame, text="Filter:", bg=WHITE, fg=FG_MUTED,
                 font=("Segoe UI", 9)).pack(side="left", padx=(0, 6))
        for label, color in [("All", FG_DARK), ("Vacant", "#27ae60"),
                              ("Occupied", "#8e44ad"), ("Maintenance", "#e67e22")]:
            tk.Button(filter_frame, text=label, bg=WHITE, fg=color,
                      font=("Segoe UI", 8), relief="solid", bd=1,
                      padx=10, pady=3, cursor="hand2").pack(side="left", padx=3)

        # ── Treeview style ───────────────────────────────────
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

        # ── Treeview ─────────────────────────────────────────
        columns = ("room_no", "type", "capacity", "occupants", "status", "last_cleaned")
        tree_frame = tk.Frame(card, bg=WHITE)
        tree_frame.pack(fill="both", expand=True, padx=16)

        tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
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
            tree.heading(cid, text=heading, anchor=anchor)
            tree.column(cid, width=width, anchor=anchor, stretch=True)

        sample_rooms = [
            ("101", "Single", "1", "1", "Occupied",    "May 20, 2025"),
            ("102", "Double", "2", "0", "Vacant",       "May 19, 2025"),
            ("103", "Triple", "3", "3", "Occupied",    "May 18, 2025"),
            ("104", "Single", "1", "0", "Maintenance", "May 15, 2025"),
            ("105", "Suite",  "4", "2", "Occupied",    "May 20, 2025"),
            ("106", "Double", "2", "0", "Vacant",       "May 17, 2025"),
        ]
        for row in sample_rooms:
            tree.insert("", "end", values=row)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)

        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=16, pady=(6, 0))

        action_bar = tk.Frame(card, bg=WHITE)
        action_bar.pack(fill="x", padx=16, pady=10)
        tk.Label(action_bar, text="6 rooms total", bg=WHITE, fg=FG_MUTED,
                 font=UNIFORM_FONT).pack(side="left", padx=(4, 0))

        btn_cfg = dict(bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT,
                       relief="solid", bd=1, padx=14, pady=5, cursor="hand2")
        tk.Button(action_bar, text="✏  Edit",         **btn_cfg).pack(side="right", padx=4)
        tk.Button(action_bar, text="⊞  View details", **btn_cfg).pack(side="right", padx=4)
        tk.Button(action_bar, text="🗑  Delete",
                  bg=WHITE, fg="#c0392b", font=UNIFORM_FONT,
                  relief="solid", bd=1, padx=14, pady=5,
                  cursor="hand2").pack(side="right", padx=4)

        tk.Label(card, text="ⓘ  Click a row to select before editing, viewing details, or deleting.",
                 bg=WHITE, fg=FG_MUTED, font=("Segoe UI", 8),
                 anchor="w").pack(fill="x", padx=20, pady=(0, 10))
    
    # Cleaning Staff
    def addCleaningStaff():
        addStaff = Toplevel()
        addStaff.title("Add Cleaning Staff")
        addStaff.config(bg=content_color)
        addStaff.geometry("500x360") 
        addStaff.resizable(False, False) 

        # Upper Frame
        upperFrame = tk.Frame(addStaff, bg=content_color)
        upperFrame.pack(fill="x", padx=15, pady=12)
        
        tk.Label(upperFrame, text="Add Cleaning Staff", bg=content_color, fg=FG_DARK, 
                font=("Segoe UI", 15, "bold")).pack(side="left")

        # Mid Frame
        midFrame = tk.Frame(addStaff, bg=WHITE, padx=15, pady=15, bd=1, relief="solid", highlightbackground=BORDER)
        midFrame.pack(fill="x", padx=15, pady=5)

        midFrame.columnconfigure(0, weight=2)  
        midFrame.columnconfigure(1, weight=2)  
        midFrame.columnconfigure(2, weight=0)  

        # ROW 1: Cleaning Staff ID 
        tk.Label(midFrame, text="Cleaning Staff ID", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 2))
        
        idFrame = tk.Frame(midFrame, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        idFrame.grid(row=1, column=0, columnspan=3, sticky="we", pady=(0, 15))
        
        idEntry = tk.Entry(idFrame, bg=WHITE, fg=BLACK, font=UNIFORM_FONT, relief="flat", bd=0, insertbackground=FG_DARK)
        idEntry.pack(fill="x", padx=5, pady=4)

        # ROW 2: Names
        lnGroup = tk.Frame(midFrame, bg=WHITE)
        lnGroup.grid(row=2, column=0, sticky="we", padx=(0, 6), pady=(0, 15))
        tk.Label(lnGroup, text="Last Name", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).pack(anchor="w", pady=(0, 2))
        lnBorder = tk.Frame(lnGroup, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        lnBorder.pack(fill="x")
        LN_Entry = tk.Entry(lnBorder, bg=WHITE, fg=BLACK, font=UNIFORM_FONT, relief="flat", bd=0, insertbackground=FG_DARK)
        LN_Entry.pack(fill="x", padx=5, pady=4)

        # First Name (Middle)
        fnGroup = tk.Frame(midFrame, bg=WHITE)
        fnGroup.grid(row=2, column=1, sticky="we", padx=6, pady=(0, 15))

        tk.Label(fnGroup, text="First Name", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).pack(anchor="w", pady=(0, 2))
        fnBorder = tk.Frame(fnGroup, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        fnBorder.pack(fill="x")

        FN_Entry = tk.Entry(fnBorder, bg=WHITE, fg=BLACK, font=UNIFORM_FONT, relief="flat", bd=0, insertbackground=FG_DARK)
        FN_Entry.pack(fill="x", padx=5, pady=4)

        #Middle Name
        miGroup = tk.Frame(midFrame, bg=WHITE)
        miGroup.grid(row=2, column=2, sticky="w", padx=(6, 0), pady=(0, 15))

        tk.Label(miGroup, text="M.I.", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).pack(anchor="w", pady=(0, 2))
        miBorder = tk.Frame(miGroup, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        miBorder.pack()

        MI_Entry = tk.Entry(miBorder, bg=WHITE, fg=BLACK, font=UNIFORM_FONT, relief="flat", bd=0, insertbackground=FG_DARK, width=3)
        MI_Entry.pack(padx=5, pady=4)

        # ROW 3: Email
        tk.Label(midFrame, text="Email", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).grid(row=3, column=0, columnspan=3, sticky="w", pady=(0, 2))
        
        emailFrame = tk.Frame(midFrame, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        emailFrame.grid(row=4, column=0, columnspan=3, sticky="we", pady=(0, 5))
        
        emailEntry = tk.Entry(emailFrame, bg=WHITE, fg=BLACK, font=UNIFORM_FONT, relief="flat", bd=0, insertbackground=FG_DARK)
        emailEntry.pack(fill="x", padx=5, pady=4)

        # Bottom Frame (Buttons)
        bottomFrame = tk.Frame(addStaff, bg=content_color)
        bottomFrame.pack(fill="x", padx=15, pady=15)

        saveStaffBtn = tk.Button(bottomFrame, text="Add Staff", font=UNIFORM_FONT)
        saveStaffBtn.pack(side="right", padx=(5, 0))

        cancelBtn = tk.Button(bottomFrame, text="Cancel", fg="#c0392b", font=UNIFORM_FONT)
        cancelBtn.pack(side="right")

        addStaff.mainloop()

    def CSassign_window():
        assign = Toplevel()
        assign.title("Assign Cleaning")
        assign.config(bg=content_color)
        assign.geometry("420x360")
        assign.resizable(False, False) 

        upperFrame = tk.Frame(assign, bg=content_color)
        upperFrame.pack(fill="x", padx=15, pady=12)
        
        tk.Label(upperFrame, text="Assign Cleaning", bg=content_color, fg=FG_DARK, 
                font=("Segoe UI", 15, "bold")).pack(side="left")

        midFrame = tk.Frame(assign, bg=WHITE, padx=15, pady=15, bd=1, relief="solid", highlightbackground=BORDER)
        midFrame.pack(fill="both", expand=True, padx=15, pady=5)

        midFrame.columnconfigure(0, weight=1)
        midFrame.columnconfigure(1, weight=1)

        tk.Label(midFrame, text="Room", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 2))
        
        roomSelection = tk.StringVar()
        roomOptions = ["Option 1", "Option 2", "Option 3"]
        roomDropdown = ttk.Combobox(midFrame, textvariable=roomSelection, values=roomOptions,
                                    state="readonly", font=UNIFORM_FONT)

        roomDropdown.grid(row=1, column=0, columnspan=2, sticky="we", pady=(0, 12))
        roomDropdown.current(0)

        tk.Label(midFrame, text="Date", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 2))
        
        searchFrame = tk.Frame(midFrame, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        searchFrame.grid(row=3, column=0, columnspan=2, sticky="we", pady=(0, 12))
        
        dateEntry = tk.Entry(searchFrame, bg=WHITE, fg=BLACK, font=UNIFORM_FONT, relief="flat", bd=0, insertbackground=FG_DARK)
        dateEntry.pack(fill="x", padx=5, pady=3)

        timeStartFrame = tk.Frame(midFrame, bg=WHITE)
        timeStartFrame.grid(row=4, column=0, sticky="we", padx=(0, 8))
        
        tk.Label(timeStartFrame, text="Time Start", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).pack(anchor="w", pady=(0, 2))
        tStartBorder = tk.Frame(timeStartFrame, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        tStartBorder.pack(fill="x")
        timeStartEntry = tk.Entry(tStartBorder, bg=WHITE, fg=BLACK, font=UNIFORM_FONT, relief="flat", bd=0)
        timeStartEntry.pack(fill="x", padx=5, pady=3)

        timeEndFrame = tk.Frame(midFrame, bg=WHITE)
        timeEndFrame.grid(row=4, column=1, sticky="we", padx=(8, 0))
        
        tk.Label(timeEndFrame, text="Time End", bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT).pack(anchor="w", pady=(0, 2))
        tEndBorder = tk.Frame(timeEndFrame, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        tEndBorder.pack(fill="x")
        timeEndEntry = tk.Entry(tEndBorder, bg=WHITE, fg=BLACK, font=UNIFORM_FONT, relief="flat", bd=0)
        timeEndEntry.pack(fill="x", padx=5, pady=3)

        bottomFrame = tk.Frame(assign, bg=content_color)
        bottomFrame.pack(fill="x", padx=15, pady=15)

        saveSchedBtn = tk.Button(bottomFrame, text="Save Schedule", font=UNIFORM_FONT)
        saveSchedBtn.pack(side="right", padx=(5, 0))

        cancelBtn = tk.Button(bottomFrame, text="Cancel",fg="#c0392b", font=UNIFORM_FONT)
        cancelBtn.pack(side="right")


    def build_cleaning_page(page):
        #Label
        upperFrame = tk.Frame(page, bg=content_color)
        cleaningStaffLabel = tk.Label(upperFrame, text="Cleaning Staff",bg=content_color, fg=FG_DARK,
            font=("Segoe UI", 17, "bold")).pack(side="left")
        addStaffBtn = tk.Button(upperFrame, text="+ Add Staff", command=addCleaningStaff, bg=WHITE, fg=FG_DARK,
                font=UNIFORM_FONT, relief="solid", bd=1,
                padx=12, pady=5, cursor="hand2").pack(side="right")
        
        card = tk.Frame(page, bg=WHITE,
                        highlightbackground=BORDER, highlightthickness=1)

        #Search
        searchFrame =tk.Frame(card, bg="white", highlightbackground=BORDER, highlightthickness=1)
        searchLabel = tk.Label(searchFrame, text="🔍", bg=WHITE, fg=FG_MUTED,
                    font=UNIFORM_FONT).pack(side="left", padx=(8, 2), pady=6)
        CSsearchEntry = tk.Entry(searchFrame,  bg=WHITE, fg=BLACK,
                                font=UNIFORM_FONT, relief="flat", bd=0,
                                insertbackground=FG_DARK)
        CSsearchEntry.pack(side="left", fill="x", expand=True, pady=7, padx=4)

        style = ttk.Style()
        style.theme_use("clam")

        style.configure("CleaningStaff.Treeview",
                        background=WHITE,
                        foreground=FG_DARK,
                        rowheight=36,
                        fieldbackground=WHITE,
                        borderwidth=0,
                        font=UNIFORM_FONT)

        style.configure("CleaningStaff.Treeview.Heading",
                        background=HEADER_BG,
                        foreground="#555577",
                        font=("Segoe UI", 9, "bold"),
                        relief="flat",
                        padding=(8, 6))

        style.map("CleaningStaff.Treeview",
                background=[("selected", ROW_SEL)],
                foreground=[("selected", FG_DARK)])

        style.layout("CleaningStaff.Treeview", [
            ("Treeview.treearea", {"sticky": "nswe"})
        ])

        #Table
        tree_frame = tk.Frame(card, bg=WHITE)
        tree = ttk.Treeview(tree_frame, columns=("CS_ID", "CS_NAME", "CS_CONTACT", "CS_EMAIL"), show="headings")
        tree.heading("CS_ID", text="Staff ID")
        tree.heading("CS_NAME", text="Name")
        tree.heading("CS_CONTACT", text="Contact")
        tree.heading("CS_EMAIL", text="Email")
            
        tree.column("CS_ID", width=80)
        tree.column("CS_NAME", width=200)
        tree.column("CS_CONTACT", width=300)
        tree.column("CS_EMAIL", width=300)

        #tree.bind("<ButtonRelease-1>", select_record)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)


        #Separator
        seperator = tk.Frame(card, bg=BORDER, height=1)

        btnFrame = tk.Frame(card, bg=WHITE)
        #Label at the button, to be unlocked later when its functional
        # CScountRecord = tk.Label(cleaning_page, text=$"{CSrecordCount} staff records , 
        #                bg=WHITE, fg=FG_MUTED, font=UNIFORM_FONT).pack(side="left", padx=(4, 0))")

        btn_cfg = dict(bg=WHITE, fg=FG_DARK, font=UNIFORM_FONT,
                    relief="solid", bd=1, padx=14, pady=5, cursor="hand2")

        tk.Button(btnFrame, text="✏  Edit",         **btn_cfg).pack(side="right", padx=4)
        tk.Button(btnFrame, text="⊞  Assign Cleaning",command=CSassign_window,  **btn_cfg).pack(side="right", padx=4)
        tk.Button(btnFrame, text="🗑  Delete",
                  bg=WHITE, fg="#c0392b", font=UNIFORM_FONT,
                  relief="solid", bd=1, padx=14, pady=5,
                  cursor="hand2").pack(side="right", padx=4)
        
        instrucLabel =  tk.Label(card,
            text="ⓘ  Click a row to select before editing, assigning, or deleting.",
            bg=WHITE, fg=FG_MUTED, font=("Segoe UI", 8),
            anchor="w")

        #Packing
        upperFrame.pack(fill="x", padx=28, pady=(20, 12))
        card.pack(fill="both", expand=True, padx=28, pady=(0, 20))
        searchFrame.pack(fill="x", padx=16, pady=(14, 10))
        tree_frame.pack(fill="both", expand=True, padx=16)
        seperator.pack(fill="x", padx=16, pady=(6, 0))
        btnFrame.pack(fill="x", padx=16, pady=10)
        instrucLabel.pack(fill="x", padx=20, pady=(0, 10))
    
    def build_settings_page(page):
        tk.Label(page, text="FOR LOG OUT AND USER MANAGEMENT", bg=content_color, fg=font_color_sidebar,
                 font=("Arial", 16, "bold")).pack(pady=20)


        
    # Main Sidebar
    sidebar = tk.Frame(root, bg=sidebar_color, width=300)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)
    
    tk.Label(sidebar, text="Dormi", bg=sidebar_color, fg=font_color_sidebar,
             font=("Arial", 14, "bold")).pack(anchor="w", padx=15, pady=(20, 0))
    tk.Label(sidebar, text="Admin panel", bg=sidebar_color, fg=font_color_sidebar,
             font=("Arial", 9)).pack(anchor="w", padx=15, pady=(0, 20))
    
    # Main content area
    content = tk.Frame(root, bg=content_color)
    content.pack(side="left", fill="both", expand=True)
    
    # ── Pages ──────────────────────────────────────────────
    dashboard_page = tk.Frame(content, bg=content_color)
    students_page  = tk.Frame(content, bg=content_color)
    rooms_page     = tk.Frame(content, bg=content_color)
    cleaning_page  = tk.Frame(content, bg=content_color)
    settings_page  = tk.Frame(content, bg=content_color)
    #Distinct Content for each page
    build_dashboard_page(dashboard_page)
    build_students_page(students_page)
    build_rooms_page(rooms_page)
    build_cleaning_page(cleaning_page)
    build_settings_page(settings_page)
    
    # ── Show page function ──────────────────────────────────
    all_pages   = [dashboard_page, students_page, rooms_page, cleaning_page, settings_page]
    all_buttons = []
    
    def show_page(page, active_btn):
        for p in all_pages:
            p.pack_forget()
        for btn in all_buttons:
            btn.config(bg=sidebar_color)
        page.pack(fill="both", expand=True)
        active_btn.config(bg=active_color)
    
    # ── Sidebar buttons ─────────────────────────────────────
    tk.Label(sidebar, text="MAIN", bg=sidebar_color, fg=font_color_sidebar,
             font=("Arial", 8)).pack(anchor="w", padx=15, pady=(5, 2))
    
    dashboardButton = tk.Button(sidebar, text="  Dashboard", bg=active_color, fg=font_color_sidebar,
                                font=("Arial", 10), relief="flat", anchor="w",
                                padx=10, pady=8, cursor="hand2")
    dashboardButton.pack(fill="x", padx=10, pady=2)
    
    tk.Label(sidebar, text="MANAGE", bg=sidebar_color, fg=font_color_sidebar,
             font=("Arial", 8)).pack(anchor="w", padx=15, pady=(10, 2))
    
    studentButton = tk.Button(sidebar, text="  Students", bg=sidebar_color, fg=font_color_sidebar,
                              font=("Arial", 10), relief="flat", anchor="w",
                              padx=10, pady=8, cursor="hand2")
    studentButton.pack(fill="x", padx=10, pady=2)
    
    roomsButton = tk.Button(sidebar, text="  Rooms", bg=sidebar_color, fg=font_color_sidebar,
                            font=("Arial", 10), relief="flat", anchor="w",
                            padx=10, pady=8, cursor="hand2")
    roomsButton.pack(fill="x", padx=10, pady=2)
    
    cleaningButton = tk.Button(sidebar, text="  Cleaning staff", bg=sidebar_color, fg=font_color_sidebar,
                               font=("Arial", 10), relief="flat", anchor="w",
                               padx=10, pady=8, cursor="hand2")
    cleaningButton.pack(fill="x", padx=10, pady=2)

    Settings = tk.Button(sidebar, text="  Settings", bg=sidebar_color, fg=font_color_sidebar,
                               font=("Arial", 10), relief="flat", anchor="w",
                               padx=10, pady=8, cursor="hand2")
    Settings.pack(fill="x", padx=10, pady=2)
    
    # Extend all_buttons list
    all_buttons.extend([dashboardButton, studentButton, roomsButton, cleaningButton, Settings])
    

    #Buttons Logic
    dashboardButton.config(command=lambda: show_page(dashboard_page, dashboardButton))
    studentButton.config(command=lambda: show_page(students_page, studentButton))
    roomsButton.config(command=lambda: show_page(rooms_page, roomsButton))
    cleaningButton.config(command=lambda: show_page(cleaning_page, cleaningButton))
    Settings.config(command=lambda: show_page(settings_page, Settings))
    
    show_page(dashboard_page, dashboardButton)
    
    root.mainloop()
    if login_root:
        login_root.destroy()
