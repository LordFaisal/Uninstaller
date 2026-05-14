# core/uninstaller.py

"""
Handles execution of uninstall commands retrieved from the Windows Registry.

This module is intentionally kept separate from registry.py because:
- Reading registry data is a separate concern from executing commands
- Makes it easy to test logging/display without risking real uninstalls
- subprocess logic may grow (timeouts, retries) without touching registry code
"""

import subprocess
from typing import Optional

from config import DRY_RUN, STATUS_SUCCESS, STATUS_FAILED, STATUS_DRY_RUN, STATUS_ERROR
from core.logger import log_action


def uninstall_app(app: dict) -> Optional[bool]:
    """
    Attempt to uninstall the given application.

    Return values have three meanings:
        True  → uninstall succeeded (or was simulated in DRY_RUN mode)
        False → uninstall was attempted but failed
        None  → user cancelled — no attempt was made

    Args:
        app: App dictionary from get_installed_apps().

    Returns:
        True, False, or None as described above.
    """
    name = app["name"]
    uninstall_string = app["uninstall_string"]

    # --- DRY RUN MODE ---
    # Simulate the uninstall without executing anything.
    # Safe for testing — logs the action but touches nothing.
    if DRY_RUN:
        print(f"[DRY RUN] Would uninstall: {name}")
        print(f" [DRY RUN] Command: {uninstall_string}")
        log_action(name, uninstall_string, STATUS_DRY_RUN)
        return True  # Simulate success in dry run mode
    
    # --- USER CONFIRMATION ---
    # Uninstalling is irreversible. Always require explicit confirmation.
    # We accept only "yes" — not "y", not "Y", not "YES".
    # Deliberate strictness: accidental presses shouldn't uninstall software.
    print(f"\n ⚠ WARNING: this will permanently uninstall {name}!")
    print(f" This action cannot be undone.")
    confirm = input(" Type 'yes' to confirm, anything else to cancel: ").strip().lower()

    # if user doesn't type "yes", cancel the uninstall
    if confirm != "yes":
        print(" Cancelled.")
        log_action(name, uninstall_string, STATUS_FAILED)
        return None  # ← None means "user chose not to proceed" — not a failure
    
    # --- EXECUTE UNINSTALL ---
    print(f"\n Running uninstaller for {name}...")
    print(f" Command: {uninstall_string}\n")

    try:
        result = subprocess.run(
            uninstall_string,       # The exact commant string from the registry
            shell=True,             # Let Windows parse and execute the full string
            capture_output=True,    # Capture stdout/stderr so we can log errors
            text=True               # Return output as string not raw bytes
        )

        # returncode 0 = success by universal convention
        if result.returncode == 0:
            print(f" ✓ Successfully uninstalled {name}!")
            log_action(name, uninstall_string, STATUS_SUCCESS)
            return True
        else:
            print(f" ✗ Uninstall failed for {name}!")
            # Only show first 200 chars — error messages can be very long
            if result.stderr:
                print(f"  Error: {result.stderr[:200]}")
            log_action(name, uninstall_string, STATUS_FAILED)
            return False

    
    except Exception as e:
        # Something unexpected happened — subprocess couldn't even start
        # e.g. the uninstall executable is missing from disk
        print(f" ✗ Unexpected error: {e}")
        log_action(name, uninstall_string, STATUS_ERROR)
        return False