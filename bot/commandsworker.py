from aiogram import Bot
from aiogram.types import BotCommand
from aiogram.types.bot_command_scope import BotCommandScopeDefault, BotCommandScopeChat


async def set_bot_commands(bot: Bot, admin_chat_id: int):
    usercommands = [
        BotCommand(command="help", description="Справка по использованию бота"),
    ]
    await bot.set_my_commands(usercommands, scope=BotCommandScopeDefault())

    admin_commands = [
        BotCommand(command="who", description="Получение информации о пользователе"),
        BotCommand(command="ban", description="Заблокировать пользователя"),
        BotCommand(command="shadowban", description="Скрытно заблокировать пользователя"),
        BotCommand(command="unban", description="Разблокировать пользователя"),
        BotCommand(command="list_banned", description="Список заблокированных"),
        BotCommand(command="help", description="Справка для админа бота"),
    ]
    await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=admin_chat_id))
