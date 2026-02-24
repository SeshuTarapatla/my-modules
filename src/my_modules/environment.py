from sys import platform


def is_win32(strict: bool = False) -> bool:
    if platform == "win32":
        return True
    if strict:
        raise EnvironmentError("Not a valid win32 environment.")
    else:
        return False
