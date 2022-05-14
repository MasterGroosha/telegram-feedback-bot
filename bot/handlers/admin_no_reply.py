from aiogram import Router, F
from aiogram.types import ContentType, Message

from bot.config_reader import config

router = Router()
router.message.filter(F.chat.id == config.admin_chat_id)


@router.message(~F.reply_to_message)
async def has_no_reply(message: Message):
    """
    Хэндлер на сообщение от админа, не содержащее ответ (reply).
    В этом случае надо кинуть ошибку.

    :param message: сообщение от админа, не являющееся ответом на другое сообщение
    """
    if message.content_type not in (ContentType.NEW_CHAT_MEMBERS, ContentType.LEFT_CHAT_MEMBER):
        await message.reply("Это сообщение не является ответом на какое-либо другое!")
