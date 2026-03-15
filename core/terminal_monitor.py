import subprocess
import logging

def get_last_terminal_command() -> str:
    """Retrieve the last command executed in the terminal (Windows DOSKey history)."""
    try:
        # Check command history using doskey
        history = subprocess.check_output(
            "doskey /history",
            shell=True,
            stderr=subprocess.DEVNULL
        ).decode(errors="replace")
        
        commands = history.split("\n")
        
        # Last element is usually empty string due to trailing newline, so take -2
        if commands and len(commands) > 1:
            cmd = commands[-2].strip()
            if cmd:
                return cmd
    except Exception as e:
        # Usually fails if doskey isn't tracking or shell differs
        pass
        
    return "No command"
