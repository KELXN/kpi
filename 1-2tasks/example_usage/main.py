from infinite_tools.generators import (
    fibonacci_generator,
    color_cycle_generator,
    round_robin_generator
)
from infinite_tools.timeout import timeout_iterator
from infinite_tools.memoization import memoize
import time


def main():
    print("=== Task 1 & 2: Generators + Timeout Iterator ===\n")
    
    # Fibonacci з таймаутом
    print("Fibonacci sequence (2 секунди):")
    timeout_iterator(fibonacci_generator(), timeout_seconds=2)
    
    print("\nColor cycle (1.5 секунди):")
    timeout_iterator(color_cycle_generator(), timeout_seconds=1.5)
    
    print("\n" + "="*50)
    print("=== Task 3: Memoization ===\n")

    @memoize(maxsize=32, policy="lru")
    def fib(n: int) -> int:
        if n <= 1:
            return n
        return fib(n-1) + fib(n-2)

    # Тест швидкості
    start = time.time()
    print("fib(35) =", fib(35))
    print(f"Час першого виклику: {time.time() - start:.4f} сек")

    start = time.time()
    print("fib(35) повторно =", fib(35))
    print(f"Час повторного виклику: {time.time() - start:.4f} сек")

    print("\n✅ Task 3 виконано успішно!")


if __name__ == "__main__":
    main()