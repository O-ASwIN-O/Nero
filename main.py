import logging
import time
import sys
import os
from core.signal_collector import collect_signals
from core.context_builder import build_context
from core.activity_tracker import tracker
from ai.predictor import predict_prompt
from database.db import save_prediction, init_db
from ui.popup import show_prediction
from core.file_monitor import start_file_monitor
import threading

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# -----------------------------------------------
# SINGLE INSTANCE LOCK
# -----------------------------------------------
LOCK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".nero.lock")

def acquire_lock():
    """Ensure only one instance of Nero-AI is running."""
    if os.path.exists(LOCK_FILE):
        logging.error("Another instance of Nero-AI is already running! Exiting.")
        logging.error("If this is a mistake, delete the file: " + LOCK_FILE)
        sys.exit(1)
    with open(LOCK_FILE, 'w') as f:
        f.write(str(os.getpid()))

def release_lock():
    """Remove the lock file on exit."""
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

# Shared state for background predictor
latest_prediction_data = {
    "prompt": "Nero is warming up...",
    "context": ""
}
prediction_lock = threading.Lock()

def background_predictor_loop():
    """Continuously builds context and generates predictions in background."""
    global latest_prediction_data
    
    while True:
        try:
            signals = collect_signals()
            context = build_context(signals)
            new_pred = predict_prompt(context)
            
            with prediction_lock:
                latest_prediction_data = {
                    "prompt": new_pred,
                    "context": context
                }
                
            save_prediction(context, new_pred)
            logging.info("Background prediction refreshed.")
            
            time.sleep(15)
        except Exception as e:
            logging.error(f"Background Predictor Error: {e}")
            time.sleep(15)

def main():
    """Main pipeline for Nero-AI."""
    logging.info("Starting Nero-AI Full Activity Monitor...")
    
    acquire_lock()
    
    try:
        init_db()
        
        # Start all monitors
        start_file_monitor()
        tracker.start()  # Start activity tracking (window titles, searches, etc.)
        
        # Start background prediction thread
        predictor_thread = threading.Thread(target=background_predictor_loop, daemon=True)
        predictor_thread.start()
        
        # Check initial LLM state
        initial_signals = collect_signals()
        llm_was_open = bool(initial_signals.get("llm_sites"))
        popup_shown = False
        
        logging.info("Monitoring all user activity. Waiting for LLM site trigger...")
        
        while True:
            try:
                signals = collect_signals()
                llm_is_open = bool(signals.get("llm_sites"))
                
                # Edge detection: popup when LLM site first opens
                if llm_is_open and not llm_was_open and not popup_shown:
                    site = signals['llm_sites'][0]
                    logging.info(f"LLM Site Detected ({site}). Showing predictions...")
                    
                    with prediction_lock:
                        current_prompt = latest_prediction_data["prompt"]
                        current_context = latest_prediction_data["context"]
                    
                    popup_shown = True
                    show_prediction(current_prompt, current_context)
                    logging.info("Popup dismissed. Resuming monitoring...")
                
                # Reset when user closes LLM sites
                if not llm_is_open:
                    popup_shown = False
                
                llm_was_open = llm_is_open
                time.sleep(1.5)
                
            except KeyboardInterrupt:
                logging.info("Nero-AI manually stopped.")
                break
                
        logging.info("Pipeline execution complete.")
    finally:
        release_lock()

if __name__ == "__main__":
    main()
