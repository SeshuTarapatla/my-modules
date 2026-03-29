"""WSL (Windows Subsystem for Linux) utility functions.

This module provides utilities for interacting with WSL environments,
including network configuration and IP address retrieval.
"""

from subprocess import check_output

def get_wsl_ip() -> str:
    """Get the IP address of the default WSL network interface.

    Retrieves the IP address of the default network interface in WSL
    by executing the 'wsl ip route show default' command and parsing
    the output.

    Returns:
        str: The IP address of the default WSL network interface.

    Raises:
        subprocess.CalledProcessError: If the WSL command fails to execute.
        IndexError: If the command output format is unexpected and parsing fails.
    """
    response = check_output(["wsl", "ip", "route", "show", "default"], text=True)
    return response.split()[2]