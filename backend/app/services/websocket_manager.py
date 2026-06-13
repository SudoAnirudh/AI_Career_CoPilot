from typing import List, Dict
from fastapi import WebSocket
import logging

logger = logging.getLogger("app.services.websocket")

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {
            "jobs": [],
            "tasks": []
        }

    async def connect(self, websocket: WebSocket, channel: str):
        """Accept a websocket connection and register it to a channel."""
        await websocket.accept()
        if channel in self.active_connections:
            self.active_connections[channel].append(websocket)
            logger.info(f"Client connected to WebSocket channel: {channel}")
        else:
            await websocket.close(code=4000, reason="Invalid channel")

    def disconnect(self, websocket: WebSocket, channel: str):
        """Unregister a websocket connection from a channel."""
        if channel in self.active_connections:
            if websocket in self.active_connections[channel]:
                self.active_connections[channel].remove(websocket)
                logger.info(f"Client disconnected from WebSocket channel: {channel}")

    async def broadcast(self, message: dict, channel: str):
        """Send a JSON payload to all active connections on a channel."""
        if channel in self.active_connections:
            logger.debug(f"Broadcasting to {len(self.active_connections[channel])} clients on channel '{channel}': {message}")
            for connection in self.active_connections[channel]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.warning(f"Error sending message to client: {e}. Connection may be stale.")
                    # We don't remove here to avoid modifying list during iteration;
                    # stale connections are cleaned up on disconnect/exception handlers in the endpoint loop.

ws_manager = ConnectionManager()
