from datetime import datetime
from typing import Literal


def now() -> datetime:
    """Get the current datetime without microseconds.

    Returns:
        datetime: The current datetime with microseconds set to 0.
    """
    return datetime.now().replace(microsecond=0)


class Timestamp(datetime):
    """A Timestamp class that inherits from datetime with microseconds set to 0"""

    def __new__(cls):
        """Create a new Timestamp instance"""
        current_time = datetime.now().replace(microsecond=0)
        return super(Timestamp, cls).__new__(
            cls,
            current_time.year,
            current_time.month,
            current_time.day,
            current_time.hour,
            current_time.minute,
            current_time.second,
            0,
            current_time.tzinfo,
        )

    def __str__(self) -> str:
        """Return string representation of timestamp in YYYY-MM-DD HH:MM:SS format.

        Returns:
            str: Timestamp formatted as 'YYYY-MM-DD HH:MM:SS'.
        """
        return self.strftime("%Y-%m-%d %H:%M:%S")

    def __repr__(self) -> str:
        """Return official string representation of Timestamp object for debugging.

        Returns:
            str: Timestamp object representation formatted as `Timestamp(YYYY-MM-DD HH:MM:SS)`.
        """
        return f"Timestamp({self.strftime('%Y-%m-%d %H:%M:%S')})"

    def strftime(self, format: Literal["underscore", "hyphen", "nospace"] | str = "nospace") -> str:
        """Format timestamp using predefined or custom format strings.

        Args:
            format: Format string or one of the predefined formats:
                - "underscore": YYYYMMDD_HHMMSS
                - "hyphen": YYYYMMDD-HHMMSS
                - "nospace": YYYYMMDDHHMMSS
                - Any valid strftime format string

        Returns:
            str: Formatted timestamp string according to specified format.

        Examples:
            >>> ts = Timestamp()
            >>> ts.strftime("underscore")  # "20240115_123045"
            >>> ts.strftime("hyphen")     # "20240115-123045"
            >>> ts.strftime("nospace")    # "20240115123045"
            >>> ts.strftime("%d-%m-%Y")   # "15-01-2024"
        """
        match format:
            case "underscore":
                format = "%Y%m%d_%H%M%S"
            case "hyphen":
                format = "%Y%m%d-%H%M%S"
            case "nospace":
                format = "%Y%m%d%H%M%S"
            case _:
                pass
        return super().strftime(format)
