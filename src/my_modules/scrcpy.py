"""
Scrcpy module for controlling Android device screen mirroring.

This module provides a Scrcpy class that allows you to control scrcpy
(screen copy) functionality for Android devices. Scrcpy is a tool that
enables display and control of Android devices connected via USB or over TCP/IP.

Features:
- Verify scrcpy installation
- Check ADB device connection status
- Start scrcpy sessions with customizable parameters
- Automatic handling of device serial numbers

Requirements:
- scrcpy must be installed and available in PATH
- ADB (Android Debug Bridge) must be properly configured
- At least one Android device must be connected

Usage:
    from my_modules.scrcpy import Scrcpy

    # Start scrcpy with default settings
    scrcpy = Scrcpy()
    scrcpy.start()

    # Start scrcpy for a specific device
    scrcpy = Scrcpy(serial="device_serial_number")
    scrcpy.start()
"""

from shutil import which
from subprocess import DEVNULL, Popen

from adbutils import adb

from my_modules.logger import get_logger

log = get_logger()


class Scrcpy:
    """
    A class for controlling Android device screen mirroring using scrcpy.

    This class provides functionality to verify scrcpy installation, check ADB device
    connection status, and start scrcpy sessions with customizable parameters.

    Attributes:
        serial (str | None): The serial number of the Android device to connect to.
        proc (Popen[bytes] | None): The subprocess handling the scrcpy session.
    """

    def __init__(self, serial: str | None = None) -> None:
        """
        Initialize the Scrcpy instance.

        Args:
            serial (str | None): The serial number of the Android device to connect to.
                                If None, the first available device will be used.
        """
        self.verify_scrcpy_installation()
        self.serial = serial
        self.proc = None

    def verify_scrcpy_installation(self):
        """
        Verify that scrcpy is installed and available in the system PATH.

        This method checks if scrcpy is available in the system PATH. If not found,
        it displays an error message with installation instructions.

        Raises:
            SystemExit: If scrcpy is not found in PATH.
        """
        if which("scrcpy") is None:
            log.error(
                "[bold red]scrcpy[/] is not found in PATH. Install with '[italic yellow]winget install Genymobile.scrcpy[/]'."
            )

    def verify_device_connected(self):
        """
        Verify that an Android device is connected via ADB.

        This method checks if the specified device (by serial) is connected, or if any
        device is connected when no specific serial is provided. If a specific serial
        is not provided, it automatically selects the first available device.

        Raises:
            SystemExit: If no devices are connected or if the specified device is not found.
        """
        devices = adb.device_list()
        if self.serial:
            for device in devices:
                if device.serial == self.serial:
                    return
            log.error(
                f"No adb device is connected with serial: [cyan]{self.serial}[/]",
            )
            exit(1)
        else:
            if devices:
                self.serial = devices[0].serial
                return
            log.error("No adb devices are connected for scrcpy session.")
            exit(1)

    def start(self) -> Popen[bytes]:
        """
        Start a scrcpy session for the connected Android device.

        This method verifies device connection, kills any existing scrcpy process,
        and starts a new scrcpy session with default parameters including:
        - Screen turned off on device
        - Maximum resolution of 1024
        - Stay awake functionality
        - 60 FPS maximum frame rate
        - Custom window positioning and sizing

        Returns:
            Popen[bytes]: The subprocess object handling the scrcpy session.

        Raises:
            SystemExit: If no devices are connected or if scrcpy installation is not verified.
        """
        self.verify_device_connected()
        if self.proc:
            self.proc.kill()
        log.info(
            f"Starting scrcpy session for AdbDevice(serial=[bold green]{self.serial}[/])"
        )
        self.proc = Popen(
            [
                "scrcpy",
                f"--serial={self.serial}",
                "--turn-screen-off",
                "-m1024",
                "--stay-awake",
                "--max-fps=60",
                "--window-x=1",
                "--window-y=45",
                "--window-height=1480",
            ],
            stdout=DEVNULL,
            stderr=DEVNULL,
        )
        return self.proc


if __name__ == "__main__":
    Scrcpy().start()
