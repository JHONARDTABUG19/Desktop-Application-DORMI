# Dormi — Dorm Management Desktop App

A local desktop application for managing dorm students, rooms, and cleaning staff. Built with Python (Tkinter) and SQLite.

---

## Requirements

- Python 3.10 or higher
- Required libraries:
  ```bash
  pip install pillow
  pip install pyinstaller
  ```

---

## Running the App in Development

1. Clone or download the project folder.
2. Make sure the following files are in the same folder:
   ```
   your_project/
   ├── LoginPage.py
   ├── MainPage.py
   ├── dormyz.png
   └── dorm_management.db        <- auto-created on first run
   ```
3. Run the login page:
   ```bash
   python LoginPage.py
   ```

---

## Building as a Standalone Desktop App (.exe)

No Python or VS Code needed on the target machine after this.

**Step 1** — Install PyInstaller:
```bash
pip install pyinstaller
```

**Step 2** — Navigate to your project folder in the terminal and run:
```bash
python -m PyInstaller --onefile --windowed --add-data "dormyz.png;." LoginPage.py
```

**Step 3** — After the build finishes, go to the `dist` folder:
```
your_project/
├── dist/
│   └── LoginPage.exe    <- your standalone app
├── build/               <- ignore
├── LoginPage.spec       <- ignore
├── LoginPage.py
├── MainPage.py
└── dormyz.png
```

**Step 4** — Double-click `LoginPage.exe` inside `dist/` to launch the app.

> The `dorm_management.db` database file will be **automatically created** in the same folder as the `.exe` on first run. All your data is stored there.

---

## Notes

- The app is intended for **single admin use** on one machine.
- The `.db` file holds all your data — back it up regularly by copying it somewhere safe.
- If you move the `.exe` to another folder or PC, the database starts fresh. To carry your data over, move the `.db` file alongside the `.exe`.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `pyinstaller` not recognized | Use `python -m PyInstaller` instead |
| App crashes on launch | Rebuild without `--windowed` to see the error in terminal |
| Image not found error | Make sure `dormyz.png` is in the project folder before building |
| `pip install` warning about PATH | Use `python -m pip install` instead of `pip install` |
