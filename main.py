import tkinter as tk

root = tk.Tk()
root.geometry("1200x650")
root.minsize(1100, 650)
root.title("Dormi Admin Panel")
 
font_color_sidebar = "white"
sidebar_color = "#0f1b3d"
active_color = "#2e3a6e"
content_color = "#c7bfbf"

# Sidebar
sidebar = tk.Frame(root, bg=sidebar_color, width=200)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

# App title
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

tk.Label(dashboard_page, text="Dashboard Page", bg=content_color, fg=font_color_sidebar, font=("Arial", 16, "bold")).pack(pady=20)
tk.Button(dashboard_page, text="test button for dashboard", bg="#446ad2", fg="white").pack(anchor="w",pady=10, padx=20)


tk.Label(students_page,  text="Students Page",  bg=content_color, fg=font_color_sidebar, font=("Arial", 16, "bold")).pack(pady=20)
tk.Label(rooms_page,     text="Rooms Page",     bg=content_color, fg=font_color_sidebar, font=("Arial", 16, "bold")).pack(pady=20)
tk.Label(cleaning_page,  text="Cleaning Staff Page", bg=content_color, fg=font_color_sidebar, font=("Arial", 16, "bold")).pack(pady=20)

# ── Show page function ──────────────────────────────────
all_pages = [dashboard_page, students_page, rooms_page, cleaning_page]
all_buttons = []  # will fill this after buttons are created

def show_page(page, active_btn):
    # Hide all pages
    for p in all_pages:
        p.pack_forget()

    # Reset all button colors
    for btn in all_buttons:
        btn.config(bg=sidebar_color)

    # Show selected page and highlight active button
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

# Now that buttons exist, fill the list
all_buttons.extend([dashboardButton, studentButton, roomsButton, cleaningButton])

# Assign commands to each button
dashboardButton.config(command=lambda: show_page(dashboard_page, dashboardButton))
studentButton.config(command=lambda: show_page(students_page, studentButton))
roomsButton.config(command=lambda: show_page(rooms_page, roomsButton))
cleaningButton.config(command=lambda: show_page(cleaning_page, cleaningButton))

# Show dashboard by default
show_page(dashboard_page, dashboardButton)

root.mainloop()