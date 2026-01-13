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