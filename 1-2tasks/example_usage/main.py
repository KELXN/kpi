import asyncio
from infinite_tools.generators import fibonacci_generator, color_cycle_generator
from infinite_tools.timeout import timeout_iterator
from infinite_tools.memoization import memoize
from infinite_tools.priority_queue import BiDirectionalPriorityQueue
from infinite_tools.async_array import async_map, callback_async_map, async_map_with_abort
from infinite_tools.event_emitter import EventEmitter
from infinite_tools.auth_proxy import AuthProxy, ApiKeyStrategy, BearerTokenStrategy
from infinite_tools.logging_decorator import (
    log,
    ConsoleLogHandler,
    FileLogHandler,
    ExternalServiceLogHandler,
    JSONLogFormatter,
)
import json
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
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

    print("\n" + "="*60)
    print("Task 8: Implementing an Authentication Proxy")

    class MockAPIHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = self.path.split("?", 1)
            query = parsed[1] if len(parsed) > 1 else ""
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {
                "path": parsed[0],
                "query": query,
                "headers": dict(self.headers),
                "message": "API response received",
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode("utf-8"))

        def log_message(self, format, *args):
            return

    api_port = 8081
    server = HTTPServer(("localhost", api_port), MockAPIHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    token_counter = {"value": 0}

    def refresh_token() -> str:
        token_counter["value"] += 1
        return f"refreshed-token-{token_counter['value']}"

    proxy = AuthProxy(f"http://localhost:{api_port}", rate_limit=3, logger=print)
    bearer_strategy = BearerTokenStrategy("initial-token", expires_in=1, refresh_callback=refresh_token)
    api_key_strategy = ApiKeyStrategy("super-secret-key", inject_into="header")

    proxy.register_strategy("bearer", bearer_strategy)
    proxy.register_strategy("api_key", api_key_strategy)
    proxy.set_strategy("bearer")

    print("Sending request with Bearer token strategy...")
    response1 = proxy.send_request("/data", params={"query": "first"})
    print("Response 1:", response1)

    time.sleep(1.5)
    print("Sending request after token expiration to trigger refresh...")
    response2 = proxy.send_request("/data", params={"query": "refresh"})
    print("Response 2:", response2)

    proxy.set_strategy("api_key")
    print("Switching to API key strategy...")
    response3 = proxy.send_request("/data", params={"query": "api-key"})
    print("Response 3:", response3)

    print("Proxy history entries:", len(list(proxy.get_history())))
    server.shutdown()
    server.server_close()
    print("\nТаск 8 виконано")

    print("\n" + "="*60)
    print("Task 9: Logging Decorator with Configurable Log Levels")

    external_log_entries = []

    def external_sink(message: str) -> None:
        external_log_entries.append(message)

    @log(level="INFO", include_timing=True)
    def multiply(a, b):
        return a * b

    @log(level="ERROR", output="file", filename="task9_errors.log")
    def fail_when_negative(value):
        if value < 0:
            raise ValueError("Negative values are not allowed")
        return value

    @log(
        level="DEBUG",
        handlers=[ConsoleLogHandler(), ExternalServiceLogHandler(external_sink)],
        formatter=JSONLogFormatter(),
        include_timing=True,
    )
    async def async_add(a, b):
        await asyncio.sleep(0.05)
        return a + b

    print("multiply result:", multiply(6, 7))

    try:
        fail_when_negative(-3)
    except ValueError as exc:
        print("Caught error:", exc)

    print("Running async_add...")
    print("async_add result:", asyncio.run(async_add(3, 4)))

    print("External log entries:", len(external_log_entries))
    print("Sample external entry:", external_log_entries[0] if external_log_entries else "none")
    print("Logged errors stored in task9_errors.log")

    print("\nТаск 9 виконано")

if __name__ == "__main__":
    main()
