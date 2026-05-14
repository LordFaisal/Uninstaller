# main.py

"""
Entry point for WinUninstaller.

This file only coordinates — it imports from other modules and
connects them together. It contains no business logic of its own.
This is called the "thin controller" pattern.
"""

import math
from core.registry import get_installed_apps
from core.uninstaller import uninstall_app
from ui.display import display_apps, print_header
from config import APPS_PER_PAGE


def main() -> None:
    """
    Main entry point for WinUninstaller.
    Coordinates the main loop, user input, and module calls.
    """

    # --- Startup ---
    print_header()
    print("  Scanning installed applications...")

    all_apps = get_installed_apps()   # master list — never modified
    apps     = all_apps               # working list — can be filtered

    print(f"  Found {len(apps)} installed apps.\n")

    current_page = 1

    # --- Main Loop ---
    while True:
        display_apps(apps, current_page)

        choice = input("  Enter command: ").strip().lower()

        # --- Navigation ---
        if choice == "n":
            total_pages = math.ceil(len(apps) / APPS_PER_PAGE)
            if current_page < total_pages:
                current_page += 1
            else:
                print("  Already on last page.")

        elif choice == "p":
            if current_page > 1:
                current_page -= 1
            else:
                print("  Already on first page.")

        # --- Quit ---
        elif choice == "q":
            print("\n  Goodbye!\n")
            break

        # --- Search ---
        elif choice == "s":
            term = input("  Search by name (Enter to clear): ").strip().lower()

            if term == "":
                apps = all_apps      # restore full list
                print(f"  Showing all {len(apps)} apps.")
            else:
                # List comprehension — filter to apps whose name contains term
                apps = [
                    app for app in all_apps
                    if term in app["name"].lower()
                ]

                if len(apps) == 0:
                    print(f"  No apps found matching '{term}'. Restoring full list.")
                    apps = all_apps
                else:
                    print(f"  Found {len(apps)} apps matching '{term}'.")

            current_page = 1  # always reset to page 1 after search

        # --- Select App By Number ---
        elif choice.isdigit():
            number = int(choice)

            # Validate range — catches 0, negatives, and out-of-range
            if number < 1 or number > len(apps):
                print(f"  Invalid number. Enter between 1 and {len(apps)}.")
                continue

            # Lists are 0-indexed, user numbers start at 1
            selected_app = apps[number - 1]

            # Show app details before doing anything
            print(f"\n  Selected:  {selected_app['name']}")
            print(f"  Version:   {selected_app['version']   or 'N/A'}")
            print(f"  Publisher: {selected_app['publisher'] or 'N/A'}")

            # Attempt uninstall — returns True, False, or None
            result = uninstall_app(selected_app)

            if result is True:
                print(f"\n  ✓ {selected_app['name']} was successfully uninstalled.")
                # Remove from both lists so it doesn't reappear
                if selected_app in all_apps:
                    all_apps.remove(selected_app)
                apps = [a for a in apps if a != selected_app]

            elif result is False:
                print(f"\n  ✗ Failed to uninstall {selected_app['name']}.")

            elif result is None:
                print(f"\n  Uninstall cancelled.")

        else:
            print("  Unknown command. Use n/p/s/q or enter an app number.")


if __name__ == "__main__":
    main()