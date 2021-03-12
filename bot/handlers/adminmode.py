from typing import Tuple, Optional
from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import IsReplyFilter, IDFilter
from aiogram.utils.exceptions import BotBlocked, TelegramAPIError


def _extract_id(message: types.Message) -> Tuple[Optional[int], Optional[str]]:
    # Получение списка сущностей (entities) из текста или подписи к медиафайлу в отвечаемом сообщении
    entities = message.reply_to_message.entities or message.reply_to_message.caption_entities
    # Если всё сделано верно, то последняя (или единственная) сущность должна быть хэштегом...
    if not entities or entities[-1].type != "hashtag":
        return None, "Не удалось извлечь ID для ответа!"

    # ... более того, хэштег должен иметь вид #id123456, где 123456 — ID получателя
    hashtag = entities[-1].get_text(message.reply_to_message.text or message.reply_to_message.caption)
    if len(hashtag) < 4 or not hashtag[3:].isdigit():  # либо просто #id, либо #idНЕЦИФРЫ
        return None, "Некорректный ID для ответа!"

    return hashtag[3:], None


async def unsupported_reply_types(message: types.Message):
    """
    Хэндлер на неподдерживаемые типы сообщений, т.е. те, которые не имеют смысла
    для копирования. Например, опросы (админ не увидит результат)

    :param message: сообщение от администратора
    """
    await message.reply("К сожалению, этот тип сообщения не поддерживается для ответа пользователю.")


async def has_no_reply(message: types.Message):
    """
    Хэндлер на сообщение от админа, не содержащее ответ (reply).
    В этом случае надо кинуть ошибку.

    :param message: сообщение от админа, не являющееся ответом на другое сообщение
    """
    if message.content_type not in (types.ContentType.NEW_CHAT_MEMBERS, types.ContentType.LEFT_CHAT_MEMBER):
        await message.reply("Это сообщение не является ответом на какое-либо другое!")


async def reply_to_user(message: types.Message):
    """
    Ответ администратора на сообщение юзера (отправленное ботом).
    Используется метод copy_message, поэтому ответить можно чем угодно, хоть опросом.

    :param message: сообщение от админа, являющееся ответом на другое сообщение
    """

    user_id, error = _extract_id(message)
    if error:
        return await message.reply(error)

    # Вырезаем ID и пробуем отправить копию сообщения.
    # В теории, это можно оформить через errors_handler, но мне так нагляднее
    try:
        await message.copy_to(user_id)
    except BotBlocked:
        await message.reply("Не удалось отправить сообщение адресату, т.к. бот заблокирован на их стороне")
    except TelegramAPIError as ex:
        await message.reply(f"Не удалось отправить сообщение адресату! Ошибка: {ex}")


async def get_user_info(message: types.Message):
    user_id, error = _extract_id(message)
    if error:
        return await message.reply(error)
    try:
        user = await message.bot.get_chat(user_id)
    except TelegramAPIError as ex:
        return await message.reply(f"Не удалось получить информацию о пользователе! Ошибка: {ex}")
    await message.reply(f"Имя: {user.full_name}\n\nID: {user.id}\nUsername: {user.username or 'нет'}")


async def admin_help(message: types.Message):
    await message.answer(f"В настоящий момент доступны следующие команды администратора:\n\n"
                         f"/get (в ответ на сообщение) — запрос информации о пользователе по его ID.")


def register_adminmode_handlers(dp: Dispatcher, admin_chat_id: int):
    dp.register_message_handler(unsupported_reply_types, IsReplyFilter(is_reply=True), IDFilter(chat_id=admin_chat_id),
                                content_types=types.ContentTypes.POLL)
    dp.register_message_handler(get_user_info, IsReplyFilter(is_reply=True), IDFilter(chat_id=admin_chat_id),
                                commands="get")
    dp.register_message_handler(admin_help, IDFilter(chat_id=admin_chat_id), commands="help")
    dp.register_message_handler(reply_to_user, IsReplyFilter(is_reply=True), IDFilter(chat_id=admin_chat_id),
                                content_types=types.ContentTypes.ANY)
    dp.register_message_handler(has_no_reply, IsReplyFilter(is_reply=False), IDFilter(chat_id=admin_chat_id),
                                content_types=types.ContentTypes.ANY)
