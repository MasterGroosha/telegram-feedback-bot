from contextlib import suppress

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import IsReplyFilter, IDFilter

from bot.blocklists import banned, shadowbanned
from bot.handlers.adminmode import extract_id


async def cmd_ban(message: types.Message):
    try:
        user_id = extract_id(message)
    except ValueError as ex:
        return await message.reply(str(ex))
    banned.add(int(user_id))
    await message.reply(
        f"ID {user_id} добавлен в список заблокированных. "
        f"При попытке отправить сообщение пользователь получит уведомление о том, что заблокирован."
    )


async def cmd_shadowban(message: types.Message):
    try:
        user_id = extract_id(message)
    except ValueError as ex:
        return await message.reply(str(ex))
    shadowbanned.add(int(user_id))
    await message.reply(
        f"ID {user_id} добавлен в список скрытно заблокированных. "
        f"При попытке отправить сообщение пользователь не узнает, что заблокирован."
    )


async def cmd_unban(message: types.Message):
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


async def cmd_list_banned(message: types.Message):
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


def register_bans_handlers(dp: Dispatcher, admin_chat_id: int):
    dp.register_message_handler(cmd_ban, IsReplyFilter(is_reply=True), IDFilter(chat_id=admin_chat_id),
                                commands="ban")
    dp.register_message_handler(cmd_shadowban, IsReplyFilter(is_reply=True), IDFilter(chat_id=admin_chat_id),
                                commands="shadowban")
    dp.register_message_handler(cmd_unban, IsReplyFilter(is_reply=True), IDFilter(chat_id=admin_chat_id),
                                commands="unban")
    dp.register_message_handler(cmd_list_banned, IDFilter(chat_id=admin_chat_id),
                                commands="list_banned")
