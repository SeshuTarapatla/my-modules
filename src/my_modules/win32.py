import ctypes
from os import getenv
from subprocess import check_output
from sys import platform


def snap_window(title: str, x: int, y: int, w: int, h: int):
    """Snap a window to specific coordinates and dimensions.

    This function finds a window by its title and moves/resizes it to the specified
    position and dimensions using Windows API calls.

    Args:
        title: The title of the window to find and snap.
        x: The new x-coordinate for the window's top-left corner.
        y: The new y-coordinate for the window's top-left corner.
        w: The new width of the window.
        h: The new height of the window.

    Returns:
        None

    Raises:
        Exception: If no window is found with the specified title.

    Examples:
        >>> snap_window("Notepad", 100, 100, 800, 600)
        # Moves the Notepad window to position (100, 100) with size 800x600
    """
    user32 = ctypes.windll.user32
    if (hwnd := user32.FindWindowW(None, title)) is None:
        raise Exception(f"No window found with title `{title}`.")
    user32.MoveWindow(hwnd, x, y, w, h, True)


def get_wsl_host_ip() -> str:
    """Get the IP address of the WSL host machine.

    This function retrieves the IP address of the Windows host machine when running
    in WSL (Windows Subsystem for Linux) environment. On Windows systems, it uses
    WSL commands to get the host IP. On other platforms, it looks for the
    WINDOWS_HOST environment variable.

    Returns:
        str: The IP address of the WSL host machine.

    Raises:
        ValueError: If the Windows Host IP is not found in the environment on non-Windows platforms.

    Examples:
        >>> host_ip = get_wsl_host_ip()
        >>> print(f"WSL Host IP: {host_ip}")
        # Outputs something like: WSL Host IP: 172.28.123.45
    """
    if platform == "win32":
        response = check_output(["wsl", "ip", "route", "show", "default"], text=True)
        return response.split()[2]
    else:
        if win_host := getenv("WINDOWS_HOST"):
            return win_host
        raise ValueError("Windows Host IP not found in the environment.")
