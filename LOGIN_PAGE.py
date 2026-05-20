from tkinter import *
from PIL import Image, ImageTk
from MainField import main
import sqlite3

def login_page():
      background = "#dafff1"
      background_inside_frame = "#ffffff"

      root = Tk()
      root.title("Dormi Management System")
      root.geometry("1000x600")
      root.resizable(False, False)
      root.configure(bg=background)

      # ── Center frame ──────────────────────────────────────────────
      frame = LabelFrame(root, bg=background, bd=0)
      frame.place(relx=0.5, rely=0.5, anchor=CENTER, width=960, height=440)

      # ── Left: Image ───────────────────────────────────────────────
      img_raw = Image.open("main files/Dormi.png")
      img_raw = img_raw.resize((600, 440))
      img = ImageTk.PhotoImage(img_raw)

      img_label = Label(frame, image=img, bd=0)
      img_label.pack(side=LEFT)

      # ── Right: Login form ─────────────────────────────────────────
      right = Frame(frame, bg=background)
      right.pack(side=LEFT, fill=BOTH, expand=True, padx=30)

      Label(right, text="🏠  Dormi", font=("Georgia", 20, "bold"),
            bg=background, fg="#000000").pack(anchor=W, pady=(60, 2))

      Label(right, text="Admin Login", font=("Arial", 10),
            bg=background, fg="#101114").pack(anchor=W, pady=(0, 30))

      # Username
      Label(right, text="Username", font=("Arial", 10, "bold"),
            bg=background, fg="#101114").pack(anchor=W)

      username_entry = Entry(right, font=("Arial", 12),
                        bg=background_inside_frame, fg="#000000",
                        insertbackground="#00AD28",
                        relief=FLAT, bd=0)
      username_entry.pack(fill=X, ipady=8, pady=(4, 18))

      # Password
      Label(right, text="Password", font=("Arial", 10, "bold"),
            bg=background, fg="#101114").pack(anchor=W)

      password_entry = Entry(right, font=("Arial", 12),
                        bg=background_inside_frame, fg="#000000",
                        insertbackground="#00AD28",
                        relief=FLAT, bd=0, show="•")
      password_entry.pack(fill=X, ipady=8, pady=(4, 28))

      # Button
      btn = Button(right, text="Login", font=("Arial", 11, "bold"),
                  bg="#000000", fg="#ffffff",
                  activebackground="#c3c3c3", activeforeground="#ffffff",
                  relief=FLAT, bd=0, cursor="hand2")
      btn.pack(fill=X, ipady=10)

      btn.bind("<Button-1>", lambda event: main())

      root.mainloop()

login_page()


