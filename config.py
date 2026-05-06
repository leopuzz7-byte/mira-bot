import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    bot_token: str
    anthropic_api_key: str
    database_url: str

    @classmethod
    def from_env(cls) -> "Config":
        token = os.getenv("BOT_TOKEN", "")
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        db_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///mira.db")
        if not token:
            raise ValueError("BOT_TOKEN не задан в .env")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY не задан в .env")
        return cls(bot_token=token, anthropic_api_key=api_key, database_url=db_url)

config = Config.from_env() if os.getenv("BOT_TOKEN") else None
