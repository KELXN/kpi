from __future__ import annotations

import json
import time
from collections import deque
from typing import Any, Callable, Dict, Iterable, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen


class AuthenticationStrategy:
    def get_auth_headers(self) -> Dict[str, str]:
        return {}

    def get_auth_params(self) -> Dict[str, str]:
        return {}

    def needs_refresh(self) -> bool:
        return False

    def refresh(self) -> None:
        return None


class ApiKeyStrategy(AuthenticationStrategy):
    def __init__(self, key: str, header_name: str = "X-API-Key", query_param: str = "api_key", inject_into: str = "header") -> None:
        self.key = key
        self.header_name = header_name
        self.query_param = query_param
        self.inject_into = inject_into

    def get_auth_headers(self) -> Dict[str, str]:
        if self.inject_into == "header":
            return {self.header_name: self.key}
        return {}

    def get_auth_params(self) -> Dict[str, str]:
        if self.inject_into == "query":
            return {self.query_param: self.key}
        return {}


class BearerTokenStrategy(AuthenticationStrategy):
    def __init__(self, token: str, expires_in: Optional[float] = None, refresh_callback: Optional[Callable[[], str]] = None) -> None:
        self.token = token
        self.refresh_callback = refresh_callback
        self.expires_at = time.time() + expires_in if expires_in is not None else None

    def get_auth_headers(self) -> Dict[str, str]:
        if self.needs_refresh():
            self.refresh()
        return {"Authorization": f"Bearer {self.token}"}

    def needs_refresh(self) -> bool:
        return self.expires_at is not None and time.time() >= self.expires_at

    def refresh(self) -> None:
        if self.refresh_callback is None:
            return
        new_token = self.refresh_callback()
        self.token = new_token
        self.expires_at = time.time() + 5


class RateLimiter:
    def __init__(self, max_requests: int, per_seconds: float = 1.0) -> None:
        self.max_requests = max_requests
        self.per_seconds = per_seconds
        self._timestamps = deque()

    def throttle(self) -> None:
        if self.max_requests <= 0:
            return
        now = time.time()
        while self._timestamps and now - self._timestamps[0] >= self.per_seconds:
            self._timestamps.popleft()
        if len(self._timestamps) >= self.max_requests:
            wait = self.per_seconds - (now - self._timestamps[0])
            if wait > 0:
                time.sleep(wait)
        self._timestamps.append(time.time())


class RequestError(Exception):
    pass


class AuthProxy:
    def __init__(self, base_url: str, rate_limit: int = 0, logger: Optional[Callable[[str], None]] = None) -> None:
        self.base_url = base_url.rstrip("/")
        self._strategies: Dict[str, AuthenticationStrategy] = {}
        self._current_strategy: Optional[AuthenticationStrategy] = None
        self._logger = logger or (lambda message: None)
        self._limiter = RateLimiter(rate_limit) if rate_limit > 0 else RateLimiter(0)
        self.history: list[Dict[str, Any]] = []

    def register_strategy(self, name: str, strategy: AuthenticationStrategy) -> None:
        self._strategies[name] = strategy
        if self._current_strategy is None:
            self._current_strategy = strategy

    def set_strategy(self, name: str) -> None:
        strategy = self._strategies.get(name)
        if strategy is None:
            raise ValueError(f"Authentication strategy '{name}' is not registered")
        self._current_strategy = strategy
        self._logger(f"Switched authentication strategy to '{name}'")

    def send_request(
        self,
        path: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        data: Optional[bytes] = None,
        timeout: float = 10.0,
    ) -> Any:
        self._limiter.throttle()

        url = urljoin(self.base_url + "/", path.lstrip("/"))
        params = params.copy() if params else {}
        headers = headers.copy() if headers else {}

        if self._current_strategy is not None:
            params.update(self._current_strategy.get_auth_params())
            headers.update(self._current_strategy.get_auth_headers())

        if params:
            url = f"{url}?{urlencode(params)}"

        request = Request(url, data=data, headers=headers, method=method)
        self._logger(f"Proxying {method} request to {url}")

        try:
            response = urlopen(request, timeout=timeout)
            raw_body = response.read()
            content_type = response.headers.get("Content-Type", "")
            body = raw_body.decode("utf-8")
            result = json.loads(body) if "application/json" in content_type else body
        except HTTPError as error:
            raise RequestError(f"HTTP error {error.code}: {error.reason}") from error
        except URLError as error:
            raise RequestError(f"Network error: {error.reason}") from error
        except ValueError:
            result = body

        self.history.append({
            "url": url,
            "method": method,
            "headers": headers,
            "response": result,
        })
        return result

    def get_history(self) -> Iterable[Dict[str, Any]]:
        return list(self.history)
