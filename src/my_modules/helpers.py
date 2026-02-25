from datetime import datetime
from inspect import isawaitable
from typing import Any


async def handle_await(object: Any) -> Any:
    return (await object) if isawaitable(object) else object


def now() -> datetime:
    return datetime.now().replace(microsecond=0)
