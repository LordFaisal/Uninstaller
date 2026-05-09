# core/registry.py

"""
Handle all Windows registry interactions for reading installed applications.

Why is this in it's own file?
Because registry logic is complex and may change independetly of the rest
of the app. Isolating it here means other files never need to know HOW
we read the reistry - they just call get_installed_apps() and get data back.
"""

import winreg
from typing import Optional # We'll use this for optional fields

# --- Constants: the two registry locations for installes apps ---
# Why constatns? so if Microsoft ever changes these paths, we fix ONE line.
REGISTRY_PATHS = [
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
    (winreg.HKEY_CURRENT_USER,  r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
]
# Note: WOW6432Node catches 32-bit apps installed on 64-bit Windows systems
# Without it, you'd miss a large chung of installed software!

def _read_value(subkey: winreg.HKEYType, field: str) -> Optional[str]:
    """
    Safely read a single value from an open registry subkey.
    
    Why a helper function?
    because we read many fields (name, version, publisher...) and each
    can be missing. Without this helper, we'd repeat try/except 6 times
    per app. This keeps get_installed_apps() clean and readable.
    
    The underscore prefix (_read_value) is a Python convention meaning:
    "this is an internal helper, not meant to be called from outside this file."

    Args:
        subkey: An open registry key handle.
        field: The name of the value to read (e.g. "DisplayName").

    Returns:
        The value as a string, or None if the field doesn't exist.
    """

    try:
        return winreg.QueryValueEx(subkey, field)[0]
    except (FileNotFoundError, OSError):
        return None # Field simply doean't exist - that's normal


def is_valid_entry(app: dict) -> bool:
    """
    Check whether a registry entry represents a real, uninstallable application.
    
    Why do we need this?
    The registry is messy. Many entries have no DisplayName (system components,
    updates, partial installs). Others have no UninstallString (can't be
    uninstalled programmatically). We filter those out here - not in the
    main loop - so the logic stays clean and testable.
    
    Args:
        app: A dictionary of app properties.
        
    Returns:
        True if the entry is worth showing to the user, False otherwise.
    """
    return bool(app.get("name")) and bool(app.get("uninstall_string"))



def get_installed_apps() -> list[dict]:
    """
    Scan the Windows Registry and return a list of installed applications.

    Checks three registry locations:
    - HKLM standard (64-bit apps and most software)
    - HKLM WOW6432Node (32-bit apps on 64-bit Windows)
    - HKCU (apps installed for the current user only)

    Returns:
        A sorted list of app dictionaries, each conataining:
        - name (str)
        - version (str or None)
        - publisher (str or None)
        - install_date (str or None)
        - size kb (str or None)
        - uninstall_string (str or None)
        - quiet_uninstall_string (str or None)
    """
    installed_apps: list[dict] = []
    seen_names: set[str] = set() # Prevents duplicate entries across registry paths
    


    for root_key, path in REGISTRY_PATHS:
        try:
            with winreg.OpenKey(root_key, path) as key:
                # QueryInfoKey returns (num_subkeys, num_values, last_modified)
                # [0] gives us the subkey count - out loop boundary
                num_subkeys = winreg.QueryInfoKey(key)[0]

                for i in range(num_subkeys):
                    try:
                        subkey_name = winreg.EnumKey(key, i)

                        with winreg.OpenKey(key, subkey_name) as subkey:
                            app = {
                                "name":                     _read_value(subkey, "DisplayName"),
                                "version":                  _read_value(subkey, "DisplayVersion"),
                                "publisher":                _read_value(subkey, "Publisher"),
                                "install_date":             _read_value(subkey, "InstallDate"),
                                "size_kb":                  _read_value(subkey, "EstimatedSize"),
                                "uninstall_string":         _read_value(subkey, "UninstallString"),
                                "quiet_uninstall_string":   _read_value(subkey, "QuietUninstallString"),
                            }
                            
                            # Only keep valid entries we haven't seen before
                            if is_valid_entry(app) and app["name"] not in seen_names:
                                seen_names.add(app["name"])
                                installed_apps.append(app)

                    except OSError:
                        # Individual subkey read failed - skip and continue
                        continue

        except OSError:
            # Entire registry path unavailable (e.g. no permissions) - skip it
            continue

    # Sort alphabetically by name for consistent display
    # key=lambda x: ... means "sort using this function to extract a sort value"
    # .lower() makes it case-insensitive (so "zoom" doens't sort after "Zoom")
    return sorted(installed_apps, key=lambda x: x["name"].lower())