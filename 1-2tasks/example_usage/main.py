from infinite_tools.generators import fibonacci_generator, color_cycle_generator
from infinite_tools.timeout import timeout_iterator
from infinite_tools.memoization import memoize
from infinite_tools.priority_queue import BiDirectionalPriorityQueue
import time


def main():
    print("=== Infinite Tools - KPI Tasks ===\n")

    # Task 1 + 2
    print("Task 1-2: Generators + Timeout")
    print("Fibonacci (2 сек):")
    timeout_iterator(fibonacci_generator(), 2)
    
    print("\n" + "="*60)

    # Task 3
    print("Task 3: Memoization")
    @memoize(maxsize=100, policy="lru")
    def fib(n):
        if n <= 1: return n
        return fib(n-1) + fib(n-2)

    start = time.time()
    print(f"fib(35) = {fib(35)}")
    print(f"Час: {time.time()-start:.4f} сек (з кешем — швидко)\n")

    # Task 4
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


if __name__ == "__main__":
    main()