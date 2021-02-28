from aiogram import Dispatcher, types
from aiogram.types import ContentType


async def text_message(message: types.Message):
    await message.reply("ok text")


async def supported_media(message: types.Message):
    await message.reply("ok media")


async def unsupported_types(message: types.Message):
    print(message.content_type)
    await message.reply("К сожалению, этот тип сообщения не поддерживается "
                        "для пересылки. Отправьте что-нибудь другое.")


def register_usermode_handlers(dp: Dispatcher):
    dp.register_message_handler(text_message, content_types=ContentType.TEXT)
    dp.register_message_handler(supported_media, content_types=[
        ContentType.ANIMATION, ContentType.AUDIO, ContentType.PHOTO,
        ContentType.DOCUMENT, ContentType.VIDEO, ContentType.VOICE
    ])
    dp.register_message_handler(unsupported_types, content_types=ContentType.ANY)
