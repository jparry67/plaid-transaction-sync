"""Application entry point."""

import threading
import subprocess
import sys

from accounts_store import load_accounts

def start_management_app():
    subprocess.run([sys.executable, "app/manage_accounts_app.py"])

# Pre-load accounts at startup
load_accounts()

management_thread = threading.Thread(target=start_management_app)
management_thread.daemon = True
management_thread.start()
management_thread.join()
print("Management app started on port 4343")
