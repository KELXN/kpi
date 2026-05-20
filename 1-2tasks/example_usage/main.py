import asyncio
from infinite_tools.generators import fibonacci_generator, color_cycle_generator
from infinite_tools.timeout import timeout_iterator
from infinite_tools.memoization import memoize
from infinite_tools.priority_queue import BiDirectionalPriorityQueue
from infinite_tools.async_array import async_map, callback_async_map, async_map_with_abort
from infinite_tools.event_emitter import EventEmitter
import time
from infinite_tools.stream_processor import large_data_stream, process_stream


def main():
    print("=== Infinite Tools - KPI Tasks ===\n")

    # таск 1 + 2
    print("Task 1-2: Generators + Timeout")
    print("Fibonacci (2 сек):")
    timeout_iterator(fibonacci_generator(), 2)
    
    print("\n" + "="*60)

    # таск 3
    print("Task 3: Memoization")
    @memoize(maxsize=100, policy="lru")
    def fib(n):
        if n <= 1: return n
        return fib(n-1) + fib(n-2)

    start = time.time()
    print(f"fib(35) = {fib(35)}")
    print(f"Час: {time.time()-start:.4f} сек (з кешем — швидко)\n")

    # таск 4
    print("Task 4: Bi-Directional Priority Queue")
    pq = BiDirectionalPriorityQueue()

    pq.enqueue("Низький пріоритет", 1)
    pq.enqueue("Високий пріоритет", 10)
    pq.enqueue("Середній", 5)
    pq.enqueue("Критичний", 100)
    pq.enqueue("Ще один старий", 1)

    print("Розмір черги:", pq.size())
    print("Найвищий пріоритет:", pq.dequeue_highest())
    print("Найнижчий пріоритет:", pq.dequeue_lowest())
    print("Найстаріший (oldest):", pq.dequeue_oldest())
    print("Найновіший (newest):", pq.dequeue_newest())

    print("\n Таск 4 виконано")

    print("\n" + "="*60)

    # таск5
    print("Task 5: Async Array Function Variants")
    values = [1, 2, 3, 4, 5]

    async def async_double(value):
        await asyncio.sleep(0.1)
        return value * 2

    def sync_double(value):
        return value * 2

    print("\nAsync/await version (async_map with async function):")
    print(asyncio.run(async_map(async_double, values)))

    print("\nAsync/await version (async_map with sync function):")
    print(asyncio.run(async_map(sync_double, values)))

    print("\nCallback-style version (callback_async_map):")
    callback_async_map(sync_double, values, lambda result: print(result))

    print("\nAbortable version (async_map_with_abort):")
    abort_event = asyncio.Event()
    abort_event.set()
    print(asyncio.run(async_map_with_abort(sync_double, values, abort_event)))

    print("\nТаск 5 виконано")

    print("\n" + "="*60)
    print("Task 6: Large Data Processing with Async Stream")

    result = asyncio.run(process_stream(large_data_stream(100000)))
    print("Result:", result)
    print("\nТаск 6 виконано")

    print("\n" + "="*60)
    print("Task 7: Reactive Communication with EventEmitter")

    emitter = EventEmitter()

    def logger(event_payload):
        print("Logger received:", event_payload)

    def alice_listener(payload):
        if payload and payload.get("to") == "Вася":
            print("Вася got message:", payload["text"])

    def bob_listener(payload):
        if payload and payload.get("to") == "Нікіта":
            print("Нікіта got message:", payload["text"])

    log_subscription = emitter.subscribe("message", logger)
    alice_subscription = emitter.subscribe("message", alice_listener)
    bob_subscription = emitter.subscribe("message", bob_listener)

    emitter.emit("message", {"from": "Нікіта", "to": "Вася", "text": "Привіт, Вася!"})
    emitter.emit("message", {"from": "Вася", "to": "Нікіта", "text": "Привіт, Нікіта!"})

    bob_subscription.unsubscribe()
    print("Нікіта відписався")

    emitter.emit("message", {"from": "Вася", "to": "Нікіта", "text": "Це останнє повідомлення для Нікіти"})

    print("\nТаск 7 виконано")

if __name__ == "__main__":
    main()
