# core/logger.py

"""
Handles logging of uninstall actions to a text file.

Why log at all?
Uninstalling software is irreversible. Keeping a record means the user
can always review what was removed, when, and whether it succeeded.
This is standard practice in any tool that modifies the system state. 
"""

import os
from datetime import datetime
from config import LOG_FILE_PATH


def get_log_path() -> str:
    """
    return the absolute path to the log file.

    Why absolute? Relative paths depend on where Python is run from,
    Absolute paths work regardless of working directory.

    Returns:
        Absolute path to the log file as a string.
    """
    return os.path.abspath(LOG_FILE_PATH)


def _ensure_log_file_exists() -> None:
    """
    Create the logs directory and write a header if the log file is new.
    
    Why a separate function?
    This setup logic would clutter log_action if left inline.
    Extracting it keeps each function focused on one job.
    The underscore prefix marks it as internal - not for outside use.
    """
    # Create logs/ folder if it doean't exist
    # exist_ok=True means don't crash if folder already exists
    os.makedirs(os.path.dirname(get_log_path()), exist_ok=True)

    # Write a header only if the file is brand new
    if not os.path.exists(get_log_path()):
        with open(get_log_path(), "w", encoding="utf-8") as f:
            f.write("=" * 70 + "\n")
            f.write(f" WinUninstaller Log File\n")
            f.write("=" *70 + "\n\n")


def log_action(app_name: str, uninstall_string: str, status: str) -> None:
    """
    Write one uninstall action to the log file.

    Each line records exactly when the action happened, what the result
    was, which app was targeted, and the command that was used.

    Args:
        app_name: Display name of the app (e.g. "Google Chrome").
        uninstall_string: The command that was run (or would be run).
        status: Outcome — one of 'Success', 'Failed', or 'Dry Run'.

    Returns:
        None
    """
    # Always call this first — ensures folder and file exist
    _ensure_log_file_exists()

    # Get the current time for every log entry.
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Status is padded to 7 chars so columns line up in the log file:
    # SUCCESS = 7 chars
    # FAILED  = 6 chars -> padded to 7
    # DRY RUN = 7 chars
    status_padded = status.ljust(7)

    log_line = (
        f"[{timestamp}] {status_padded} | "
        f"{app_name:<40} | "
        f"{uninstall_string}\n"
    )

    # 'a' = append mode — never overwrites existing log entries
    with open(get_log_path(), "a", encoding="utf-8") as f:
        f.write(log_line)

