import asyncio
from fastapi import Request
from typing import AsyncGenerator

class SSEManager:
    def __init__(self):
        # project_id -> list of queues
        self.queues: dict[str, list[asyncio.Queue]] = {}

    async def subscribe(self, project_id: str) -> AsyncGenerator[str, None]:
        queue = asyncio.Queue()
        self.queues.setdefault(project_id, []).append(queue)
        try:
            yield ": heartbeat\n\n"
            while True:
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=20.0)
                    yield f"data: {data}\n\n"
                except asyncio.TimeoutError:
                    yield ": heartbeat\n\n"
        finally:
            if project_id in self.queues and queue in self.queues[project_id]:
                self.queues[project_id].remove(queue)
                if not self.queues[project_id]:
                    del self.queues[project_id]

    async def broadcast(self, project_id: str, message: str):
        if project_id in self.queues:
            for queue in self.queues[project_id]:
                await queue.put(message)

    async def send_nudge(self, project_id: str, nudge: dict):
        import json
        await self.broadcast(project_id, json.dumps({"type": "nudge", **nudge}))

sse_manager = SSEManager()
