from asyncio import create_task, sleep

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ContentType, Message
from fluent.runtime import FluentLocalization

from bot.blocklists import banned, shadowbanned
from bot.config_reader import config
from bot.filters import SupportedMediaFilter

router = Router()


async def _send_expiring_notification(message: Message, l10n: FluentLocalization):
    """
    Отправляет "самоуничтожающееся" через 5 секунд сообщение

    :param message: сообщение, на которое бот отвечает подтверждением отправки
    :param l10n: объект локализации
    """
    msg = await message.reply(l10n.format_value("sent-confirmation"))
    if config.remove_sent_confirmation:
        await sleep(5.0)
        await msg.delete()


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, l10n: FluentLocalization):
    """
    Приветственное сообщение от бота пользователю

    :param message: сообщение от пользователя с командой /start
    :param l10n: объект локализации
    """
    await message.answer(l10n.format_value("intro"))


@router.message(Command(commands=["help"]))
async def cmd_help(message: Message, l10n: FluentLocalization):
    """
    Справка для пользователя

    :param message: сообщение от пользователя с командой /help
    :param l10n: объект локализации
    """
    await message.answer(l10n.format_value("help"))


@router.message(Command(commands=["quality"]))
async def cmd_help(message: Message, l10n: FluentLocalization, state: FSMContext):
    await message.answer(l10n.format_value("quality"))
    await state.update_data(hashtag="#quality")


@router.message(Command(commands=["other"]))
async def cmd_help(message: Message, l10n: FluentLocalization, state: FSMContext):
    await message.answer(l10n.format_value("other"))
    await state.update_data(hashtag="#other")


def prepare_message_text(message: Message, category: str) -> str:
    username = "нет"
    if message.from_user.username:
        username = f"@{message.from_user.username}"
    parts = [message.html_text or "", f"\n\nUsername: {username}"]
    if category:
        parts.append(f"\nКатегория вопроса: {category}")
    parts.append(f"\nID пользователя: #id{message.from_user.id}")
    return "".join(parts)


@router.message(F.text)
async def process_hashtag(message: Message, bot: Bot, l10n: FluentLocalization, state: FSMContext):
    data = await state.get_data()
    category = data.get("hashtag")

    if category is None:
        await message.reply(l10n.format_value("no-question-category-selected"))
        return

    if len(message.text) > 4000:
        await message.reply(l10n.format_value("too-long-text-error"))
        return
    if message.from_user.id in banned:
        await message.answer(l10n.format_value("you-were-banned-error"))
        return
    elif message.from_user.id in shadowbanned:
        return

    await bot.send_message(
        chat_id=config.admin_chat_id,
        text=prepare_message_text(message, category)
    )
    await state.set_data({})  # Очищаем сохранённый хэштег
    create_task(_send_expiring_notification(message, l10n))


@router.message(SupportedMediaFilter())
async def process_hashtag(message: Message,l10n: FluentLocalization, state: FSMContext):
    data = await state.get_data()
    category = data.get("hashtag")

    if category is None:
        await message.reply(l10n.format_value("no-question-category-selected"))
        return

    if message.caption and len(message.caption) > 4000:
        await message.reply(l10n.format_value("too-long-caption-error"))
        return
    if message.from_user.id in banned:
        await message.answer(l10n.format_value("you-were-banned-error"))
        return
    elif message.from_user.id in shadowbanned:
        return

    await message.copy_to(
        chat_id=config.admin_chat_id,
        caption=prepare_message_text(message, category),
        parse_mode="HTML"
    )
    await state.set_data({})  # Очищаем сохранённый хэштег
    create_task(_send_expiring_notification(message, l10n))


@router.message()
async def unsupported_types(message: Message, l10n: FluentLocalization):
    """
    Хэндлер на неподдерживаемые типы сообщений, т.е. те, к которым нельзя добавить подпись

    :param message: сообщение от пользователя
    :param l10n: объект локализации
    """
    # Игнорируем служебные сообщения
    if message.content_type not in (
            ContentType.NEW_CHAT_MEMBERS, ContentType.LEFT_CHAT_MEMBER, ContentType.VIDEO_CHAT_STARTED,
            ContentType.VIDEO_CHAT_ENDED, ContentType.VIDEO_CHAT_PARTICIPANTS_INVITED,
            ContentType.MESSAGE_AUTO_DELETE_TIMER_CHANGED, ContentType.NEW_CHAT_PHOTO, ContentType.DELETE_CHAT_PHOTO,
            ContentType.SUCCESSFUL_PAYMENT, "proximity_alert_triggered",  # в 3.0.0b3 нет поддержка этого контент-тайпа
            ContentType.NEW_CHAT_TITLE, ContentType.PINNED_MESSAGE):
        await message.reply(l10n.format_value("unsupported-message-type-error"))
