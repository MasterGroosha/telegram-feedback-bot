from aiogram import Router, F
from aiogram.types import ContentType, Message
from fluent.runtime import FluentLocalization

from bot.config_reader import config

router = Router()
router.message.filter(F.chat.id == config.admin_chat_id)


@router.message(~F.reply_to_message)
async def has_no_reply(message: Message, l10n: FluentLocalization):
    """
    Хэндлер на сообщение от админа, не содержащее ответ (reply).
    В этом случае надо кинуть ошибку.

    :param message: сообщение от админа, не являющееся ответом на другое сообщение
    :param l10n: объект локализации
    """
    if message.content_type not in (ContentType.NEW_CHAT_MEMBERS, ContentType.LEFT_CHAT_MEMBER):
        await message.reply(l10n.format_value("no-reply-error"))
