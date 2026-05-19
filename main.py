import tkinter as tk

root = tk.Tk()
root.geometry("1200x650")
root.minsize(1100, 650)
root.title("Dormi Admin Panel")

font_color_sidebar = "white"
sidebar_color = "#0f1b3d"
active_color = "#2e3a6e"
content_color = "#c7bfbf"

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

def build_cleaning_page(page):
    tk.Label(page, text="Cleaning Staff Page", bg=content_color, fg=font_color_sidebar,
             font=("Arial", 16, "bold")).pack(pady=20)
    # add more cleaning staff widgets here...

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
