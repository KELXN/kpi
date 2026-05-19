import time
from typing import Iterator, Callable, Any


def timeout_iterator(
    iterator: Iterator[Any], 
    timeout_seconds: float, 
    process_func: Callable[[Any], None] = print
) -> None:
    """
    Обробляє ітератор протягом заданого часу.
    """
    start_time = time.time()
    count = 0

    try:
        for value in iterator:
            process_func(value)
            count += 1
            if time.time() - start_time > timeout_seconds:
                print(f"\n⏰ Таймаут {timeout_seconds} сек. Оброблено елементів: {count}")
                break
    except Exception as e:
        print(f"Помилка: {e}")
