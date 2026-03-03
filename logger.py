import sqlite3
import psutil
import time
import os
from datetime import datetime
import win32gui
import win32process

DB_PATH = "data/activity.db"
MIN_SESSION_SECONDS = 2  # Ignore noisy rapid switching


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
            event_type TEXT,
            inferred_topic TEXT
        )
    """)

    # migrate existing table to include inferred_topic if missing
    cursor.execute("PRAGMA table_info('sessions')")
    existing_cols = [row[1] for row in cursor.fetchall()]
    if 'inferred_topic' not in existing_cols:
        cursor.execute("ALTER TABLE sessions ADD COLUMN inferred_topic TEXT")

    # Index for faster future querying
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
# DETECT EVENT TYPE + TOPIC
# -------------------------------
def detect_event(process, window_title):
    title = window_title.lower()
    process = process.lower()

    event_type = "normal"
    inferred_topic = None

    # Browser detection
    if any(browser in process for browser in ["chrome", "brave", "msedge"]):

        # Google Search detection
        if "google search" in title:
            event_type = "google_search"

            # Extract search query
            try:
                inferred_topic = window_title.split("- Google Search")[0].strip()
            except Exception:
                inferred_topic = None

        elif "chatgpt" in title:
            event_type = "chatgpt_opened"

        elif "gemini" in title:
            event_type = "gemini_opened"

        elif "geeksforgeeks" in title:
            event_type = "gfg_opened"

        else:
            event_type = "browser_tab"

    # Error detection
    elif any(word in title for word in ["error", "exception", "traceback"]):
        event_type = "error_detected"

    return event_type, inferred_topic


# -------------------------------
# SAVE SESSION SAFELY
# -------------------------------
def save_session(cursor, process, title, start_time, event_type, inferred_topic):
    if process is None or start_time is None:
        return

    end_time = datetime.now()
    duration = int((end_time - start_time).total_seconds())

    # Ignore very short sessions
    if duration < MIN_SESSION_SECONDS:
        return

    cursor.execute("""
        INSERT INTO sessions
        (process, window_title, start_time, end_time, duration_seconds, event_type, inferred_topic)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        process,
        title,
        start_time.isoformat(),
        end_time.isoformat(),
        duration,
        event_type,
        inferred_topic
    ))

    print(f"Saved: {process} | {duration}s | {event_type} | {inferred_topic}")


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
    last_topic = None
    start_time = None

    try:
        while True:
            process, window_title = get_active_window()
            event_type, inferred_topic = detect_event(process, window_title)

            # Detect session change
            if process != last_process or window_title != last_title:

                # Save previous session
                save_session(
                    cursor,
                    last_process,
                    last_title,
                    start_time,
                    last_event,
                    last_topic
                )
                conn.commit()

                # Start new session
                last_process = process
                last_title = window_title
                last_event = event_type
                last_topic = inferred_topic
                start_time = datetime.now()

            time.sleep(2)

    except KeyboardInterrupt:
        print("\nStopping logger...")

    finally:
        # Save last active session on shutdown
        save_session(
            cursor,
            last_process,
            last_title,
            start_time,
            last_event,
            last_topic
        )
        conn.commit()
        conn.close()
        print("Logger safely closed.")


if __name__ == "__main__":
    init_db()
    log_activity()