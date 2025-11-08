from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Dict, List, Set, Any

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect


class WebSocketManager:
    """Track WebSocket connections by evaluation session."""

    def __init__(self) -> None:
        self._connections: Dict[str, Set[WebSocket]] = defaultdict(set)
        self._pending_messages: Dict[str, List[Any]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def connect(self, session_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections[session_id].add(websocket)
            pending = self._pending_messages.pop(session_id, [])
        for message in pending:
            await self._safe_send(websocket, message)

    async def disconnect(self, session_id: str, websocket: WebSocket) -> None:
        async with self._lock:
            connections = self._connections.get(session_id)
            if connections and websocket in connections:
                connections.remove(websocket)
                if not connections:
                    self._connections.pop(session_id, None)

    async def _safe_send(self, websocket: WebSocket, message: Any) -> None:
        try:
            await websocket.send_json(message)
        except (WebSocketDisconnect, RuntimeError):
            # Connection is gone; ignore
            pass

    async def send(self, session_id: str, message: Any) -> None:
        async with self._lock:
            connections = list(self._connections.get(session_id, []))
            if not connections:
                # Defer delivery until a client connects
                self._pending_messages[session_id].append(message)
                return
        to_remove: List[WebSocket] = []
        for websocket in connections:
            try:
                await websocket.send_json(message)
            except (WebSocketDisconnect, RuntimeError):
                to_remove.append(websocket)
        if to_remove:
            async with self._lock:
                for ws in to_remove:
                    connections = self._connections.get(session_id)
                    if connections and ws in connections:
                        connections.remove(ws)
                if connections := self._connections.get(session_id):
                    if not connections:
                        self._connections.pop(session_id, None)

    async def close_session(self, session_id: str) -> None:
        async with self._lock:
            websockets = list(self._connections.pop(session_id, []))
        for websocket in websockets:
            try:
                await websocket.close()
            except RuntimeError:
                pass
        async with self._lock:
            self._pending_messages.pop(session_id, None)


websocket_manager = WebSocketManager()
