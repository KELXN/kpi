import random
from itertools import cycle
from typing import Iterator, Any, List


def fibonacci_generator() -> Iterator[int]:
    """Нескінченна послідовність Фібоначчі"""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


def round_robin_generator(items: List[Any]) -> Iterator[Any]:
    """Round-robin (циклічне повторення списку)"""
    if not items:
        return
    for item in cycle(items):
        yield item


def color_cycle_generator() -> Iterator[str]:
    """Цикл кольорів"""
    colors = ["red", "green", "blue", "yellow", "purple", "orange"]
    return round_robin_generator(colors)


def incremental_counter(start: int = 0) -> Iterator[int]:
    """Зростаючий лічильник"""
    n = start
    while True:
        yield n
        n += 1


def random_int_generator(min_val: int = 1, max_val: int = 100) -> Iterator[int]:
    """Випадкові числа"""
    while True:
        yield random.randint(min_val, max_val)
