from collections import deque
import heapq
from typing import Any, Optional, Tuple, List


class BiDirectionalPriorityQueue:
    """
    Двостороння пріоритетна черга.
    Підтримує роботу як за пріоритетом (max/min), так і за порядком вставки (oldest/newest).
    """
    
    def __init__(self):
        self._priority_queue: List[Tuple[int, int, Any]] = []  
        self._insertion_order: deque = deque()                 
        self._counter = 0                                     
        self._entry_finder = {}                                

    def enqueue(self, item: Any, priority: int) -> None:
        """Додати елемент з пріоритетом"""
        self._counter += 1
        entry = (priority, self._counter, item)
        
        heapq.heappush(self._priority_queue, entry)
        self._insertion_order.append((priority, self._counter, item))
        self._entry_finder[(priority, self._counter)] = item

    def dequeue_highest(self) -> Optional[Any]:
        """Витягти елемент з найвищим пріоритетом"""
        while self._priority_queue:
            priority, counter, item = heapq.heappop(self._priority_queue)
            if (priority, counter) in self._entry_finder:
                del self._entry_finder[(priority, counter)]
                self._remove_from_insertion_order(priority, counter)
                return item
        return None

    def dequeue_lowest(self) -> Optional[Any]:
        """Витягти елемент з найнижчим пріоритетом (перевернутий пріоритет)"""
        while self._priority_queue:
            entry = heapq.heappop(self._priority_queue)
            neg_entry = (-entry[0], entry[1], entry[2])
            if (entry[0], entry[1]) in self._entry_finder:
                del self._entry_finder[(entry[0], entry[1])]
                self._remove_from_insertion_order(entry[0], entry[1])
                return entry[2]
        return None

    def dequeue_oldest(self) -> Optional[Any]:
        """Витягти найстаріший елемент (FIFO)"""
        while self._insertion_order:
            entry = self._insertion_order.popleft()
            if (entry[0], entry[1]) in self._entry_finder:
                del self._entry_finder[(entry[0], entry[1])]
                return entry[2]
        return None

    def dequeue_newest(self) -> Optional[Any]:
        """Витягти найновіший елемент (LIFO)"""
        while self._insertion_order:
            entry = self._insertion_order.pop()
            if (entry[0], entry[1]) in self._entry_finder:
                del self._entry_finder[(entry[0], entry[1])]
                return entry[2]
        return None

    def peek_highest(self) -> Optional[Any]:
        """Подивитися на елемент з найвищим пріоритетом (не видаляючи)"""
        while self._priority_queue:
            priority, counter, item = self._priority_queue[0]
            if (priority, counter) in self._entry_finder:
                return item
            heapq.heappop(self._priority_queue)
        return None

    def peek_lowest(self) -> Optional[Any]:
        """Подивитися на елемент з найнижчим пріоритетом"""
        if not self._priority_queue:
            return None
        min_prio = min(p for p, c, i in self._priority_queue if (p, c) in self._entry_finder)
        for p, c, i in self._priority_queue:
            if p == min_prio and (p, c) in self._entry_finder:
                return i
        return None

    def peek_oldest(self) -> Optional[Any]:
        """Подивитися найстаріший елемент"""
        for entry in self._insertion_order:
            if (entry[0], entry[1]) in self._entry_finder:
                return entry[2]
        return None

    def peek_newest(self) -> Optional[Any]:
        """Подивитися найновіший елемент"""
        for entry in reversed(self._insertion_order):
            if (entry[0], entry[1]) in self._entry_finder:
                return entry[2]
        return None

    def _remove_from_insertion_order(self, priority: int, counter: int):
        pass

    def size(self) -> int:
        return len(self._entry_finder)

    def is_empty(self) -> bool:
        return len(self._entry_finder) == 0

def create_priority_queue():
    return BiDirectionalPriorityQueue()