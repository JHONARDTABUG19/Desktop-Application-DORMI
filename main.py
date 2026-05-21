import tkinter as tk
import tkinter.ttk as ttk
from tkinter import *

root = tk.Tk()
root.geometry("1200x650")
root.minsize(1100, 650)
root.title("Dormi Admin Panel")

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
sidebar_color = "#0f1b3d"
active_color = "#2e3a6e"
content_color = "#c7bfbf"
black = "#070707"

# ── Page content functions ──────────────────────────────
def build_dashboard_page(page):
    tk.Label(page, text="Dashboard Page", bg=content_color, fg=font_color_sidebar,
             font=("Arial", 16, "bold")).pack(pady=20)
    tk.Button(page, text="test button for dashboard", bg="#446ad2", fg="white").pack(anchor="w", pady=10, padx=20)

def build_students_page(page):
    tk.Label(page, text="Students Page", bg=content_color, fg=font_color_sidebar,
             font=("Arial", 16, "bold")).pack(pady=20)
    # add more student widgets here...

def build_rooms_page(page):
    tk.Label(page, text="Rooms Page", bg=content_color, fg=font_color_sidebar,
             font=("Arial", 16, "bold")).pack(pady=20)
    # add more room widgets here...

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

    assign.mainloop()


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

    #Line below is for selecting record, will be used later
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


# Sidebar
sidebar = tk.Frame(root, bg=sidebar_color, width=200)
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

# Build all pages
build_dashboard_page(dashboard_page)
build_students_page(students_page)
build_rooms_page(rooms_page)
build_cleaning_page(cleaning_page)


# ── Show page function ──────────────────────────────────
all_pages = [dashboard_page, students_page, rooms_page, cleaning_page]
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
