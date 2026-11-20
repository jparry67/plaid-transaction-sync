"""Application entry point."""

import threading
import subprocess
import sys

def start_app():
    subprocess.run([sys.executable, "app/app.py"])

app_thread = threading.Thread(target=start_app)
app_thread.daemon = True
app_thread.start()
app_thread.join()
print("App started on port 4343")
