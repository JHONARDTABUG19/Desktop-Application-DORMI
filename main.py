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
    
    
    def build_rooms_page(page):
        tk.Label(page, text="Rooms", bg=content_color, fg=font_color_sidebar,
                 font=("Arial", 16, "bold")).pack(pady=20)
    
    # Cleaning Staff
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
        addStaffBtn = tk.Button(upperFrame, text="+ Add Staff", bg=WHITE, fg=FG_DARK,
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
