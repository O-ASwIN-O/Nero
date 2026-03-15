import logging
import time
import threading
from collections import deque

try:
    import pygetwindow as gw
except ImportError:
    gw = None

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ActivityTracker:
    """
    Tracks ALL user activity: window switches, browser searches, file edits.
    Maintains a rolling history of the last 20 actions.
    """
    
    def __init__(self, max_history=20):
        self.history = deque(maxlen=max_history)
        self._last_window_title = ""
        self._running = False
        self._lock = threading.Lock()
    
    def start(self):
        """Start background tracking thread."""
        self._running = True
        thread = threading.Thread(target=self._track_loop, daemon=True)
        thread.start()
        logging.info("Activity tracker started.")
    
    def _track_loop(self):
        """Continuously monitors active window titles every 2 seconds."""
        while self._running:
            try:
                self._capture_window()
            except Exception as e:
                logging.debug(f"Tracker tick error: {e}")
            time.sleep(2)
    
    def _capture_window(self):
        """Capture the current active window title and log meaningful changes."""
        if gw is None:
            return
            
        try:
            active = gw.getActiveWindow()
            if not active or not active.title:
                return
                
            title = active.title.strip()
            
            # Only log when the window title actually changes
            if title == self._last_window_title:
                return
            
            self._last_window_title = title
            
            # Parse the title to understand what the user is doing
            activity = self._parse_title(title)
            if activity:
                with self._lock:
                    self.history.append({
                        "time": time.strftime("%H:%M:%S"),
                        "action": activity
                    })
        except Exception:
            pass
    
    def _parse_title(self, title: str) -> str:
        """Convert raw window title into a human-readable activity description."""
        title_lower = title.lower()
        
        # Google Search detection
        if "google search" in title_lower:
            # Handle Chrome format: "mango - Google Search - Google Chrome"
            query = title_lower.replace(" - google search - google chrome", "")
            query = query.replace(" - google search", "").replace("google search - ", "").strip()
            if query and query != "google search":
                return f"Searched Google: '{query}'"
        
        # YouTube
        if "youtube" in title_lower:
            video = title.replace(" - YouTube", "").strip()
            return f"Watching YouTube: '{video}'"
        
        # Stack Overflow
        if "stack overflow" in title_lower:
            return f"Reading Stack Overflow: '{title.split(' - ')[0].strip()}'"
        
        # GitHub
        if "github" in title_lower:
            return f"Browsing GitHub: '{title.split(' · ')[0].strip()}'"
        
        # LLM sites
        if "chatgpt" in title_lower:
            return "Opened ChatGPT"
        if "claude" in title_lower:
            return "Opened Claude"
        if "gemini" in title_lower:
            return "Opened Gemini"
        if "grok" in title_lower:
            return "Opened Grok"
        
        # VS Code
        if "visual studio code" in title_lower:
            filename = title.split(" - ")[0].strip() if " - " in title else title
            return f"Editing in VS Code: '{filename}'"
        
        # Terminal/PowerShell/CMD
        if any(t in title_lower for t in ["powershell", "cmd", "terminal", "command prompt"]):
            return "Using terminal/command prompt"
        
        # File Explorer
        if "file explorer" in title_lower or "explorer" == title_lower:
            return "Browsing files in Explorer"
        
        # Generic browser tabs
        if any(b in title_lower for b in ["chrome", "edge", "firefox", "brave"]):
            page = title.split(" - ")[0].strip() if " - " in title else title
            if len(page) > 5:
                return f"Browsing: '{page}'"
        
        return ""
    
    def add_file_event(self, filepath: str):
        """Log a file creation/modification event."""
        import os
        basename = os.path.basename(filepath)
        with self._lock:
            self.history.append({
                "time": time.strftime("%H:%M:%S"),
                "action": f"Modified file: '{basename}'"
            })
    
    def add_terminal_command(self, command: str):
        """Log a terminal command."""
        with self._lock:
            self.history.append({
                "time": time.strftime("%H:%M:%S"),
                "action": f"Ran command: '{command}'"
            })
    
    def get_activity_summary(self) -> str:
        """Return a formatted summary of recent activities for the LLM."""
        with self._lock:
            if not self.history:
                return "No recent activity detected."
            
            lines = []
            for entry in self.history:
                lines.append(f"[{entry['time']}] {entry['action']}")
            
            return "\n".join(lines)
    
    def get_latest_activity(self) -> str:
        """Return just the most recent activity."""
        with self._lock:
            if self.history:
                return self.history[-1]["action"]
            return ""


# Global singleton
tracker = ActivityTracker()
