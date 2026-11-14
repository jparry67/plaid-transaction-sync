import threading
import subprocess
import sys

def start_management_app():
    # Run the management app in a separate process
    subprocess.run([sys.executable, "app/manage_accounts_app.py"])

# Start the management app in background
management_thread = threading.Thread(target=start_management_app)
management_thread.daemon = True
management_thread.start()

print("Management app started on port 4343")
