# config.py
import os
import sys

# When packaged as exe, sys.executable points to the exe location.
# When run as a script, __file__ points to config.py.
# This ensures logs always appear next to the executable/script.
if getattr(sys, 'frozen', False):
    # Running as compiled exe
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Running as normal Python script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOG_FILE_PATH: str = os.path.join(BASE_DIR, "logs", "uninstall_log.txt")

APP_NAME: str = "WinUninstaller"
APP_VERSION: str = "1.0.0"

DRY_RUN: bool = True

# --- Uninstall Status Constants ---
STATUS_SUCCESS: str = "SUCCESS"
STATUS_FAILED: str  = "FAILED"
STATUS_DRY_RUN: str = "DRY-RUN"
STATUS_ERROR: str   = "ERROR"
APPS_PER_PAGE: int = 20