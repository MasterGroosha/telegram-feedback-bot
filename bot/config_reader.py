from typing import Optional
from secrets import token_urlsafe

from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    bot_token: SecretStr
    admin_chat_id: int
    remove_sent_confirmation: bool
    webhook_domain: Optional[str]
    webhook_path: Optional[str]
    app_host: Optional[str] = "0.0.0.0"
    app_port: Optional[int] = 9000
    custom_bot_api: Optional[str]
    drop_pending_updates: Optional[bool]

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        env_nested_delimiter = '__'
        fields = {
            "app_port": {
                "env": "port",
            },
            "webhook_domain": {
                "env": "render_external_hostname",
            },
            "webhook_path": {
                "default_factory": token_urlsafe,
            },
        }


config = Settings()
