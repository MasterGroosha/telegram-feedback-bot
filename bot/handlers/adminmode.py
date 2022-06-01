from aiogram import Router, F, Bot
from aiogram.dispatcher.filters import Command
from aiogram.exceptions import TelegramAPIError
from aiogram.types import Message, Chat
from pyrogram import Client

from bot.config_reader import config

router = Router()
router.message.filter(F.chat.id == config.admin_chat_id)


def extract_id(message: Message) -> int:
    # Получение списка сущностей (entities) из текста или подписи к медиафайлу в отвечаемом сообщении
    entities = message.entities or message.caption_entities
    # Если всё сделано верно, то последняя (или единственная) сущность должна быть хэштегом...
    if not entities or entities[-2].type != "hashtag":
        raise ValueError("Не удалось извлечь ID для ответа!")

    # ... более того, хэштег должен иметь вид #id123456, где 123456 — ID получателя
    hashtag = entities[-1].extract(message.text or message.caption)
    if len(hashtag) < 4 or not hashtag[3:].isdigit():  # либо просто #id, либо #idНЕЦИФРЫ
        raise ValueError("Некорректный ID для ответа!")

    return int(hashtag[3:])

def get_users():
    """
    Return users list

    In this example returns some random ID's
    """
    users = [x.user.id for x in client.iter_chat_members(-1001565513038)]
    return users

@router.message(Command(commands=["get", "who"]), F.reply_to_message)
async def get_user_info(message: Message, bot: Bot):
    def get_full_name(chat: Chat):
        if not chat.first_name:
            return ""
        if not chat.last_name:
            return chat.first_name
        return f"{chat.first_name} {chat.last_name}"

    try:
        user_id = extract_id(message.reply_to_message)
    except ValueError as ex:
        return await message.reply(str(ex))

    try:
        user = await bot.get_chat(user_id)
    except TelegramAPIError as ex:
        return await message.reply(f"Не удалось получить информацию о пользователе! Ошибка: {ex}")

    u = f"@{user.username}" if user.username else 'нет'
    await message.reply(f"Имя: {get_full_name(user)}\n\nID: {user.id}\nUsername: {u}")


@router.message(F.reply_to_message)
async def reply_to_user(message: Message):
    """
    Ответ администратора на сообщение юзера (отправленное ботом).
    Используется метод copy_message, поэтому ответить можно чем угодно, хоть опросом.

    :param message: сообщение от админа, являющееся ответом на другое сообщение
    """

    # Вырезаем ID
    try:
        user_id = extract_id(message.reply_to_message)
    except ValueError as ex:
        return await message.reply(str(ex))

    # Пробуем отправить копию сообщения.
    # В теории, это можно оформить через errors_handler, но мне так нагляднее
    try:
        await message.copy_to(user_id)
    except TelegramAPIError as ex:
        await message.reply(f"Не удалось отправить сообщение адресату!\nОтвет от Telegram: {ex.message}")
        
@router.message(Command(commands=["broadcast"]))
async def broadcaster(message: Message) -> int:
    """
    Simple broadcaster

    :return: Count of messages
    """
    count = 0
    try:
        for user_idd in get_users():
            if await send_message(user_idd, '<b>Hello!</b>'):
                count += 1
            await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
    finally:
        log.info(f"{count} messages successful sent.")

    return count

