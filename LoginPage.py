import tkinter as tk
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
BG          = "#1C1A17"          # near-black warm background
PANEL       = "#26231F"          # slightly lighter card panel
ACCENT      = "#C8915A"          # warm amber — matches sidebar_color family
ACCENT_DARK = "#A77040"          # hover / pressed state
WHITE       = "#F5F0EA"          # off-white text
MUTED       = "#7A7167"          # placeholder / hint text
BORDER      = "#3A352E"          # subtle input border
INPUT_BG    = "#2E2A25"          # input field background
ERR         = "#E05A5A"          # error red

DB_NAME = "dorm_management.db"


# ── DB helpers ────────────────────────────────────────────────────────
def create_table_for_login():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Admin (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL
        )
    """)
    cur.execute("INSERT OR IGNORE INTO Admin (username, password) VALUES (?,?)",
                ("admin", "admin123"))
    con.commit()
    con.close()


def check_credentials(username, password):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("SELECT * FROM Admin WHERE username=? AND password=?", (username, password))
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
            self.entry.config(fg=WHITE, show=self._show)
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
    # Try to show the dorm image; fall back to a typographic panel
    img_ref = None
    image_loaded = False

    if PIL_AVAILABLE:
        for img_path in ["dormyz.png", "Dormi.png", "dormi.png",
                         os.path.join("IM", "dormyz.png")]:
            if os.path.exists(img_path):
                try:
                    raw = Image.open(img_path).resize((400, 560), Image.LANCZOS)
                    # dark overlay tint
                    overlay = Image.new("RGBA", raw.size, (28, 26, 23, 160))
                    if raw.mode != "RGBA":
                        raw = raw.convert("RGBA")
                    raw = Image.alpha_composite(raw, overlay).convert("RGB")
                    img_ref = ImageTk.PhotoImage(raw)
                    lbl = tk.Label(left, image=img_ref, bd=0)
                    lbl.place(x=0, y=0, relwidth=1, relheight=1)
                    lbl.image = img_ref
                    image_loaded = True
                    break
                except Exception:
                    pass

    # Branding text on top of image (or plain bg)
    brand_frame = tk.Frame(left, bg="" if image_loaded else ACCENT)
    brand_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
    if image_loaded:
        brand_frame.config(bg="")          # transparent feel via same bg trick
        # use a canvas label so text shows over image
        canvas = tk.Canvas(left, bg=ACCENT, highlightthickness=0, width=400, height=560)
        canvas.place(x=0, y=0)
        if img_ref:
            canvas.create_image(0, 0, anchor="nw", image=img_ref)
        # dark gradient strip at bottom
        for i in range(180):
            alpha_hex = format(min(255, int(i * 1.4)), "02x")
            color = f"#1c1a17"
            canvas.create_line(0, 560-180+i, 400, 560-180+i, fill=color)
        canvas.create_text(32, 390, anchor="sw",
                           text="🏠  Dormi", fill=WHITE,
                           font=("Georgia", 28, "bold"))
        canvas.create_text(32, 415, anchor="sw",
                           text="Dormitory Management System", fill=MUTED,
                           font=("Segoe UI", 11))
        # keep image reference alive
        canvas.image = img_ref
    else:
        # Pure typographic left panel (no image)
        tk.Label(left, text="🏠", font=("Segoe UI", 48),
                 bg=ACCENT, fg=WHITE).pack(pady=(120, 8))
        tk.Label(left, text="Dormi", font=("Georgia", 30, "bold"),
                 bg=ACCENT, fg=WHITE).pack()
        tk.Label(left, text="Dormitory\nManagement System",
                 font=("Segoe UI", 11), bg=ACCENT, fg="#1C1A17",
                 justify="center").pack(pady=(8, 0))

        # decorative bottom strip
        tk.Frame(left, bg="#A77040", height=6).pack(side="bottom", fill="x")

    # ── Right panel — form ──────
    form = tk.Frame(right, bg=PANEL)
    form.place(relx=0.5, rely=0.5, anchor="center", width=340)

    tk.Label(form, text="Welcome back", font=("Georgia", 22, "bold"),
             bg=PANEL, fg=WHITE).pack(anchor="w", pady=(0, 4))
    tk.Label(form, text="Sign in to your admin account",
             font=("Segoe UI", 10), bg=PANEL, fg=MUTED).pack(anchor="w", pady=(0, 28))

    # Username
    tk.Label(form, text="USERNAME", font=("Segoe UI", 8, "bold"),
             bg=PANEL, fg=MUTED).pack(anchor="w", pady=(0, 4))
    username_entry = StyledEntry(form, placeholder="Enter your username")
    username_entry.pack(fill="x", pady=(0, 16))

    # Password
    tk.Label(form, text="PASSWORD", font=("Segoe UI", 8, "bold"),
             bg=PANEL, fg=MUTED).pack(anchor="w", pady=(0, 4))
    password_entry = StyledEntry(form, placeholder="Enter your password", show="•")
    password_entry.pack(fill="x", pady=(0, 6))

    # Show/hide password toggle
    show_var = tk.BooleanVar(value=False)
    def toggle_pw():
        if show_var.get():
            password_entry.entry.config(show="")
            toggle_btn.config(text="🙈  Hide")
        else:
            password_entry.entry.config(show="•")
            toggle_btn.config(text="👁  Show")
    toggle_btn = tk.Button(form, text="👁  Show", bg=PANEL, fg=MUTED,
                           font=("Segoe UI", 8), relief="flat", bd=0,
                           cursor="hand2",
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
        username = username_entry.get().strip()
        password = password_entry.get().strip()

        if not username or not password:
            err_label.config(text="Please enter both username and password.")
            shake(form)
            return

        if check_credentials(username, password):
            err_label.config(text="")
            root.destroy()
            from MainPage import main as MainApp
            app = MainApp()
            app.mainloop()
        else:
            err_label.config(text="Incorrect username or password.")
            password_entry.entry.delete(0, "end")
            shake(form)

    # Enter key triggers login
    root.bind("<Return>", attempt_login)

    # ── Shake animation on wrong password
    def shake(widget, times=6, distance=8):
        orig_x = widget.winfo_x()
        orig_y = widget.winfo_y()
        def _shake(count, direction):
            if count <= 0:
                widget.place(x=orig_x, y=orig_y)
                return
            widget.place(x=orig_x + direction * distance, y=orig_y)
            widget.after(40, lambda: _shake(count - 1, -direction))
        _shake(times, 1)

    root.mainloop()


if __name__ == "__main__":
    login_page()
