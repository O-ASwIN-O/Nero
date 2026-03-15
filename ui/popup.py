import logging
import tkinter as tk

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# -------------------------------
# SHOW PREDICTION (FLOATING UI)
# -------------------------------
def show_prediction(predictions: str, context: str = ""):
    """Display predictions in a floating Tkinter window."""
    try:
        window = tk.Tk()
        window.title("Nero Prompt Suggestions")
        
        # Make the window float on top
        window.attributes("-topmost", True)
        window.geometry("450x250")
        
        # Modern subtle styling
        window.configure(bg="#1E1E1E")
        
        # Title label
        title_label = tk.Label(
            window,
            text="Nero Prompt Suggestions",
            font=("Segoe UI", 12, "bold"),
            fg="#00D2FF",
            bg="#1E1E1E",
            justify="center"
        )
        title_label.pack(pady=(15, 5))

        # Predictions label
        label = tk.Label(
            window,
            text=predictions,
            font=("Segoe UI", 10),
            fg="#E0E0E0",
            bg="#1E1E1E",
            justify="left",
            wraplength=400
        )
        label.pack(pady=10, padx=20)
        
        # Button Frame to hold both buttons side-by-side
        btn_frame = tk.Frame(window, bg="#1E1E1E")
        btn_frame.pack(pady=(10, 15))

        def copy_to_clipboard():
            window.clipboard_clear()
            
            # Append context to clipboard text so the LLM knows what the prompt refers to
            copied_text = predictions
            if context and context != "Developer just started a session.":
                copied_text += "\n\n--- Context ---\n" + context
                
            window.clipboard_append(copied_text)
            copy_btn.config(text="Copied!")
            window.after(2000, lambda: copy_btn.config(text="Copy to Clipboard"))

        # Copy button
        copy_btn = tk.Button(
            btn_frame,
            text="Copy to Clipboard",
            command=copy_to_clipboard,
            bg="#005C8A",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            activebackground="#007ACC",
            activeforeground="white",
            padx=15,
            pady=5
        )
        copy_btn.pack(side=tk.LEFT, padx=10)

        # Close button
        close_btn = tk.Button(
            btn_frame,
            text="Dismiss",
            command=window.destroy,
            bg="#333333",
            fg="white",
            font=("Segoe UI", 9),
            relief="flat",
            activebackground="#555555",
            activeforeground="white",
            padx=15,
            pady=5
        )
        close_btn.pack(side=tk.LEFT, padx=10)

        window.mainloop()
    except Exception as e:
        logging.error(f"UI Error: {e}")
        print("\n=== Nero Prompt Predictions ===")
        print(predictions)
        print("===============================\n")
