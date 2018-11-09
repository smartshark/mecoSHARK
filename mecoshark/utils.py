import sys
import os

def path_sanitize(path):
    # The Windows filesystem is case-insensitive. Convert all paths to
    # lower-case to prevent data inconsistencies
    if os.name == 'nt':
        path = path.lower()

    return path.replace('\\', '/')
def expand_home(path):
    home_folder = os.path.expanduser('~') + "/"
    path = path.replace("~", home_folder) if path.startswith("~") else path
    return path_sanitize(path)
def path_join(path, *paths):
    path = path_sanitize(os.path.join(path, *paths))
    return path
