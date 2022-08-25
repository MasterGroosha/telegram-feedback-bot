from aiogram.filters import BaseFilter
from aiogram.types import Message, ContentType


class SupportedMediaFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.content_type in (
            ContentType.ANIMATION, ContentType.AUDIO, ContentType.DOCUMENT,
            ContentType.PHOTO, ContentType.VIDEO, ContentType.VOICE
        )
