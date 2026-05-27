from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
from zDesktop_in_class import main
import sqlite3
import sys
import os

def resource_path(relative_path):
    """Get the correct path whether running as script or .exe"""
    if hasattr(sys, '_MEIPASS'):
        # running as .exe — PyInstaller extracts files here
        return os.path.join(sys._MEIPASS, relative_path)
    # running normally as .py
    return os.path.join(os.path.abspath("."), relative_path)



def create_table_for_login():
    connect = sqlite3.connect("dorm_management.db")
    cursor = connect.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(255) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL)
    """)

    cursor.execute("""
    INSERT OR IGNORE INTO Admin (username, password)
    VALUES (?, ?)""", ("admin", "admin123"))

    connect.commit()
    connect.close()



def login_page(): 
      
      DB_NAME = "dorm_management.db"

      create_table_for_login()
      
      def login_action():
        username = username_entry.get()
        password = password_entry.get()

        if check_login_entry(username, password):
            messagebox.showinfo("Success", "Login Successful")
            root.destroy()
            main()
        else:
            messagebox.showerror("Error", "Invalid Username or Password")

      def check_login_entry(username, password):
            connect = sqlite3.connect(DB_NAME)
            cursor = connect.cursor()
            cursor.execute(
                  "SELECT * FROM Admin WHERE USERNAME=? AND PASSWORD=?", (username, password))
            result = cursor.fetchone()
            connect.close()
            return result is not None


      background_outside_frame = "#FFE8BB"
      background = "#F3E4C9"
      background_inside_frame = "#ffffff"

      root = Tk()
      root.title("Dormi Management System")
      root.geometry("1000x600")
      root.configure(bg=background_outside_frame)

      # ── Center frame ──────────────────────────────────────────────
      frame = LabelFrame(root, bg=background, highlightbackground="black", highlightthickness=2)
      frame.place(relx=0.5, rely=0.5, anchor=CENTER, width=960, height=440)

      # ── Left: Image ───────────────────────────────────────────────
      img_raw = Image.open(resource_path("dormyz.png"))
      img_raw = img_raw.resize((600, 440))
      img = ImageTk.PhotoImage(img_raw)

      img_label = Label(frame, image=img, bd=0)
      img_label.pack(side=LEFT)

      # ── Right: Login form ─────────────────────────────────────────
      right = Frame(frame, bg=background)
      right.pack(side=LEFT, fill=BOTH, expand=True, padx=30)

      Label(right, text="Dormitory", font=("Georgia", 20, "bold"),bg=background, fg="#000000").pack(anchor=W, pady=(60, 2))
      
      Label(right, text="Management System", font=("Georgia", 18, "bold"),bg=background, fg="#000000").pack(anchor=W)

      Label(right, text="Admin Login", font=("Arial", 10),bg=background, fg="#101114").pack(anchor=W, pady=(0, 30))

      # Username
      Label(right, text="Username", font=("Arial", 10, "bold"),bg=background, fg="#101114").pack(anchor=W)

      username_entry = Entry(right, font=("Arial", 12),bg=background_inside_frame, fg="#000000",relief=FLAT, bd=0)
      username_entry.pack(fill=X, ipady=8, pady=(4, 18))

      # Password
      Label(right, text="Password", font=("Arial", 10, "bold"),bg=background, fg="#101114").pack(anchor=W)

      password_entry = Entry(right, font=("Arial", 12),bg=background_inside_frame, fg="#000000",relief=FLAT, bd=0, show="•")
      password_entry.pack(fill=X, ipady=8, pady=(4, 28))

      # Button
      btn = Button(right, text="Log In", font=("Arial", 11, "bold"),bg="#A77F60", fg="#ffffff",activebackground="#858585",relief=FLAT, bd=0, cursor="hand2", command=lambda: login_action())
      btn.pack(fill=X, ipady=10)

      root.mainloop()


      
login_page()





