"""
NEXUS-PM — Main FastAPI Application
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from backend.config import get_settings
from backend.database import init_db
from backend.services.nudge_engine import nudge_engine
from backend.agent.nexus_agent import nexus_agent
from backend.websocket.manager import manager
from backend.websocket.sse_manager import sse_manager
from fastapi.responses import StreamingResponse
from backend.routes import tasks, meetings, chat, members, agent, sprint

try:
    import nest_asyncio
    nest_asyncio.apply()
except ImportError:
    pass  # not needed on non-Windows

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    import os
    db_path = settings.database_url.replace("sqlite+aiosqlite:///", "")
    if db_path.startswith("./"):
        os.makedirs(os.path.dirname(os.path.abspath(db_path)) or ".", exist_ok=True)
    
    print("NEXUS-PM starting...")
    try:
        await init_db()
        print("  ✓ Database initialized")
    except Exception as e:
        print(f"  ✗ Database init warning: {e}")
    try:
        nudge_engine.start()
        print("  ✓ Nudge engine started")
    except Exception as e:
        print(f"  ⚠ Nudge engine warning: {e}")
    print("NEXUS-PM ready on http://localhost:8000")
    yield
    nudge_engine.shutdown()


app = FastAPI(title="NEXUS-PM API", lifespan=lifespan, debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers under /api prefix
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(meetings.router, prefix="/api/meetings", tags=["meetings"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(members.router, prefix="/api/members", tags=["members"])
app.include_router(agent.router, prefix="/api/agent", tags=["agent"])
app.include_router(sprint.router, prefix="/api/sprint", tags=["sprint"])


# WebSocket route directly on app (not via router)
@app.websocket("/ws/{project_id}")
async def ws_endpoint(websocket: WebSocket, project_id: str):
    await manager.connect(websocket, project_id)
    greeting = await nexus_agent.greet(project_id)
    await websocket.send_json(
        {"type": "agent_message", "content": greeting, "memories_used": 0}
    )
    try:
        while True:
            data = await websocket.receive_json()
            response = await nexus_agent.answer(
                data.get("message", ""),
                project_id,
                data.get("memory_enabled", True),
            )
            await websocket.send_json(
                {
                    "type": "agent_message",
                    "content": response.agent_message,
                    "memories_used": response.memories_used,
                }
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket, project_id)


@app.get("/api/notifications/events/{project_id}")
async def sse_events(project_id: str):
    """Server-Sent Events endpoint for proactive nudges."""
    return StreamingResponse(
        sse_manager.subscribe(project_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )


@app.get("/health")
async def health():
    from backend.ml.ml_engine import get_model_status
    ml_status = get_model_status()
    return {
        "status": "ok",
        "app": "NEXUS-PM",
        "memory": "Hindsight Cloud",
        "llm": settings.groq_model,
        "ml_models": ml_status,
    }


@app.get("/")
async def root():
    return {
        "message": "NEXUS-PM API",
        "docs": "/docs",
        "health": "/health",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
