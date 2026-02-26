__all__ = ["Telegram"]

from dataclasses import dataclass
from os import getenv
from typing import cast

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.channels import CreateChannelRequest
from telethon.types import Channel, Updates

from my_modules.helpers import handle_await


class StrSession(StringSession):
    def __str__(self) -> str:
        return self.save()


@dataclass
class TelegramEnv:
    TELEGRAM_API_ID: int = int(getenv("TELEGRAM_API_ID", 0))
    TELEGRAM_API_HASH: str = getenv("TELEGRAM_API_HASH", "")
    TELEGRAM_SESSION: StrSession = StrSession(getenv("TELEGRAM_SESSION", ""))
    TELEGRAM_NUMBER: str = getenv("TELEGRAM_NUMBER", "")

    def __post_init__(self):
        if not any(
            (
                self.TELEGRAM_API_ID,
                self.TELEGRAM_API_HASH,
                self.TELEGRAM_SESSION,
                self.TELEGRAM_NUMBER,
            )
        ):
            raise EnvironmentError(
                "Telegram session variables are not found in the environment."
            )

    def items(self):
        for key, value in self.__dict__.items():
            yield key, value


class Telegram(TelegramClient):
    def __init__(self):
        t_env = TelegramEnv()
        self.phone_number = t_env.TELEGRAM_NUMBER
        self.session: StringSession = t_env.TELEGRAM_SESSION
        super().__init__(
            t_env.TELEGRAM_SESSION, t_env.TELEGRAM_API_ID, t_env.TELEGRAM_API_HASH
        )

    async def start(self):  # type: ignore[override]
        _start = super().start(self.phone_number)
        return await handle_await(_start)

    async def test_connection(self) -> bool:
        try:
            return bool(await self.start())
        except Exception:
            return False

    async def get_channel(self, title: str) -> Channel | None:
        for archived in (False, True):
            async for dialog in self.iter_dialogs(archived=archived):
                if isinstance(dialog.entity, Channel) and dialog.title == title:
                    return dialog.entity

    async def create_channel(
        self, title: str, *, about: str = "", broadcast: bool = True
    ) -> Channel:
        request = CreateChannelRequest(title=title, about=about)
        if broadcast:
            request.broadcast = True
        else:
            request.megagroup = True
        result = cast(Updates, await self(request))
        return cast(Channel, result.chats[0])
