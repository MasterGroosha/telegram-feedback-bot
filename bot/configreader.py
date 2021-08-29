from dataclasses import dataclass
from os import getenv
from typing import Optional


@dataclass
class Bot:
    token: str
    admin_chat_id: int


@dataclass
class App:
    webhook_enabled: bool
    webhook_domain: Optional[str]
    webhook_path: Optional[str]
    host: Optional[str]
    port: Optional[int]


@dataclass
class Config:
    bot: Bot
    app: App


def load_config() -> Config:
    return Config(
        bot=Bot(
            token=getenv("BOT_TOKEN"),
            admin_chat_id=int(getenv("ADMIN_CHAT_ID"), 0)
        ),
        app=App(
            webhook_enabled=bool(getenv("WEBHOOK_ENABLED", False)),
            webhook_domain=getenv("WEBHOOK_DOMAIN"),
            webhook_path=getenv("WEBHOOK_PATH"),
            host=getenv("APP_HOST", "0.0.0.0"),
            port=int(getenv("APP_PORT", 9000))
        )
    )

