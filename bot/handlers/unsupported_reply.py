from aiogram import Router, F
from aiogram.types import Message
from fluent.runtime import FluentLocalization

from bot.config_reader import config

router = Router()


@router.message(F.reply_to_message, F.chat.id == config.admin_chat_id, F.poll)
async def unsupported_admin_reply_types(message: Message, l10n: FluentLocalization):
    """
    Хэндлер на неподдерживаемые типы сообщений, т.е. те, которые не имеют смысла
    для копирования. Например, опросы (админ не увидит результат)

    :param message: сообщение от администратора
    :param l10n: объект локализации
    """
    await message.reply(l10n.format_value("cannot-reply-with-this-type-error"))
