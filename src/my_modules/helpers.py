from datetime import datetime
from inspect import isawaitable
from typing import Any, Literal, overload


async def handle_await(object: Any) -> Any:
    return (await object) if isawaitable(object) else object


@overload
def now(text: Literal[False] = False, strf: str = "%Y%m%d-%H%M%S") -> datetime: ...


@overload
def now(text: Literal[True], strf: str = "%Y%m%d-%H%M%S") -> str: ...


def now(text: bool = False, strf: str = "%Y%m%d-%H%M%S") -> datetime | str:
    dt = datetime.now().replace(microsecond=0)
    return dt.strftime(strf) if text else dt
