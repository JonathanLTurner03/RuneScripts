import os

# Checks if the current user is root
def check_root() -> bool:
    if os.getuid() == 0:
        return True
    return False

# Attempts to elevate privileges using sudo
def elevate_privileges() -> None:
    if not check_root():
        print("Elevating privileges with sudo...")
        os.execvp("sudo", ["sudo"] + ["python3"] + os.sys.argv)
    else:
        print("Running as root...")

# Creates a directory if it does not exist
def create_directory(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")
    else:
        print(f"Directory already exists: {path}")

# Sets executable permissions for a given file
def set_executable(file_path: str) -> None:
    os.chmod(file_path, os.stat(file_path).st_mode | 0o111)

# Creates a symbolic link
def create_symlink(target: str, link_name: str) -> None:
    try:
        if os.path.islink(link_name) or os.path.exists(link_name):
            os.remove(link_name)
        os.symlink(target, link_name)
        print(f"Created symlink: {link_name} -> {target}")
    except Exception as e:
        print(f"Failed to create symlink {link_name} -> {target}: {e}")

# Removes a file or directory
def remove_path(path: str) -> None:
    try:
        if os.path.isdir(path):
            os.rmdir(path)
        elif os.path.isfile(path):
            os.remove(path)
        print(f"Removed: {path}")
    except Exception as e:
        print(f"Failed to remove {path}: {e}")

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

#Gets the current working directory
def get_current_directory() -> str:
    return os.getcwd()