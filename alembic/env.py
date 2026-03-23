import asyncio
import os
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import async_engine_from_config, AsyncConnection
from sqlalchemy import pool
from alembic import context
from dotenv import load_dotenv

load_dotenv()

from backend.models.db_models import Base
target_metadata = Base.metadata

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)


def get_url():
    url = os.environ.get("DATABASE_URL", "")
    if url.startswith("postgresql+asyncpg"):
        return url
    return url.replace("postgresql://", "postgresql+asyncpg://")


def run_migrations_offline():
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    cfg = config.get_section(config.config_ini_section, {})
    cfg["sqlalchemy.url"] = get_url()
    engine = async_engine_from_config(
        cfg, prefix="sqlalchemy.", poolclass=pool.NullPool
    )
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
