# security/audit_logs.py

from datetime import datetime

def log_access(action, file_name):
    with open("logs/app.log", "a") as f:
        f.write(f"{datetime.now()} | {action} | {file_name}\n")
        