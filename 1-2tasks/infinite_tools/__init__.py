"""Infinite Tools Package - KPI Practical Tasks"""

__version__ = "0.4.0"

from .generators import fibonacci_generator, color_cycle_generator, round_robin_generator
from .timeout import timeout_iterator
from .memoization import memoize

# таск 4
from .priority_queue import BiDirectionalPriorityQueue, create_priority_queue

__all__ = [
    # таск 1-2
    "fibonacci_generator", "color_cycle_generator", "round_robin_generator",
    "timeout_iterator",
    # таск 3
    "memoize",
    # таск 4
    "BiDirectionalPriorityQueue", "create_priority_queue",
    # таск 5
    "async_map", "callback_async_map", "async_map_with_abort",
    # таск 6
    "large_data_stream", "process_stream",
    # таск 7
    "EventEmitter", "Subscription",
    # таск 8
    "AuthProxy", "ApiKeyStrategy", "BearerTokenStrategy",
]
# таск 5
from .async_array import async_map, callback_async_map, async_map_with_abort
# таск 6
from .stream_processor import large_data_stream, process_stream
# таск 7
from .event_emitter import EventEmitter, Subscription
# таск 8
from .auth_proxy import AuthProxy, ApiKeyStrategy, BearerTokenStrategy