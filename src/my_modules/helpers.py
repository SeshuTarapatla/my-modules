__all__ = ["handle_await"]

from inspect import isawaitable
from typing import Any, Awaitable, TypeVar, overload

T = TypeVar("T")


@overload
async def handle_await(object: T) -> T: ...


@overload
async def handle_await(object: Awaitable[T]) -> T: ...


async def handle_await(object: Any) -> Any:
    return await object if isawaitable(object) else object
