import asyncio
from typing import Callable, TypeVar, List, Awaitable, Any
from asyncio import AbstractEventLoop

T = TypeVar('T')
R = TypeVar('R')


async def async_map(func: Callable[[T], Awaitable[R] | R], iterable: List[T]) -> List[R]:
    """Асинхронна версія map з підтримкою async функцій"""
    if asyncio.iscoroutinefunction(func):
        return await asyncio.gather(*(func(item) for item in iterable))
    else:
        return await asyncio.to_thread(lambda: [func(item) for item in iterable])


def callback_async_map(func: Callable, iterable: List[T], callback: Callable[[List[R]], None]) -> None:
    """Callback-style асинхронний map"""
    async def _run():
        result = await async_map(func, iterable)
        callback(result)
    
    asyncio.run(_run())

async def async_map_with_abort(
    func: Callable, 
    iterable: List[T], 
    abort_event: asyncio.Event
) -> List[R]:
    """Асинхронний map з можливістю скасування"""
    tasks = []
    for item in iterable:
        if abort_event.is_set():
            break
        task = asyncio.create_task(asyncio.to_thread(func, item) if not asyncio.iscoroutinefunction(func) else func(item))
        tasks.append(task)
    
    return await asyncio.gather(*tasks, return_exceptions=True)


def create_async_map():
    return async_map