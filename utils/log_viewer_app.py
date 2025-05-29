import json
from utils.logger import get_logs
from utils.log_viewer_gui import LogViewerGUI

class LogViewerApp(LogViewerGUI):
    def __init__(self, master=None):
        super().__init__(master)
        self.load_and_display_logs()

    def load_and_display_logs(self):
        logs = get_logs()
        formatted_logs = self.format_logs(logs)
        self.display_logs(formatted_logs)

    def format_logs(self, logs):
        formatted_text = []
        for log_entry in logs:
            timestamp = log_entry.get("timestamp", "N/A")
            action = log_entry.get("action", "N/A")
            user_id = log_entry.get("user_id", "N/A")
            data_before = log_entry.get("data_before")
            data_after = log_entry.get("data_after")

            formatted_text.append(f"Timestamp: {timestamp}")
            formatted_text.append(f"Action: {action}")
            formatted_text.append(f"User ID: {user_id}")
            if data_before:
                formatted_text.append(f"  Data Before: {json.dumps(data_before, indent=2, ensure_ascii=False)}")
            if data_after:
                formatted_text.append(f"  Data After: {json.dumps(data_after, indent=2, ensure_ascii=False)}")
            formatted_text.append("-" * 50) # Separator

        return "\n".join(formatted_text)

if __name__ == "__main__":
    # This part is for testing the LogViewerApp independently
    import customtkinter as ctk
    root = ctk.CTk()
    root.withdraw() # Hide the main root window
    app = LogViewerApp(root)
    root.mainloop()
