"""
Clean phantom sprints created by sprint planner.
Run: python -m scripts.clean_sprints
"""
import sys, os, asyncio
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def clean():
    from backend.database import async_session, init_db
    from sqlalchemy import delete, select
    from backend.models.db_models import Sprint

    await init_db()
    async with async_session() as db:
        # Keep only sprints with sprint_number 1-4 (the real seed sprints)
        result = await db.execute(
            select(Sprint).where(Sprint.sprint_number > 4)
        )
        phantoms = result.scalars().all()
        print(f"Found {len(phantoms)} phantom sprints to delete...")
        await db.execute(delete(Sprint).where(Sprint.sprint_number > 4))
        await db.commit()
        print(f"Deleted {len(phantoms)} phantom sprints. Done.")

        # Verify
        result2 = await db.execute(select(Sprint))
        remaining = result2.scalars().all()
        print(f"Remaining sprints: {[s.name for s in remaining]}")

if __name__ == "__main__":
    asyncio.run(clean())
