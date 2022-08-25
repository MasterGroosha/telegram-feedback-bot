from contextlib import suppress

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from bot.blocklists import banned, shadowbanned
from bot.config_reader import config
from bot.handlers.adminmode import extract_id

router = Router()
router.message.filter(F.chat.id == config.admin_chat_id)


@router.message(Command(commands=["ban"]), F.reply_to_message)
async def cmd_ban(message: Message):
    try:
        user_id = extract_id(message.reply_to_message)
        print(user_id)
    except ValueError as ex:
        return await message.reply(str(ex))
    banned.add(int(user_id))
    await message.reply(
        f"ID {user_id} добавлен в список заблокированных. "
        f"При попытке отправить сообщение пользователь получит уведомление о том, что заблокирован."
    )


@router.message(Command(commands=["shadowban"]), F.reply_to_message)
async def cmd_shadowban(message: Message):
    try:
        user_id = extract_id(message)
    except ValueError as ex:
        return await message.reply(str(ex))
    shadowbanned.add(int(user_id))
    await message.reply(
        f"ID {user_id} добавлен в список скрытно заблокированных. "
        f"При попытке отправить сообщение пользователь не узнает, что заблокирован."
    )


@router.message(Command(commands=["unban"]), F.reply_to_message)
async def cmd_unban(message: Message):
    try:
        user_id = extract_id(message)
    except ValueError as ex:
        return await message.reply(str(ex))
    user_id = int(user_id)
    with suppress(KeyError):
        banned.remove(user_id)
    with suppress(KeyError):
        shadowbanned.remove(user_id)
    await message.reply(f"ID {user_id} разблокирован")


@router.message(Command(commands=["list_banned"]))
async def cmd_list_banned(message: Message):
    has_bans = len(banned) > 0 or len(shadowbanned) > 0
    if not has_bans:
        await message.answer("Нет заблокированных пользователей")
        return
    result = []
    if len(banned) > 0:
        result.append("Список заблокированных:")
        for item in banned:
            result.append(f"• #id{item}")
    if len(shadowbanned) > 0:
        result.append("\nСписок скрытно заблокированных:")
        for item in shadowbanned:
            result.append(f"• #id{item}")

    await message.answer("\n".join(result))
