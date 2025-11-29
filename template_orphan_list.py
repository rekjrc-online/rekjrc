#!/usr/bin/env python3
import os
import sys

def find_files(root_dir, filename):
    """Recursively find files with a given name."""
    matches = []
    for dirpath, _, files in os.walk(root_dir):
        if filename in files:
            matches.append(os.path.join(dirpath, filename))
    return matches

def find_all_html_files(templates_dir):
    """Recursively find all .html files in templates_dir."""
    html_files = []
    for dirpath, _, files in os.walk(templates_dir):
        for f in files:
            if f.endswith(".html"):
                html_files.append(os.path.join(dirpath, f))
    return html_files

def read_views_files(views_paths):
    """Read all views.py files and return a list of their contents."""
    contents = []
    for path in views_paths:
        with open(path, "r", encoding="utf-8") as f:
            contents.append(f.read())
    return contents

def main():
    project_root = os.getcwd()

    # Check if manage.py exists
    if not os.path.exists(os.path.join(project_root, "manage.py")):
        print("Error: This script must be run from the root of a Django project (where manage.py exists).")
        sys.exit(1)

    # Locate templates directory
    templates_dir = os.path.join(project_root, "templates")
    if not os.path.exists(templates_dir):
        print("Error: No 'templates' directory found in the project root.")
        sys.exit(1)

    # Check for at least one .html file in templates
    html_files = find_all_html_files(templates_dir)
    if not html_files:
        print("Error: No .html files found in templates directory.")
        sys.exit(1)

    # Locate all views.py files
    views_files = find_files(project_root, "views.py")
    if not views_files:
        print("Error: No views.py files found in the project.")
        sys.exit(1)

    # Read all views.py files into memory
    views_contents = read_views_files(views_files)

    # Check each HTML file against all views.py contents
    orphan_html_files = []
    for html_path in html_files:
        html_name = os.path.basename(html_path)
        found = any(html_name in content for content in views_contents)
        if not found:
            orphan_html_files.append(html_path)

    # Output orphan HTML files
    if orphan_html_files:
        print("Orphan .html files (not referenced in any views.py):")
        for f in orphan_html_files:
            print(f)
    else:
        print("All .html files are referenced in views.py.")

if __name__ == "__main__":
    main()
