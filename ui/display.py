# ui/display.py

"""
Hanldes all terminal display and formatting for WinUninstaller.

Why seperate from core/?
Display logic changes often (column widths, colors, layout).
Keeping it isolated means we can redesign the UI without
touching any business logic in core/.
"""


import math
from config import APP_NAME, APP_VERSION

# --- Layout Constants ---
# Defining column widths as constants means changing the layout
# requires editing ONE number, not hunting through print statements.
APPS_PER_PAGE = 20
COL_NUM = 5
COL_NAME = 45
COL_VERSION = 20
COL_PUBLISHER = 30

def truncate(text: str, max_width: int) -> str:
    """Truncate a string to max_width, addind '...; if cut short.
    
    Args:
        text: The string to truncate.
        max_width: Maximum allowed character width.
        
    Retrurns:
        Original strig if short enough, otherwise truncated with '...'
    """
    if len(text) <= max_width:
        return text
    return text[:max_width - 3] + "..."
    # Note: no 'else' needed here. The 'if' return early,
    # so anything after it only runs when the condition is False.


def print_header() -> None:
    """
    Print the application title banner.
    
    Why a separate function?
    We'll call this in multiple places (startup, after clearing screen, etc).
    One function means one place to update the design.
    """
    width = 60
    print("\n" + "—" * width)
    print(f" {APP_NAME} v{APP_VERSION}".center(width))
    print("—" * width + "\n")


def display_apps(apps: list[dict], page: int) -> None:
    """
    Display one page of installed apps as formatted table.
    
    Args:
        apps: Full list of app dictionaries from the registry.
        page: The page number to display (starts at 1).
        
    Returns:
        None. This function only prints to the terminal.
    """
    
    
    
    # --- Pagination Calculations ---
    total_pages = math.ceil(len(apps) / APPS_PER_PAGE)

    # Gaurd against invalid page numbers
    # This prevents crashes if someone passes page=0 or page = 999
    if page < 1:
        page = 1
    if page > total_pages:
        page = total_pages

    start = (page - 1) * APPS_PER_PAGE
    end = start + APPS_PER_PAGE
    page_apps = apps[start:end]

    # --- Page Info Line ---
    print(f"  Showing page {page} of {total_pages} | Total installed apps: {len(apps)}\n")

    # --- Column Headers ---
    # f-string alignment: {value:<width} = left-align in 'width' characters
    print(f" {'#':<{COL_NUM}} {'Name':<{COL_NAME}} {'Version':<{COL_VERSION}} {'Publisher':<{COL_PUBLISHER}}")

    # --- Divider Line ---
    # '-' * width creates a line of that many dash characters
    print(f" {'─'*COL_NUM} {'─'*COL_NAME} {'─'*COL_VERSION} {'─'*COL_PUBLISHER}")


    # --- App Rows ---
    for i, app in enumerate(page_apps):
        # Real number across all pages: page 2 starts at 21, not 1
        number = start + i + 1

        # Safely handle None values before truncating
        # We must handle None BEFORE truncate() because
        # len(None) would crash ─ None has no length
        name = truncate(app["name"], COL_NAME - 1)
        version = truncate(app["version"] or "N/A", COL_VERSION - 1)
        publisher = truncate(app["publisher"] or "N/A", COL_PUBLISHER - 1)

        print(f" {number:<{COL_NUM}} {name:<{COL_NAME}} {version:<{COL_VERSION}} {publisher:<{COL_PUBLISHER}}")
    
    # --- Footer ---
    print(f"\n {'─'*60}")
    print(f" Page {page}/{total_pages} | [n] Next [p] Previous [q] Quit")
    print(f" {'─'*60}\n")

    