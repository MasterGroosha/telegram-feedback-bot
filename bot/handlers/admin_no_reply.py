from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import IsReplyFilter, IDFilter


async def has_no_reply(message: types.Message):
    """
    Хэндлер на сообщение от админа, не содержащее ответ (reply).
    В этом случае надо кинуть ошибку.

    :param message: сообщение от админа, не являющееся ответом на другое сообщение
    """
    if message.content_type not in (types.ContentType.NEW_CHAT_MEMBERS, types.ContentType.LEFT_CHAT_MEMBER):
        await message.reply("Это сообщение не является ответом на какое-либо другое!")


def register_admin_no_reply_handlers(dp: Dispatcher, admin_chat_id: int):
    dp.register_message_handler(
        has_no_reply, IsReplyFilter(is_reply=False), IDFilter(chat_id=admin_chat_id),
        content_types=types.ContentTypes.ANY
    )
