import asyncio
from datetime import datetime
from sqlalchemy import select

def _run_async(coro):
    """Submit a coroutine to the running event loop from a background thread."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.run_coroutine_threadsafe(coro, loop)
        else:
            loop.run_until_complete(coro)
    except RuntimeError:
        # No event loop in this thread — create a fresh one
        asyncio.run(coro)

class NudgeEngine:
    def __init__(self):
        self.scheduler = None

    def start(self):
        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            from backend.config import get_settings
            
            settings = get_settings()
            self.scheduler = BackgroundScheduler(
                job_defaults={"misfire_grace_time": 60}
            )

            # Wrap async methods for sync scheduler
            def _check():
                _run_async(self.check_all_projects())

            def _digest():
                _run_async(self.send_morning_digest())

            self.scheduler.add_job(
                _check, "interval", minutes=30, id="nudge_check"
            )
            self.scheduler.add_job(
                _digest,
                "cron",
                hour=settings.digest_hour,
                minute=settings.digest_minute,
                id="morning_digest"
            )
            self.scheduler.start()
            print("[NudgeEngine] BackgroundScheduler started (cross-platform)")
        except Exception as e:
            print(f"[NudgeEngine] Scheduler failed to start: {e}")

    def shutdown(self):
        try:
            if self.scheduler and self.scheduler.running:
                self.scheduler.shutdown(wait=False)
                print("[NudgeEngine] Scheduler stopped")
        except Exception as e:
            print(f"[NudgeEngine] Shutdown warning: {e}")

    async def send_morning_digest(self):
        """Generate and deliver morning digest to all channels."""
        try:
            from backend.services.digest_service import generate_morning_digest
            from backend.services.delivery_service import deliver_digest
            from backend.models.db_models import Project, Nudge
            from backend.database import async_session
            from backend.websocket.manager import manager
            from backend.websocket.sse_manager import sse_manager
            import json

            async with async_session() as db:
                result = await db.execute(select(Project))
                projects = result.scalars().all()

                for project in projects:
                    project_id = str(project.id)

                    # 1. Generate the digest text
                    digest = await generate_morning_digest(project_id, db)
                    print(f"[NudgeEngine] Digest generated for {project_id}")

                    # 2. Deliver via Slack + Email
                    delivery_results = await deliver_digest(
                        project_id=project_id,
                        digest_text=digest,
                        project_name=project.name
                    )

                    # 3. Broadcast via WebSocket + SSE
                    payload = {
                        "type": "morning_digest",
                        "content": digest,
                        "timestamp": datetime.utcnow().isoformat(),
                        "delivered_via": delivery_results
                    }
                    await manager.broadcast(project_id, payload)
                    await sse_manager.broadcast(project_id, json.dumps(payload))

                    # 4. Save to Nudge table
                    nudge = Nudge(
                        project_id=project_id,
                        nudge_type="morning_digest",
                        message=digest,
                        severity="info",
                        created_at=datetime.utcnow()
                    )
                    db.add(nudge)

                await db.commit()
                print("[NudgeEngine] Morning digest cycle complete")

        except Exception as e:
            print(f"[NudgeEngine] send_morning_digest error: {e}")

    async def check_all_projects(self):
        try:
            from backend.agent.nexus_agent import nexus_agent
            from backend.models.db_models import Nudge, Project
            from backend.database import async_session
            from backend.websocket.manager import manager
            from backend.websocket.sse_manager import sse_manager

            async with async_session() as db:
                result = await db.execute(select(Project))
                projects = result.scalars().all()
                for project in projects:
                    nudge_messages = await nexus_agent.proactive_check(
                        str(project.id), db
                    )
                    for msg in nudge_messages:
                        nudge = Nudge(
                            project_id=str(project.id),
                            nudge_type="proactive",
                            message=msg,
                            severity="warning",
                            created_at=datetime.utcnow(),
                        )
                        db.add(nudge)
                        
                        # Send via WS and SSE
                        await manager.send_nudge(
                            str(project.id),
                            {"message": msg, "severity": "warning"},
                        )
                        await sse_manager.send_nudge(
                            str(project.id),
                            {"message": msg, "severity": "warning"},
                        )
                    await db.commit()
        except Exception as e:
            print(f"NudgeEngine check error: {e}")

    async def get_active_nudges(self, project_id: str, db) -> list:
        from backend.models.db_models import Nudge
        result = await db.execute(
            select(Nudge)
            .where(Nudge.project_id == project_id, Nudge.was_read == False)
            .order_by(Nudge.created_at.desc())
        )
        return result.scalars().all()

    async def mark_read(self, nudge_id: str, db):
        from sqlalchemy import update
        from backend.models.db_models import Nudge
        await db.execute(
            update(Nudge).where(Nudge.id == nudge_id).values(was_read=True)
        )
        await db.commit()

nudge_engine = NudgeEngine()
