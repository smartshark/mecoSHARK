import sys
import os

def path_sanitize(path):
    return path.replace('\\', '/')
def expand_home(path):
    home_folder = os.path.expanduser('~') + "/"
    path = path.replace("~", home_folder) if path.startswith("~") else path
    return path_sanitize(path)
