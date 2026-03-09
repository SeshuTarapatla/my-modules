from datetime import datetime

def now() -> datetime:
    """Get the current datetime without microseconds.

    Returns:
        datetime: The current datetime with microseconds set to 0.
    """
    return datetime.now().replace(microsecond=0)