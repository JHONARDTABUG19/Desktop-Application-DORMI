import tkinter as tk
import sqlite3
import base64
import io

from tkinter import messagebox
import sqlite3
import os

# ── Try importing Pillow (optional — falls back gracefully) ───────────
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


# ── Colours ───────────────────────────────────────────────────────────
BG      = "#f0f0f0"     # light grey root background
PANEL   = "#ffffff"     # white right panel
ACCENT  = "#23b3d3"     # teal accent (buttons, highlights)
ACCENT_DARK = "#17849c" # darker teal for hover/pressed
WHITE   = "#ffffff"
MUTED   = "#6b7280"     # medium grey for labels & placeholders
BORDER  = "#d1d5db"     # light grey border for input boxes
INPUT_BG = "#f9fafb"    # near-white input background
ERR     = "#e05252"     # soft red for errors


DB_NAME = "dorm_management.db"


# ── DB helpers ────────────────────────────────────────────────────────
def create_table_for_login():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ADMIN (
            AdminID       INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
            Username VARCHAR(255) NOT NULL UNIQUE,
            Password VARCHAR(255) NOT NULL
        )
    """)
    cur.execute("INSERT OR IGNORE INTO ADMIN (Username, Password) VALUES (?,?)",
                ("admin", "admin123"))
    con.commit()
    con.close()


def check_credentials(Username, Password):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("SELECT * FROM ADMIN WHERE Username=? AND Password=?", (Username, Password))
    result = cur.fetchone()
    con.close()
    return result is not None


# ── Rounded-rectangle canvas helper ───────────────────────────────────
def rounded_rect(canvas, x1, y1, x2, y2, r, **kwargs):
    canvas.create_arc(x1,     y1,     x1+2*r, y1+2*r, start=90,  extent=90,  style="pieslice", **kwargs)
    canvas.create_arc(x2-2*r, y1,     x2,     y1+2*r, start=0,   extent=90,  style="pieslice", **kwargs)
    canvas.create_arc(x1,     y2-2*r, x1+2*r, y2,     start=180, extent=90,  style="pieslice", **kwargs)
    canvas.create_arc(x2-2*r, y2-2*r, x2,     y2,     start=270, extent=90,  style="pieslice", **kwargs)
    canvas.create_rectangle(x1+r, y1,   x2-r, y2,   **kwargs)
    canvas.create_rectangle(x1,   y1+r, x2,   y2-r, **kwargs)


# ── Custom styled entry ───────────────────────────────────────────────
class StyledEntry(tk.Frame):
    def __init__(self, parent, placeholder="", show="", **kwargs):
        super().__init__(parent, bg=INPUT_BG,
                         highlightbackground=BORDER, highlightthickness=1)
        self._placeholder = placeholder
        self._showing_placeholder = True

        self.entry = tk.Entry(self, bg=INPUT_BG, fg=MUTED,
                              font=("Segoe UI", 11), relief="flat", bd=0,
                              insertbackground=ACCENT,
                              show="" if placeholder else show)
        self.entry.pack(fill="x", padx=12, pady=10)
        self._show = show

        if placeholder:
            self.entry.insert(0, placeholder)

        self.entry.bind("<FocusIn>",  self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)
        self.bind("<Enter>", lambda e: self.config(highlightbackground=ACCENT))
        self.bind("<Leave>", lambda e: self.config(highlightbackground=BORDER))

    def _on_focus_in(self, e):
        self.config(highlightbackground=ACCENT)
        if self._showing_placeholder:
            self.entry.delete(0, "end")
            self.entry.config(fg="#111111", show=self._show)
            self._showing_placeholder = False

    def _on_focus_out(self, e):
        self.config(highlightbackground=BORDER)
        if not self.entry.get():
            self.entry.config(fg=MUTED, show="")
            self.entry.insert(0, self._placeholder)
            self._showing_placeholder = True

    def get(self):
        if self._showing_placeholder:
            return ""
        return self.entry.get()


# ── Main login page ───────────────────────────────────────────────────
def login_page():
    create_table_for_login()

    root = tk.Tk()
    root.title("Dormi — Admin Login")
    root.geometry("940x560")
    root.resizable(False, False)
    root.configure(bg=BG)

    # ── Two-column layout ─────────────────────────────────────────────
    left  = tk.Frame(root, bg=ACCENT, width=400)
    right = tk.Frame(root, bg=PANEL,  width=540)
    left.pack(side="left",  fill="y")
    right.pack(side="left", fill="both", expand=True)
    left.pack_propagate(False)
    right.pack_propagate(False)

    # ── Left panel — branding ─────────────────────────────────────────
    # Show Dormi_Text.png centered on the left; fall back to typography
    left_canvas = tk.Canvas(left, width=400, height=560,
                            bg=ACCENT, highlightthickness=0)
    left_canvas.place(x=0, y=0)

    # Search relative to this script's folder so the image is found
    # regardless of what the working directory is at runtime.
    _here = os.path.dirname(os.path.abspath(__file__))

    dormi_text_ref = None
    if PIL_AVAILABLE:
        for txt_path in [
            os.path.join(_here, "Dormi_Text.png"),
            os.path.join(_here, "Dormi_Icon.png"),
            os.path.join(_here, "IM", "Dormi_Text.png"),
            os.path.join(_here, "IM", "Dormi.png"),
            "Dormi_Text.png",
            "Dormi_Icon.png",
        ]:
            if os.path.exists(txt_path):
                try:
                    txt_img = Image.open(txt_path).convert("RGBA")
                    txt_img = txt_img.resize((260, 260), Image.LANCZOS)
                    dormi_text_ref = ImageTk.PhotoImage(txt_img)
                    left_canvas.create_image(200, 240, anchor="center",
                                             image=dormi_text_ref)
                    left_canvas.image = dormi_text_ref
                    break
                except Exception:
                    pass

    if dormi_text_ref is None:
        # Fallback: plain text branding
        left_canvas.create_text(200, 220, text="🏠", fill=WHITE,
                                font=("Segoe UI", 52), anchor="center")
        left_canvas.create_text(200, 290, text="Dormi",
                                fill=WHITE, font=("Georgia", 32, "bold"),
                                anchor="center")

    left_canvas.create_text(200, 430, text="Dormitory Management System",
                            fill=MUTED, font=("Segoe UI", 10), anchor="center")
    left_canvas.create_text(200, 452, text="Admin Portal  ·  v1.0",
                            fill=BORDER, font=("Segoe UI", 9), anchor="center")
    # accent strip at bottom
    left_canvas.create_rectangle(0, 554, 400, 560, fill=ACCENT_DARK, outline="")

    # ── Right panel — form ──────
    form = tk.Frame(right, bg=PANEL)
    form.place(relx=0.5, rely=0.5, anchor="center", width=340)

    tk.Label(form, text="Welcome back", font=("Poppins", 22, "bold"),
             bg=PANEL, fg="#111111").pack(anchor="w", pady=(0, 4))
    tk.Label(form, text="Sign in to your admin account",
             font=("Segoe UI", 10), bg=PANEL, fg=MUTED).pack(anchor="w", pady=(0, 28))

    # Username
    tk.Label(form, text="USERNAME", font=("Segoe UI", 8, "bold"),
             bg=PANEL, fg=MUTED).pack(anchor="w", pady=(0, 4))
    username_entry = StyledEntry(form, placeholder="Enter your Username")
    username_entry.pack(fill="x", pady=(0, 16))

    # Password
    tk.Label(form, text="PASSWORD", font=("Segoe UI", 8, "bold"),
             bg=PANEL, fg=MUTED).pack(anchor="w", pady=(0, 4))
    password_entry = StyledEntry(form, placeholder="Enter your Password", show="•")
    password_entry.pack(fill="x", pady=(0, 6))

    # Show/hide Password toggle
    show_var = tk.BooleanVar(value=False)
    def toggle_pw():
        if show_var.get():
            password_entry.entry.config(show="")
            toggle_btn.config(text="🙈  Hide")
        else:
            password_entry.entry.config(show="•")
            toggle_btn.config(text="👁  Show")
    toggle_btn = tk.Button(form, text="👁  Show", bg=PANEL, fg=ACCENT,
                           font=("Segoe UI", 8), relief="flat", bd=0,
                           cursor="hand2", activebackground=PANEL, activeforeground=WHITE,
                           command=lambda: [show_var.set(not show_var.get()), toggle_pw()])
    toggle_btn.pack(anchor="e", pady=(0, 24))

    # Error label
    err_label = tk.Label(form, text="", fg=ERR, bg=PANEL,
                         font=("Segoe UI", 9))
    err_label.pack(anchor="w", pady=(0, 8))

    # Login button (canvas-drawn for rounded corners)
    btn_canvas = tk.Canvas(form, width=340, height=46,
                           bg=PANEL, highlightthickness=0)
    btn_canvas.pack(fill="x", pady=(0, 20))

    def draw_btn(color):
        btn_canvas.delete("all")
        rounded_rect(btn_canvas, 0, 0, 340, 46, 8, fill=color, outline=color)
        btn_canvas.create_text(170, 23, text="Sign In",
                               fill=WHITE, font=("Segoe UI", 11, "bold"))

    draw_btn(ACCENT)
    btn_canvas.bind("<Enter>",    lambda e: draw_btn(ACCENT_DARK))
    btn_canvas.bind("<Leave>",    lambda e: draw_btn(ACCENT))
    btn_canvas.bind("<Button-1>", lambda e: attempt_login())

    # Divider
    div = tk.Frame(form, bg=BORDER, height=1)
    div.pack(fill="x", pady=(0, 16))

    tk.Label(form, text="Dormi v1.0  ·  Admin Portal",
             font=("Segoe UI", 8), bg=PANEL, fg=MUTED).pack(anchor="center")

    # ── Login logic ──
    def attempt_login(event=None):
        Username = username_entry.get().strip()
        Password = password_entry.get().strip()

        if not Username or not Password:
            err_label.config(text="Please enter both Username and Password.")
            shake(form)
            return

        if check_credentials(Username, Password):
            err_label.config(text="")
            root.destroy()
            from MainPage import main as MainApp
            app = MainApp()
            app.mainloop()
        else:
            err_label.config(text="Incorrect Username or Password.")
            password_entry.entry.delete(0, "end")
            shake(form)

    # Enter key triggers login
    root.bind("<Return>", attempt_login)

    # ── Shake animation on wrong Password
    def shake(widget, times=6, distance=8):
        def _shake(count, direction):
            if count <= 0:
                widget.place(relx=0.5, rely=0.5, anchor="center", width=340, x=0)
                return
            widget.place(relx=0.5, rely=0.5, anchor="center", width=340, x=direction * distance)
            widget.after(40, lambda: _shake(count - 1, -direction))
        _shake(times, 1)

    root.mainloop()


if __name__ == "__main__":
    login_page()
