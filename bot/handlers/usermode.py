from asyncio import create_task, sleep
from aiogram import Dispatcher, types
from aiogram.types import ContentType

from bot.blocklists import banned, shadowbanned


async def _send_expiring_notification(message: types.Message):
    """
    Отправляет "самоуничтожающееся" через 5 секунд сообщение

    :param message: сообщение, на которое бот отвечает подтверждением отправки
    """
    msg = await message.reply("Сообщение отправлено!")
    await sleep(5.0)
    await msg.delete()


async def text_message(message: types.Message):
    """
    Хэндлер на текстовые сообщения от пользователя

    :param message: сообщение от пользователя для админа(-ов)
    """
    if len(message.text) > 4000:
        return await message.reply("К сожалению, длина этого сообщения превышает допустимый размер. "
                                   "Пожалуйста, сократи свою мысль и попробуй ещё раз.")
    admin_chat_id = message.bot.get("admin_chat_id")

    if message.from_user.id in banned:
        await message.answer("К сожалению, ты был заблокирован автором бота и твои сообщения не будут доставлены.")
    elif message.from_user.id in shadowbanned:
        return
    else:
        await message.bot.send_message(
            admin_chat_id, message.html_text + f"\n\n#id{message.from_user.id}", parse_mode="HTML"
        )
        await create_task(_send_expiring_notification(message))


async def supported_media(message: types.Message):
    """
    Хэндлер на медиафайлы от пользователя.
    Поддерживаются только типы, к которым можно добавить подпись (полный список см. в регистраторе внизу)

    :param message: медиафайл от пользователя
    """
    if message.caption and len(message.caption) > 1000:
        return await message.reply("К сожалению, длина подписи медиафайла превышает допустимый размер. "
                                   "Пожалуйста, сократи свою мысль и попробуй ещё раз.")
    admin_chat_id = message.bot.get("admin_chat_id")
    await message.copy_to(admin_chat_id,
                          caption=((message.caption or "") + f"\n\n#id{message.from_user.id}"),
                          parse_mode="HTML")
    await create_task(_send_expiring_notification(message))


async def unsupported_types(message: types.Message):
    """
    Хэндлер на неподдерживаемые типы сообщений, т.е. те, к которым нельзя добавить подпись

    :param message: сообщение от пользователя
    """
    # Игнорируем служебные сообщения
    if message.content_type not in (
            ContentType.NEW_CHAT_MEMBERS, ContentType.LEFT_CHAT_MEMBER, ContentType.VOICE_CHAT_STARTED,
            ContentType.VOICE_CHAT_ENDED, ContentType.VOICE_CHAT_PARTICIPANTS_INVITED,
            ContentType.MESSAGE_AUTO_DELETE_TIMER_CHANGED, ContentType.NEW_CHAT_PHOTO, ContentType.DELETE_CHAT_PHOTO,
            ContentType.SUCCESSFUL_PAYMENT, ContentType.PROXIMITY_ALERT_TRIGGERED,
            ContentType.NEW_CHAT_TITLE, ContentType.PINNED_MESSAGE):
        await message.reply("К сожалению, этот тип сообщения не поддерживается "
                            "для пересылки от пользователей. Отправь что-нибудь другое.")


async def cmd_help_user(message: types.Message):
    """
    Справка для пользователя

    :param message: сообщение от пользователя с командой /help
    """
    await message.answer(
        "С моей помощью ты можешь связаться с владельцем этого бота и получить от него ответ.\n"
        "Просто продолжай писать в этот диалог, но учти, что поддерживаются не все типы сообщений, "
        "а только текст, фото, видео, аудио, файлы и голосовые сообщения (последние лучше не использовать "
        "без крайней необходимости).")


async def cmd_start_user(message: types.Message):
    """
    Приветственное сообщение от бота пользователю

    :param message: сообщение от пользователя с командой /start
    """
    await message.answer(
        "Привет ✌️\n"
        "C моей помощью ты можешь связаться с моим хозяином и получить от него ответ. "
        "Просто напиши что-нибудь в этот диалог.")


def register_usermode_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_start_user, commands="start")
    dp.register_message_handler(cmd_help_user, commands="help")
    dp.register_message_handler(text_message, content_types=ContentType.TEXT)
    dp.register_message_handler(supported_media, content_types=[
        ContentType.ANIMATION, ContentType.AUDIO, ContentType.PHOTO,
        ContentType.DOCUMENT, ContentType.VIDEO, ContentType.VOICE
    ])
    dp.register_message_handler(unsupported_types, content_types=ContentType.ANY)
