import sqlite3
import logging

DB_PATH = "data/nero.db"

def get_past_predictions() -> list[str]:
    """Retrieve past predictions to help the AI learn context from past user prompts."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # We only want recent and unique ones implicitly via DB layout, but fetching all for simple pattern matching
        # Adjust SQL to just get recent distinct ones if DB grows large
        cursor.execute("SELECT prediction FROM predictions ORDER BY id DESC LIMIT 50")
        rows = cursor.fetchall()
        
        conn.close()
        
        # Flatten and filter out basic errors
        predictions = []
        for row in rows:
            if row[0] and not row[0].startswith("Error:"):
                # Usually it's a block of text, maybe split by lines
                lines = row[0].split("\n")
                for line in lines:
                    line = line.strip()
                    if line and line not in predictions:
                        predictions.append(line)
                        
        return predictions
        
    except sqlite3.Error as e:
        logging.error(f"Failed to fetch past predictions: {e}")
        return []
