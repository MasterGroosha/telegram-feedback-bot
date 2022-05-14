from aiogram import Router
from aiogram.types import Message


router = Router()


@router.edited_message()
async def edited_message_warning(message: Message):
    """
    Хэндлер на редактирование сообщений.
    В настоящий момент реакция на редактирование с любой стороны одна: уведомлять о невозможности
    изменить нужное сообщение на стороне получателя.

    :param message: отредактированное пользователем или админом сообщение
    """
    await message.reply("К сожалению, редактирование сообщения не будет видно принимающей стороне. "
                        "Рекомендую просто отправить новое сообщение.")
