from aiogram import Router
from aiogram.types import Message
from fluent.runtime import FluentLocalization


router = Router()


@router.edited_message()
async def edited_message_warning(message: Message, l10n: FluentLocalization):
    """
    Хэндлер на редактирование сообщений.
    В настоящий момент реакция на редактирование с любой стороны одна: уведомлять о невозможности
    изменить нужное сообщение на стороне получателя.

    :param message: отредактированное пользователем или админом сообщение
    :param l10n: объект локализации
    """
    await message.reply(l10n.format_value("cannot-update-edited-error"))
