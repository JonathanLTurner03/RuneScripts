import os
import logging
import time

# Sets logged up to INFO level by default
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Checks if the current user is root
def check_root() -> bool:
    if os.getuid() == 0:
        return True
    return False

# Attempts to elevate privileges using sudo
def elevate_privileges() -> None:
    if not check_root():
        logging.info("Elevating privileges with sudo...")
        os.execvp("sudo", ["sudo"] + ["python3"] + os.sys.argv)
    else:
        logging.debug("Running as root...")

# Creates a directory if it does not exist
def create_directory(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)
        logging.debug(f"Created directory: {path}")
    else:
        logging.debug(f"Directory already exists: {path}")

# Sets executable permissions for a given file
def set_executable(file_path: str) -> None:
    os.chmod(file_path, os.stat(file_path).st_mode | 0o111)
    logging.debug(f"Set executable permissions for: {file_path}")

# Creates a symbolic link
def create_symlink(target: str, link_name: str) -> None:
    try:
        if os.path.islink(link_name) or os.path.exists(link_name):
            os.remove(link_name)
        os.symlink(target, link_name)
        logging.debug(f"Created symlink: {link_name} -> {target}")
    except Exception as e:
        logging.error(f"Failed to create symlink {link_name} -> {target}: {e}")

# Removes a file or directory
def remove_path(path: str) -> None:
    try:
        if os.path.isdir(path):
            os.rmdir(path)
        elif os.path.isfile(path):
            os.remove(path)
        logging.debug(f"Removed: {path}")
    except Exception as e:
        logging.error(f"Failed to remove {path}: {e}")

# Checks if a path exists
def path_exists(path: str) -> bool:
    return os.path.exists(path)

# Joins multiple path components
def join_paths(*paths: str) -> str:
    return os.path.join(*paths)

# Gets the absolute path of a given path
def get_absolute_path(path: str) -> str:
    return os.path.abspath(path)

# Changes the current working directory
def change_directory(path: str) -> None:
    os.chdir(path)
    logging.debug(f"Changed directory to: {path}")

#Gets the current working directory
def get_current_directory() -> str:
    cwd = os.getcwd()
    logging.debug(f"Current directory: {cwd}")
    return cwd