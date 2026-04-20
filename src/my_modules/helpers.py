"""Helper functions module.

This module provides utility functions for handling async operations.
"""

__all__: list[str] = [
    "handle_await",
    "achain",
]

import asyncio
from inspect import isawaitable
from typing import (
    Any,
    AsyncIterable,
    AsyncIterator,
    Awaitable,
    Callable,
    TypeVar,
    overload,
)

T = TypeVar("T")


@overload
async def handle_await(object: T) -> T: ...


@overload
async def handle_await(object: Awaitable[T]) -> T: ...


async def handle_await(object: Any) -> Any:
    """Handle awaitable objects by awaiting them if they are awaitable, otherwise return as-is.

    This function checks if the input object is awaitable (coroutine, async function, etc.)
    and awaits it if so. If the object is not awaitable, it returns the object unchanged.

    Args:
        object: The object to handle. Can be any type, including awaitable objects.

    Returns:
        The result of awaiting the object if it's awaitable, otherwise the original object.

    Examples:
        >>> import asyncio
        >>> async def get_value():
        ...     return 42
        ...
        >>> async def main():
        ...     # Handle awaitable
        ...     result1 = await handle_await(get_value())
        ...     print(result1)  # Output: 42
        ...
        ...     # Handle non-awaitable
        ...     result2 = await handle_await(42)
        ...     print(result2)  # Output: 42
        ...
        >>> asyncio.run(main())
    """
    return await object if isawaitable(object) else object


@overload
def achain(*async_iterables: AsyncIterable[T]) -> AsyncIterator[T]: ...


@overload
def achain(*async_iterables: AsyncIterable[Any]) -> AsyncIterator[Any]: ...


async def achain(*async_iterables: AsyncIterable[Any]) -> AsyncIterator[Any]:
    """Chain multiple async iterables into a single async iterator.

    Yields items from each async iterable in sequence, moving to the next
    iterable only after the current one is exhausted.

    Args:
        *async_iterables: Zero or more async iterables to chain together.

    Yields:
        Items from each async iterable in the order they were provided.

    Examples:
        >>> import asyncio
        >>> async def async_range(start: int, stop: int):
        ...     for i in range(start, stop):
        ...         yield i
        ...
        >>> async def main():
        ...     async for item in achain(async_range(0, 3), async_range(3, 6)):
        ...         print(item)  # Output: 0, 1, 2, 3, 4, 5
        ...
        >>> asyncio.run(main())
    """
    for iterable in async_iterables:
        async for item in iterable:
            yield item


def handle_async(func: Callable):
    try:
        loop = asyncio.get_running_loop()
    except Exception:
        return asyncio.run(func())
    else:
        return loop.create_task(func())
