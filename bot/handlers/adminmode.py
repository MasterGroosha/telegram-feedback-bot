from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import IsReplyFilter, IDFilter
from aiogram.utils.exceptions import BotBlocked, TelegramAPIError


async def has_no_reply(message: types.Message):
    if message.content_type not in (types.ContentType.NEW_CHAT_MEMBERS, types.ContentType.LEFT_CHAT_MEMBER):
        await message.reply("Это сообщение не является ответом на какое-либо другое!")


async def reply_to_user(message: types.Message):
    entities = message.reply_to_message.entities or message.reply_to_message.caption_entities
    if not entities or entities[-1].type != "hashtag":
        return await message.reply("Не удалось извлечь ID для ответа!")

    hashtag = entities[-1].get_text(message.reply_to_message.text or message.reply_to_message.caption)
    if len(hashtag) < 4 or not hashtag[3:].isdigit():  # либо просто #id, либо #idНЕЦИФРЫ
        return await message.reply("Некорректный ID для ответа!")

    try:
        await message.copy_to(hashtag[3:])
    except BotBlocked:
        await message.reply("Не удалось отправить сообщение адресату, т.к. бот заблокирован на их стороне")
    except TelegramAPIError as ex:
        await message.reply(f"Не удалось отправить сообщение адресату! Ошибка: {ex}")


def register_adminmode_handlers(dp: Dispatcher, admin_chat_id: int):
    dp.register_message_handler(reply_to_user, IsReplyFilter(is_reply=True), IDFilter(chat_id=admin_chat_id),
                                content_types=types.ContentTypes.ANY)
    dp.register_message_handler(has_no_reply, IsReplyFilter(is_reply=False), IDFilter(chat_id=admin_chat_id),
                                content_types=types.ContentTypes.ANY)
