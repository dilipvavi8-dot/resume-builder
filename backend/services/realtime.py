"""Small local WebSocket event hub used by the workspace UI."""

from __future__ import annotations

import asyncio
from typing import Any

from fastapi import WebSocket


class LocalEventHub:
    def __init__(self) -> None:
        self.connections: set[WebSocket] = set()
        self.loop: asyncio.AbstractEventLoop | None = None

    def start(self) -> None:
        self.loop = asyncio.get_running_loop()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.connections.discard(websocket)

    def publish(self, event: dict[str, Any]) -> None:
        if self.loop and self.connections:
            asyncio.run_coroutine_threadsafe(self._broadcast(event), self.loop)

    async def _broadcast(self, event: dict[str, Any]) -> None:
        stale: list[WebSocket] = []
        for connection in list(self.connections):
            try:
                await connection.send_json(event)
            except Exception:
                stale.append(connection)
        for connection in stale:
            self.disconnect(connection)


event_hub = LocalEventHub()
