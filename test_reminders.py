import asyncio
import os
import sys

# Add current dir to path
sys.path.append(os.getcwd())

async def test():
    from backend.routes.tasks import get_deadline_reminders
    from backend.database import async_session
    async with async_session() as db:
        try:
            print("Calling get_deadline_reminders...")
            res = await get_deadline_reminders("project-1", db)
            print(f"Success: {res}")
        except Exception as e:
            import traceback
            print("Caught exception:")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
