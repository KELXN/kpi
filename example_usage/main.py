from infinite_tools.generators import fibonacci_generator, round_robin_generator
from infinite_tools.timeout import timeout_iterator


def main():
    print("Приклад: Фібоначчі (2 секунди)")
    fib = fibonacci_generator()
    timeout_iterator(fib, timeout_seconds=2)

    print("\nПриклад: round-robin (6 елементів, 10 ітерацій)")
    rr = round_robin_generator(["A", "B", "C", "D", "E", "F"]) 
    for i, v in zip(range(10), rr):
        print(v, end=" ")
    print()


if __name__ == "__main__":
    main()
