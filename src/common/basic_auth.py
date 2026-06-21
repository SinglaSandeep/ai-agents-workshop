"""HTTP Basic authentication middleware for workshop MCP servers."""

from __future__ import annotations

import base64
import binascii
import os
import secrets
from collections.abc import Awaitable, Callable
from typing import Any

from starlette.datastructures import Headers
from starlette.middleware import Middleware
from starlette.types import Receive, Scope, Send


ASGIApp = Callable[[Scope, Receive, Send], Awaitable[None]]


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} must be set to enable MCP Basic Auth.")
    return value


class BasicAuthMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        *,
        username: str | None = None,
        password: str | None = None,
        realm: str = "Zava MCP",
    ) -> None:
        self.app = app
        self.username = username or _required_env("MCP_BASIC_AUTH_USERNAME")
        self.password = password or _required_env("MCP_BASIC_AUTH_PASSWORD")
        self.realm = realm

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope.get("method") == "OPTIONS":
            await self.app(scope, receive, send)
            return

        if self._is_authorized(scope):
            await self.app(scope, receive, send)
            return

        await self._challenge(send)

    def _is_authorized(self, scope: Scope) -> bool:
        authorization = Headers(scope=scope).get("authorization", "")
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "basic" or not token:
            return False

        try:
            decoded = base64.b64decode(token, validate=True).decode("utf-8")
        except (binascii.Error, UnicodeDecodeError):
            return False

        username, separator, password = decoded.partition(":")
        if not separator:
            return False

        return secrets.compare_digest(username, self.username) and secrets.compare_digest(
            password, self.password
        )

    async def _challenge(self, send: Send) -> None:
        body = b"Unauthorized"
        headers: list[tuple[bytes, bytes]] = [
            (b"www-authenticate", f'Basic realm="{self.realm}"'.encode("ascii")),
            (b"content-type", b"text/plain; charset=utf-8"),
            (b"content-length", str(len(body)).encode("ascii")),
        ]
        await send({"type": "http.response.start", "status": 401, "headers": headers})
        await send({"type": "http.response.body", "body": body})


def mcp_basic_auth_middleware(**kwargs: Any) -> Middleware:
    return Middleware(BasicAuthMiddleware, **kwargs)