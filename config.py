# config.py

APP_NAME: str = "WinUninstaller"
APP_VERSION: str = "1.0.0"

LOG_FILE_PATH: str = "logs/uninstall_log.txt"

DRY_RUN: bool = True

# --- Uninstall Status Constants ---
STATUS_SUCCESS: str = "SUCCESS"
STATUS_FAILED: str  = "FAILED"
STATUS_DRY_RUN: str = "DRY-RUN"
STATUS_ERROR: str   = "ERROR"
APPS_PER_PAGE: int = 20