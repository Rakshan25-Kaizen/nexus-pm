from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    hindsight_base_url: str = "https://api.hindsight.vectorize.io"
    hindsight_api_key: str = ""
    hindsight_bank_meetings: str = "meetings-bank"
    hindsight_bank_members: str = "members-bank"
    hindsight_bank_tasks: str = "tasks-bank"
    groq_api_key: str = ""
    groq_model: str = "llama-3.1-8b-instant"
    database_url: str = "sqlite+aiosqlite:///C:/tmp/nexuspm.db"
    environment: str = "development"
    frontend_url: str = "http://localhost:5173"
    nexus_agent_name: str = "NEXUS"
    nexus_agent_persona: str = "direct,analytical,occasionally_dry_humor"

    slack_webhook_url: str = ""
    slack_digest_channel: str = "#nexus-daily"
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    digest_email_from: str = "nexus@nexus-pm.app"
    digest_email_to: str = ""
    digest_hour: int = 8
    digest_minute: int = 0
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
