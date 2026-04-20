from socket import create_connection
from time import sleep

from my_modules.datetime_utils import Timestamp
from my_modules.logger import get_logger

log = get_logger(__name__)


class Internet:
    def __init__(
        self, host: str = "1.1.1.1", port: int = 80, timeout: float = 3.0
    ) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout

    @property
    def is_active(self) -> bool:
        try:
            with create_connection((self.host, self.port), timeout=self.timeout):
                return True
        except Exception:
            return False

    def wait_for_network(self):
        if not self.is_active:
            log.error("Internet disconnected. Pausing till network is back.")
            started_at = Timestamp()
            while not self.is_active:
                sleep(1)
            log.info(f"Internet is back. Disconnected for {Timestamp() - started_at}.")
