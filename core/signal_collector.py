import psutil
import time
import logging
from core.terminal_monitor import get_last_terminal_command
from core.file_monitor import get_last_modified_file
from detectors.llm_detector import detect_llm_sites

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# -------------------------------
# GET ACTIVE APPLICATIONS
# -------------------------------
def get_active_apps() -> list[str]:
    """Retrieve a list of currently running application names safely."""
    apps = []
    
    for proc in psutil.process_iter(['name']):
        try:
            name = proc.info.get('name')
            if name:
                apps.append(name.lower())
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
            
    return apps


# -------------------------------
# COLLECT SIGNALS
# -------------------------------
def collect_signals() -> dict:
    """Collect system signals like running apps and timestamps."""
    signals = {}
    
    try:
        apps = get_active_apps()
        
        # Check for common applications securely
        signals["vscode_open"] = any("code.exe" in app or "code" in app for app in apps)
        signals["browser_open"] = any(browser in app for app in apps for browser in ["chrome.exe", "msedge.exe", "brave.exe", "firefox.exe"])
        
        signals["terminal_command"] = get_last_terminal_command()
        signals["last_file"] = get_last_modified_file()
        signals["llm_sites"] = detect_llm_sites()
        
        signals["timestamp"] = time.time()
        
    except Exception as e:
        logging.error(f"Error collecting signals: {e}")
        signals["vscode_open"] = False
        signals["browser_open"] = False
        signals["terminal_command"] = "Error"
        signals["last_file"] = "Error"
        signals["llm_sites"] = []
        signals["timestamp"] = time.time()
        
    return signals
