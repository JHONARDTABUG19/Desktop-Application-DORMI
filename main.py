import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.geometry("1200x650")
root.minsize(1150, 650)
root.title("Dormi Admin Panel")

font_color_sidebar = "white"
sidebar_color = "#0f1b3d"
active_color = "#2e3a6e"
content_color = "#eceaea"

UNIFORM_FONT = ("Segoe UI", 10)

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

    tk.Label(page, text="Recent student assignments", bg=content_color,font=("Arial", 12, "bold"), fg="black").pack(anchor="w", pady=5, padx=30)

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
    WHITE      = "#ffffff"
    HEADER_BG  = "#eae8f0"
    ROW_ALT    = "#f7f6fb"
    ROW_SEL    = "#dcd8f0"
    BORDER     = "#dde0ee"
    FG_DARK    = "#1a1a2e"
    FG_MUTED   = "#9aa3c2"

    # ── Top bar ─────────────────────────────────────────
    topbar = tk.Frame(page, bg=content_color)
    topbar.pack(fill="x", padx=28, pady=(20, 12))

    tk.Label(topbar, text="Students", bg=content_color, fg=FG_DARK,
             font=("Segoe UI", 17, "bold")).pack(side="left")

    tk.Label(topbar, text="⋯", bg=content_color, fg=FG_DARK,
             font=("Segoe UI", 13)).pack(side="right", padx=(6, 0))

    tk.Button(topbar, text="+ Add student", bg=WHITE, fg=FG_DARK,
              font=UNIFORM_FONT, relief="solid", bd=1,
              padx=12, pady=5, cursor="hand2").pack(side="right")

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

def build_cleaning_page(page):
    tk.Label(page, text="Cleaning Staff Page", bg=content_color, fg=font_color_sidebar,
             font=("Arial", 16, "bold")).pack(pady=20)

# Sidebar
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

build_dashboard_page(dashboard_page)
build_students_page(students_page)
build_rooms_page(rooms_page)
build_cleaning_page(cleaning_page)

# ── Show page function ──────────────────────────────────
all_pages   = [dashboard_page, students_page, rooms_page, cleaning_page]
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

all_buttons.extend([dashboardButton, studentButton, roomsButton, cleaningButton])

dashboardButton.config(command=lambda: show_page(dashboard_page, dashboardButton))
studentButton.config(command=lambda: show_page(students_page, studentButton))
roomsButton.config(command=lambda: show_page(rooms_page, roomsButton))
cleaningButton.config(command=lambda: show_page(cleaning_page, cleaningButton))

show_page(dashboard_page, dashboardButton)

root.mainloop()
