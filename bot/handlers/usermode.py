from asyncio import create_task, sleep

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import ContentType
from aiogram.types import Message

from bot.blocklists import banned, shadowbanned
from bot.config_reader import config
from bot.filters import SupportedMediaFilter

router = Router()


async def _send_expiring_notification(message: Message):
    """
    Отправляет "самоуничтожающееся" через 5 секунд сообщение

    :param message: сообщение, на которое бот отвечает подтверждением отправки
    """
    msg = await message.reply("Сообщение отправлено!")
    if config.remove_sent_confirmation:
        await sleep(5.0)
        await msg.delete()


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message):
    """
    Приветственное сообщение от бота пользователю

    :param message: сообщение от пользователя с командой /start
    """
    await message.answer(
        "Привет ✌️\n"
        "C моей помощью ты можешь связаться с моим хозяином и получить от него ответ. "
        "Просто напиши что-нибудь в этот диалог.")


@router.message(Command(commands=["help"]))
async def cmd_help(message: Message):
    """
    Справка для пользователя

    :param message: сообщение от пользователя с командой /help
    """
    await message.answer(
        "С моей помощью ты можешь связаться с владельцем этого бота и получить от него ответ.\n"
        "Просто продолжай писать в этот диалог, но учти, что поддерживаются не все типы сообщений, "
        "а только текст, фото, видео, аудио, файлы и голосовые сообщения (последние лучше не использовать "
        "без крайней необходимости).")


@router.message(F.text)
async def text_message(message: Message, bot: Bot):
    """
    Хэндлер на текстовые сообщения от пользователя

    :param message: сообщение от пользователя для админа(-ов)
    """
    if len(message.text) > 4000:
        return await message.reply("К сожалению, длина этого сообщения превышает допустимый размер. "
                                   "Пожалуйста, сократи свою мысль и попробуй ещё раз.")

    if message.from_user.id in banned:
        await message.answer("К сожалению, автор бота решил тебя заблокировать, сообщения не будут доставлены.")
    elif message.from_user.id in shadowbanned:
        return
    else:
        await bot.send_message(
            config.admin_chat_id,
            message.html_text + f"\n\n#id{message.from_user.id}", parse_mode="HTML"
        )
        create_task(_send_expiring_notification(message))


@router.message(SupportedMediaFilter())
async def supported_media(message: Message):
    """
    Хэндлер на медиафайлы от пользователя.
    Поддерживаются только типы, к которым можно добавить подпись (полный список см. в регистраторе внизу)

    :param message: медиафайл от пользователя
    """
    if message.caption and len(message.caption) > 1000:
        return await message.reply("К сожалению, длина подписи медиафайла превышает допустимый размер. "
                                   "Пожалуйста, сократи свою мысль и попробуй ещё раз.")
    if message.from_user.id in banned:
        await message.answer("К сожалению, автор бота решил тебя заблокировать, сообщения не будут доставлены.")
    elif message.from_user.id in shadowbanned:
        return
    else:
        await message.copy_to(
            config.admin_chat_id,
            caption=((message.caption or "") + f"\n\n#id{message.from_user.id}"),
            parse_mode="HTML"
        )
        create_task(_send_expiring_notification(message))


@router.message()
async def unsupported_types(message: Message):
    """
    Хэндлер на неподдерживаемые типы сообщений, т.е. те, к которым нельзя добавить подпись

    :param message: сообщение от пользователя
    """
    # Игнорируем служебные сообщения
    if message.content_type not in (
            ContentType.NEW_CHAT_MEMBERS, ContentType.LEFT_CHAT_MEMBER, ContentType.VIDEO_CHAT_STARTED,
            ContentType.VIDEO_CHAT_ENDED, ContentType.VIDEO_CHAT_PARTICIPANTS_INVITED,
            ContentType.MESSAGE_AUTO_DELETE_TIMER_CHANGED, ContentType.NEW_CHAT_PHOTO, ContentType.DELETE_CHAT_PHOTO,
            ContentType.SUCCESSFUL_PAYMENT, "proximity_alert_triggered",  # в 3.0.0b3 нет поддержка этого контент-тайпа
            ContentType.NEW_CHAT_TITLE, ContentType.PINNED_MESSAGE):
        await message.reply("К сожалению, этот тип сообщения не поддерживается. Отправь что-нибудь другое.")
