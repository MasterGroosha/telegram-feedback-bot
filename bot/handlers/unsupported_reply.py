from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import IsReplyFilter, IDFilter


async def unsupported_admin_reply_types(message: types.Message):
    """
    Хэндлер на неподдерживаемые типы сообщений, т.е. те, которые не имеют смысла
    для копирования. Например, опросы (админ не увидит результат)

    :param message: сообщение от администратора
    """
    await message.reply("К сожалению, этот тип сообщения не поддерживается для ответа пользователю.")


def register_admin_reply_handler(dp: Dispatcher, admin_chat_id: int):
    dp.register_message_handler(
        unsupported_admin_reply_types, IsReplyFilter(is_reply=True),
        IDFilter(chat_id=admin_chat_id), content_types=types.ContentTypes.POLL
    )
