"""Helper functions module.

This module provides utility functions for handling async operations.
"""

__all__: list[str] = ["handle_await"]

from inspect import isawaitable
from typing import Any, Awaitable, TypeVar, overload

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
