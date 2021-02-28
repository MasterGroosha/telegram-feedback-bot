from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram import types
from typing import Dict, Any


class ConfigMiddleware(BaseMiddleware):
    def __init__(self, admin_chat_id: int):
        super(ConfigMiddleware, self).__init__()
        self.admin_chat_id = admin_chat_id

    async def on_pre_process_message(self, message: types.Message, data: Dict[str, Any]):
        data["admin_chat"] = self.admin_chat_id

    async def on_pre_process_callback_query(self, callback_query: types.CallbackQuery, data: Dict[str, Any]):
        data["admin_chat"] = self.admin_chat_id
