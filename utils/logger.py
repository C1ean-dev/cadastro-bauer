import os
import json
from datetime import datetime

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "user_activity.log")

def setup_logging():
    """Ensures the log directory exists."""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

def log_activity(action, user_data_before=None, user_data_after=None, user_id=None):
    """Logs user activity to a file."""
    setup_logging()
    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    log_entry = {
        "timestamp": timestamp,
        "action": action,
        "user_id": user_id,
        "data_before": user_data_before,
        "data_after": user_data_after
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

def get_logs():
    """Reads and returns all logs from the file."""
    setup_logging()
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    logs.append(json.loads(line))
                except json.JSONDecodeError:
                    # Handle malformed lines if any
                    continue
    return logs
