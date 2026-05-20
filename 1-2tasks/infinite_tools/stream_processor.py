import asyncio
from typing import AsyncIterator

async def large_data_stream(max_value: int = 1_000_000) -> AsyncIterator[int]:
    """Асинхронний потік великих даних без завантаження всього в пам’ять."""
    for i in range(1, max_value + 1):
        await asyncio.sleep(0)
        yield i

async def process_stream(stream: AsyncIterator[int]) -> dict[str, int]:
    """Обробляє стрічку по одному елементу."""
    total = 0
    count = 0
    even_count = 0

    async for item in stream:
        total += item
        count += 1
        if item % 2 == 0:
            even_count += 1

    return {"count": count, "sum": total, "even_count": even_count}