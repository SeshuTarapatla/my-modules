__all__ = ["Telegram"]

from dataclasses import dataclass
from os import getenv
from typing import AsyncGenerator, Literal, cast, overload

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.channels import CreateChannelRequest
from telethon.tl.patched import Message
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


class ChannelNotFound(Exception): ...


class TelegramMessage(Message):
    def __str__(self):
        return f"TelegramMessage(text='{self.text}', channel='{self.chat.title if isinstance(self.chat, Channel) else 'unknown'}', id={self.id})"

    def __repr__(self) -> str:
        return str(self)


class TelegramChannel(Channel):
    def __init__(self, client: "Telegram", *args, **kwargs):
        self.client = client
        super().__init__(*args, **kwargs)

    async def iter_messages(self) -> AsyncGenerator[TelegramMessage, None]:
        async for message in self.client.iter_messages(self, reverse=True, offset_id=1):
            message.__class__ = TelegramMessage
            yield message

    async def count(self) -> int:
        messages = await self.client.get_messages(self, limit=0)
        return messages.__getattribute__("total") - 1

    def __str__(self) -> str:
        return f"TelegramChannel(title='{self.title}', id={self.id})"

    def __repr__(self) -> str:
        return str(self)


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

    @overload
    async def get_channel(
        self, title: str, strict: Literal[False] = False
    ) -> TelegramChannel | None: ...

    @overload
    async def get_channel(
        self, title: str, strict: Literal[True]
    ) -> TelegramChannel: ...

    async def get_channel(
        self, title: str, strict: bool = False
    ) -> TelegramChannel | None:
        for archived in (False, True):
            async for dialog in self.iter_dialogs(archived=archived):
                if isinstance(dialog.entity, Channel) and dialog.title == title:
                    return TelegramChannel(self, **dialog.entity.__dict__)
        if strict:
            raise ChannelNotFound(f"No channel found with title='{title}'")

    async def create_channel(
        self, title: str, *, about: str = "", broadcast: bool = True
    ) -> TelegramChannel:
        request = CreateChannelRequest(title=title, about=about)
        if broadcast:
            request.broadcast = True
        else:
            request.megagroup = True
        result = cast(Updates, await self(request))
        return TelegramChannel(self, **result.chats[0].__dict__)
