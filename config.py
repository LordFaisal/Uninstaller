# config.py

"""
Global configuration settings for the WinUninstaller.
"""

# --- App Info ---
APP_NAME: str = "WinUninstaller"
APP_VERSION: str = "1.0.0"

# --- File Paths ---
LOG_FILE_PATH: str = "logs/uninstall_log.txt"

# --- Behavior Settings ---
DRY_RUN: bool = False # If True, simulate uninstalls without actually running them