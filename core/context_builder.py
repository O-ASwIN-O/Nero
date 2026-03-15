import os
import logging
from core.activity_tracker import tracker
from core.file_monitor import get_last_modified_file

# -------------------------------
# BUILD AI CONTEXT
# -------------------------------
def build_context(signals: dict) -> str:
    """
    Build rich context from activity history + current file content.
    This gives the LLM a complete picture of what the user has been doing.
    """
    parts = []
    
    # 1. Activity timeline (Google searches, window switches, file edits, etc.)
    activity = tracker.get_activity_summary()
    if activity and activity != "No recent activity detected.":
        parts.append("Recent activity timeline:")
        parts.append(activity)
    
    # 2. Current file content (if any file was recently edited)
    last_file = signals.get('last_file', 'None')
    if last_file and last_file not in ('None', 'Error') and os.path.exists(last_file):
        try:
            with open(last_file, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
                code = "".join(lines[-20:]).strip()
                if code:
                    basename = os.path.basename(last_file)
                    parts.append(f"\nCurrently editing: {basename}")
                    parts.append(f"Code:\n{code}")
        except Exception:
            pass
    
    if not parts:
        parts.append("Developer just started a session.")
    
    return "\n".join(parts)
