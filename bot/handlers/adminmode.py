from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import IsReplyFilter, IDFilter
from aiogram.utils.exceptions import BotBlocked, TelegramAPIError


def extract_id(message: types.Message) -> int:
    # Получение списка сущностей (entities) из текста или подписи к медиафайлу в отвечаемом сообщении
    entities = message.reply_to_message.entities or message.reply_to_message.caption_entities
    # Если всё сделано верно, то последняя (или единственная) сущность должна быть хэштегом...
    if not entities or entities[-1].type != "hashtag":
        raise ValueError("Не удалось извлечь ID для ответа!")

    # ... более того, хэштег должен иметь вид #id123456, где 123456 — ID получателя
    hashtag = entities[-1].get_text(message.reply_to_message.text or message.reply_to_message.caption)
    if len(hashtag) < 4 or not hashtag[3:].isdigit():  # либо просто #id, либо #idНЕЦИФРЫ
        raise ValueError("Некорректный ID для ответа!")

    return hashtag[3:]


async def reply_to_user(message: types.Message):
    """
    Ответ администратора на сообщение юзера (отправленное ботом).
    Используется метод copy_message, поэтому ответить можно чем угодно, хоть опросом.

    :param message: сообщение от админа, являющееся ответом на другое сообщение
    """

    try:
        user_id = extract_id(message)
    except ValueError as ex:
        return await message.reply(str(ex))

    # Вырезаем ID и пробуем отправить копию сообщения.
    # В теории, это можно оформить через errors_handler, но мне так нагляднее
    try:
        await message.copy_to(user_id)
    except BotBlocked:
        await message.reply("Не удалось отправить сообщение адресату, т.к. бот заблокирован на их стороне")
    except TelegramAPIError as ex:
        await message.reply(f"Не удалось отправить сообщение адресату! Ошибка: {ex}")


async def get_user_info(message: types.Message):
    try:
        user_id = extract_id(message)
    except ValueError as ex:
        return await message.reply(str(ex))
    try:
        user = await message.bot.get_chat(user_id)
    except TelegramAPIError as ex:
        return await message.reply(f"Не удалось получить информацию о пользователе! Ошибка: {ex}")
    u = f"@{user.username}" if user.username else 'нет'
    await message.reply(f"Имя: {user.full_name}\n\nID: {user.id}\nUsername: {u}")


async def admin_help(message: types.Message):
    await message.answer("В настоящий момент доступны следующие команды администратора:\n\n"
                         "/get или /who (в ответ на сообщение) — запрос информации о пользователе по его ID.")


def register_adminmode_handlers(dp: Dispatcher, admin_chat_id: int):
    dp.register_message_handler(get_user_info, IsReplyFilter(is_reply=True), IDFilter(chat_id=admin_chat_id),
                                commands=["get", "who"])
    dp.register_message_handler(admin_help, IDFilter(chat_id=admin_chat_id), commands="help")
    dp.register_message_handler(reply_to_user, IsReplyFilter(is_reply=True), IDFilter(chat_id=admin_chat_id),
                                content_types=types.ContentTypes.ANY)
