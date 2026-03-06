from functools import wraps
from shutil import which
from subprocess import CalledProcessError, run
from sys import platform
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


class SetxNotFound(FileNotFoundError):
    """Raised when `setx` is not found in the PATH."""


class SetxWriteError(RuntimeError):
    """Raised when `setx` failed to update USER env."""


def win32(func: Callable[P, R]) -> Callable[P, R]:
    """Decorator to restrict a function to Windows platforms only.

    Args:
        func: The function to be decorated.

    Returns:
        A wrapper that checks the platform before calling the function.

    Raises:
        OSError: If the platform is not Windows.
    """
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        if platform != "win32":
            raise OSError(f"{func.__qualname__} is a windows-only function.")
        return func(*args, **kwargs)

    return wrapper

class UserEnv:
    """A class for managing user environment variables on Windows using `setx`."""
    @win32
    def __init__(self) -> None:
        """Initialize the UserEnv instance and verify setx availability.

        Raises:
            SetxNotFound: If the `setx` command is not found in PATH.
        """
        self._ensure_setx()

    def _ensure_setx(self):
        """Check if setx command is available in PATH.

        Raises:
            SetxNotFound: If the `setx` command is not found in PATH.
        """
        if not which("setx"):
            raise SetxNotFound("`setx` not found. Cannot manage USER env without setx.")

    def set_user_env(self, key: str, value: str):
        """Set a user environment variable using setx.
        Args:
            key: The environment variable name.
            value: The value to set the variable to.

        Raises:
            CalledProcessError: If the setx command fails to execute.
        """
        run(["setx", key, value], check=True, capture_output=True)

    @classmethod
    def setx(cls, key: str, value: str):
        """Set a user environment variable using the class method interface.

        Args:
            key: The environment variable name.
            value: The value to set the variable to.

        Raises:
            SetxWriteError: If the environment variable fails to be set.
            CalledProcessError: If the underlying subprocess command fails.
        """
        try:
            cls().set_user_env(key, value)
        except (CalledProcessError, Exception) as e:
            raise SetxWriteError(
                f"Failed to set '{key}={value}' in USER env as a result of above error."
            ) from e
