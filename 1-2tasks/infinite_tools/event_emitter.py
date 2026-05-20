from __future__ import annotations
from typing import Callable, Dict, List, Any

class Subscription:
    def __init__(self, emitter: "EventEmitter", event: str, callback: Callable[[Any], None]):
        self._emitter = emitter
        self._event = event
        self._callback = callback
        self._is_active = True

    def unsubscribe(self) -> None:
        if not self._is_active:
            return
        self._emitter.unsubscribe(self._event, self._callback)
        self._is_active = False

    def is_active(self) -> bool:
        return self._is_active


class EventEmitter:
    def __init__(self) -> None:
        self._listeners: Dict[str, List[Callable[[Any], None]]] = {}

    def subscribe(self, event: str, callback: Callable[[Any], None]) -> Subscription:
        listeners = self._listeners.setdefault(event, [])
        listeners.append(callback)
        return Subscription(self, event, callback)

    def unsubscribe(self, event: str, callback: Callable[[Any], None]) -> None:
        listeners = self._listeners.get(event)
        if not listeners:
            return
        try:
            listeners.remove(callback)
        except ValueError:
            return
        if not listeners:
            self._listeners.pop(event, None)

    def emit(self, event: str, payload: Any = None) -> None:
        listeners = list(self._listeners.get(event, []))
        for callback in listeners:
            try:
                callback(payload)
            except Exception:
                pass

    def listener_count(self, event: str) -> int:
        return len(self._listeners.get(event, []))
