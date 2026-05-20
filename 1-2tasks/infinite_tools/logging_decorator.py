import asyncio
import datetime
import functools
import inspect
import json
from typing import Any, Callable, Dict, Iterable, List, Optional, Union

LOG_LEVELS = {
    "DEBUG": 10,
    "INFO": 20,
    "ERROR": 40,
}


class LogRecord:
    def __init__(
        self,
        level: str,
        func_name: str,
        args: tuple,
        kwargs: dict,
        result: Any = None,
        exception: Optional[Exception] = None,
        duration: Optional[float] = None,
    ):
        self.timestamp = datetime.datetime.now().isoformat()
        self.level = level
        self.function = func_name
        self.args = args
        self.kwargs = kwargs
        self.result = result
        self.exception = exception
        self.duration = duration

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "level": self.level,
            "function": self.function,
            "args": self._serialize(self.args),
            "kwargs": self._serialize(self.kwargs),
            "result": self._serialize(self.result),
            "exception": self._serialize(self._exception_data()),
            "duration": self.duration,
        }

    def _exception_data(self) -> Optional[Dict[str, str]]:
        if not self.exception:
            return None
        return {
            "type": type(self.exception).__name__,
            "message": str(self.exception),
        }

    def _serialize(self, value: Any) -> Any:
        try:
            json.dumps(value)
            return value
        except (TypeError, OverflowError):
            return repr(value)


class LogFormatter:
    def format(self, record: LogRecord) -> str:
        raise NotImplementedError


class DefaultLogFormatter(LogFormatter):
    def format(self, record: LogRecord) -> str:
        pieces = [f"[{record.timestamp}] {record.level} - {record.function}()"]
        pieces.append(f"args={record.args}")
        pieces.append(f"kwargs={record.kwargs}")

        exception_data = record._exception_data()
        if exception_data is not None:
            pieces.append(f"exception={exception_data['type']}: {exception_data['message']}")
        else:
            pieces.append(f"result={record.result}")

        if record.duration is not None:
            pieces.append(f"duration={record.duration:.6f}s")

        return " | ".join(pieces)


class JSONLogFormatter(LogFormatter):
    def format(self, record: LogRecord) -> str:
        return json.dumps(record.to_dict(), ensure_ascii=False)


class LogHandler:
    def emit(self, message: str) -> None:
        raise NotImplementedError


class ConsoleLogHandler(LogHandler):
    def emit(self, message: str) -> None:
        print(message)


class FileLogHandler(LogHandler):
    def __init__(self, filename: str, mode: str = "a"):
        self.filename = filename
        self.mode = mode

    def emit(self, message: str) -> None:
        with open(self.filename, self.mode, encoding="utf-8") as handle:
            handle.write(message + "\n")


class ExternalServiceLogHandler(LogHandler):
    def __init__(self, send_func: Callable[[str], None]):
        self.send_func = send_func

    def emit(self, message: str) -> None:
        self.send_func(message)


def _build_handlers(
    handlers: Optional[Iterable[LogHandler]] = None,
    output: str = "console",
    filename: Optional[str] = None,
    external_sender: Optional[Callable[[str], None]] = None,
) -> List[LogHandler]:
    if handlers is not None:
        return list(handlers)

    if output == "console":
        return [ConsoleLogHandler()]
    if output == "file":
        if not filename:
            raise ValueError("Filename is required when output='file'.")
        return [FileLogHandler(filename)]
    if output == "external":
        if external_sender is None:
            raise ValueError("external_sender is required when output='external'.")
        return [ExternalServiceLogHandler(external_sender)]

    raise ValueError(f"Unsupported output type: {output}")


def _build_formatter(
    formatter: Optional[Union[LogFormatter, Callable[[LogRecord], str]]],
    structured: bool,
) -> LogFormatter:
    if formatter is None:
        return JSONLogFormatter() if structured else DefaultLogFormatter()

    if isinstance(formatter, LogFormatter):
        return formatter

    class CallableFormatter(LogFormatter):
        def __init__(self, func: Callable[[LogRecord], str]):
            self.func = func

        def format(self, record: LogRecord) -> str:
            return self.func(record)

    return CallableFormatter(formatter)


def log(
    level: str = "INFO",
    handlers: Optional[Iterable[LogHandler]] = None,
    output: str = "console",
    filename: Optional[str] = None,
    external_sender: Optional[Callable[[str], None]] = None,
    formatter: Optional[Union[LogFormatter, Callable[[LogRecord], str]]] = None,
    include_timing: bool = False,
    only_on_error: bool = False,
    structured: bool = False,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    actual_level = level.upper()
    if actual_level not in LOG_LEVELS:
        raise ValueError(f"Unsupported log level '{level}'. Use DEBUG, INFO, or ERROR.")

    resolved_handlers = _build_handlers(handlers, output, filename, external_sender)
    resolved_formatter = _build_formatter(formatter, structured)
    error_only = only_on_error or actual_level == "ERROR"

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            start = datetime.datetime.now() if include_timing else None
            try:
                result = await func(*args, **kwargs)
                duration = (datetime.datetime.now() - start).total_seconds() if start else None
                if not error_only:
                    record = LogRecord(
                        level=actual_level,
                        func_name=func.__name__,
                        args=args,
                        kwargs=kwargs,
                        result=result,
                        duration=duration,
                    )
                    message = resolved_formatter.format(record)
                    for handler in resolved_handlers:
                        handler.emit(message)
                return result
            except Exception as exc:
                duration = (datetime.datetime.now() - start).total_seconds() if start else None
                record = LogRecord(
                    level="ERROR",
                    func_name=func.__name__,
                    args=args,
                    kwargs=kwargs,
                    exception=exc,
                    duration=duration,
                )
                message = resolved_formatter.format(record)
                for handler in resolved_handlers:
                    handler.emit(message)
                raise

        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            start = datetime.datetime.now() if include_timing else None
            try:
                result = func(*args, **kwargs)
                duration = (datetime.datetime.now() - start).total_seconds() if start else None
                if not error_only:
                    record = LogRecord(
                        level=actual_level,
                        func_name=func.__name__,
                        args=args,
                        kwargs=kwargs,
                        result=result,
                        duration=duration,
                    )
                    message = resolved_formatter.format(record)
                    for handler in resolved_handlers:
                        handler.emit(message)
                return result
            except Exception as exc:
                duration = (datetime.datetime.now() - start).total_seconds() if start else None
                record = LogRecord(
                    level="ERROR",
                    func_name=func.__name__,
                    args=args,
                    kwargs=kwargs,
                    exception=exc,
                    duration=duration,
                )
                message = resolved_formatter.format(record)
                for handler in resolved_handlers:
                    handler.emit(message)
                raise

        wrapper = async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper
        return functools.wraps(func)(wrapper)

    return decorator
