import sqlite3
import os
import logging

# Ensure database logic references accurate local paths relative to the project root
DB_PATH = "data/nero.db"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# -------------------------------
# DATABASE SETUP
# -------------------------------
def init_db():
    """Initialize the SQLite database and create necessary tables."""
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                context TEXT NOT NULL,
                prediction TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Add index for future fast queries based on timing
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp
            ON predictions(timestamp)
        """)

        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Database initialization error: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

# -------------------------------
# SAVE PREDICTION
# -------------------------------
def save_prediction(context: str, prediction: str):
    """Save the context and its resulting prediction safely."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO predictions (context, prediction) VALUES (?, ?)",
            (context, prediction)
        )

        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Failed to save prediction: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    init_db()
