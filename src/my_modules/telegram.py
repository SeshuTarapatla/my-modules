__all__ = ["Telegram"]

from dataclasses import dataclass
from os import getenv

from telethon import TelegramClient
from telethon.sessions import StringSession

from my_modules.helpers import handle_await


@dataclass
class TelegramEnv:
    api_id: int = int(getenv("TELEGRAM_API_ID", 0))
    api_hash: str = getenv("TELEGRAM_API_HASH", "")
    session: StringSession = StringSession(getenv("TELEGRAM_SESSION", ""))
    phone_number: str = getenv("TELEGRAM_NUMBER", "")

    def __post_init__(self):
        if not any((self.api_id, self.api_hash, self.session, self.phone_number)):
            raise EnvironmentError(
                "Telegram session variables are not found in the environment."
            )


class Telegram(TelegramClient):
    def __init__(self):
        t_env = TelegramEnv()
        self.phone_number = t_env.phone_number
        self.session: StringSession = t_env.session
        super().__init__(t_env.session, t_env.api_id, t_env.api_hash)
    
    async def start(self): # type: ignore[override]
        _start = super().start(self.phone_number)
        return await handle_await(_start)

    async def test_connection(self) -> bool:
        try:
            return bool(await self.start())
        except Exception:
            return False
