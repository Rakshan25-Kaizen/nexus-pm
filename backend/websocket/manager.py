from fastapi import WebSocket


class WebSocketManager:
    def __init__(self):
        self.connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, project_id: str):
        await websocket.accept()
        self.connections.setdefault(project_id, []).append(websocket)

    def disconnect(self, websocket: WebSocket, project_id: str):
        if project_id in self.connections:
            self.connections[project_id] = [
                ws for ws in self.connections[project_id] if ws != websocket
            ]

    async def broadcast(self, project_id: str, message: dict):
        dead = []
        for ws in self.connections.get(project_id, []):
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws, project_id)

    async def send_nudge(self, project_id: str, nudge: dict):
        await self.broadcast(project_id, {"type": "nudge", **nudge})

    async def send_agent_message(self, project_id: str, message: str):
        await self.broadcast(project_id, {"type": "agent_message", "content": message})


manager = WebSocketManager()
