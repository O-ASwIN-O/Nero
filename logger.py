import sqlite3
import psutil
import time
import os
from datetime import datetime
import win32gui
import win32process

DB_PATH = "data/activity.db"
MIN_SESSION_SECONDS = 2   # Ignore noisy rapid switching


# -------------------------------
# DATABASE SETUP
# -------------------------------
def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            process TEXT,
            window_title TEXT,
            start_time TEXT,
            end_time TEXT,
            duration_seconds INTEGER,
            event_type TEXT
        )
    """)

    # Add index for faster querying later
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_start_time
        ON sessions(start_time)
    """)

    conn.commit()
    conn.close()


# -------------------------------
# GET ACTIVE WINDOW INFO
# -------------------------------
def get_active_window():
    hwnd = win32gui.GetForegroundWindow()
    window_title = win32gui.GetWindowText(hwnd)

    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process = psutil.Process(pid).name()
    except Exception:
        process = "unknown"

    return process, window_title


# -------------------------------
# DETECT EVENT TYPE
# -------------------------------
def detect_event(window_title):
    title = window_title.lower()

    if "chatgpt" in title:
        return "chatgpt_opened"
    elif "error" in title:
        return "error_detected"
    elif "exception" in title:
        return "exception_detected"
    elif "traceback" in title:
        return "traceback_detected"
    else:
        return "normal"


# -------------------------------
# SAVE SESSION SAFELY
# -------------------------------
def save_session(cursor, process, title, start_time, event_type):
    if process is None or start_time is None:
        return

    end_time = datetime.now()
    duration = int((end_time - start_time).total_seconds())

    # Ignore very short sessions
    if duration < MIN_SESSION_SECONDS:
        return

    cursor.execute("""
        INSERT INTO sessions
        (process, window_title, start_time, end_time, duration_seconds, event_type)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        process,
        title,
        start_time.isoformat(),
        end_time.isoformat(),
        duration,
        event_type
    ))

    print(f"Saved: {process} | {duration}s | {event_type}")


# -------------------------------
# MAIN LOGGER LOOP
# -------------------------------
def log_activity():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Optimized Nero Logger Started...")

    last_process = None
    last_title = None
    last_event = None
    start_time = None

    try:
        while True:
            process, window_title = get_active_window()
            event_type = detect_event(window_title)

            # Detect session change (process OR title change)
            if process != last_process or window_title != last_title:

                # Save previous session
                save_session(cursor, last_process, last_title, start_time, last_event)
                conn.commit()

                # Start new session
                last_process = process
                last_title = window_title
                last_event = event_type
                start_time = datetime.now()

            time.sleep(2)

    except KeyboardInterrupt:
        print("\nStopping logger...")

    finally:
        # Save last active session on shutdown
        save_session(cursor, last_process, last_title, start_time, last_event)
        conn.commit()
        conn.close()
        print("Logger safely closed.")


if __name__ == "__main__":
    init_db()
    log_activity()