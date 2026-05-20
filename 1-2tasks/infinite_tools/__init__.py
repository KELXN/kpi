"""Infinite Tools Package - KPI Practical Tasks"""

__version__ = "0.4.0"

from .generators import fibonacci_generator, color_cycle_generator, round_robin_generator
from .timeout import timeout_iterator
from .memoization import memoize

# Task 4
from .priority_queue import BiDirectionalPriorityQueue, create_priority_queue

__all__ = [
    # Task 1-2
    "fibonacci_generator", "color_cycle_generator", "round_robin_generator",
    "timeout_iterator",
    # Task 3
    "memoize",
    # Task 4
    "BiDirectionalPriorityQueue", "create_priority_queue",
    #task 5
    "async_map", "callback_async_map", "async_map_with_abort"
]
from .async_array import async_map, callback_async_map, async_map_with_abort