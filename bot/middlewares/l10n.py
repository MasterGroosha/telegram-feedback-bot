from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message
from fluent.runtime import FluentLocalization


class L10nMiddleware(BaseMiddleware):
    def __init__(self, l10n_object: FluentLocalization):
        self.l10n_object = l10n_object

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        data["l10n"] = self.l10n_object
        await handler(event, data)
