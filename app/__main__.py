"""Application entry point."""

import threading
import subprocess
import sys


def start_management_app():
    subprocess.run([sys.executable, "app/manage_accounts_app.py"])

management_thread = threading.Thread(target=start_management_app)
management_thread.daemon = True
management_thread.start()
management_thread.join()
print("Management app started on port 4343")
