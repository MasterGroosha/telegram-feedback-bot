from asyncio import create_task, sleep
from aiogram import Dispatcher, types
from aiogram.types import ContentType


async def _send_expiring_notification(message: types.Message):
    msg = await message.reply("Сообщение отправлено!")
    await sleep(5.0)
    await msg.delete()


async def text_message(message: types.Message, admin_chat: int):
    if len(message.text) > 4000:
        return await message.reply("К сожалению, длина этого сообщения превышает допустимый размер. "
                                   "Пожалуйста, сократите свою мысль и попробуйте ещё раз.")
    await message.bot.send_message(admin_chat, message.html_text + f"\n\n#id{message.from_user.id}", parse_mode="HTML")
    await create_task(_send_expiring_notification(message))


async def supported_media(message: types.Message, admin_chat: int):
    if message.caption and len(message.caption) > 1000:
        return await message.reply("К сожалению, длина подписи медиафайла превышает допустимый размер. "
                                   "Пожалуйста, сократите свою мысль и попробуйте ещё раз.")
    await message.copy_to(admin_chat,
                          caption=((message.caption or "") + f"\n\n#id{message.from_user.id}"),
                          parse_mode="HTML")
    await create_task(_send_expiring_notification(message))


async def unsupported_types(message: types.Message):
    print(message.content_type)
    await message.reply("К сожалению, этот тип сообщения не поддерживается "
                        "для пересылки от пользователей. Отправьте что-нибудь другое.")


async def cmd_help_user(message: types.Message):
    await message.answer("Справку пока не завезли 😔")


async def cmd_start_user(message: types.Message):
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
