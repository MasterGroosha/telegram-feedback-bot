import asyncio
import logging
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from bot.handlers.usermode import register_usermode_handlers
from bot.handlers.adminmode import register_adminmode_handlers
from bot.handlers.common import register_common_handlers

logger = logging.getLogger(__name__)


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="help", description="Справка по использованию бота"),
    ]
    await bot.set_my_commands(commands)


def get_handled_updates_list(dp: Dispatcher) -> list:
    """
    Here we collect only the needed updates for bot based on already registered handlers types.
    This way Telegram doesn't send unwanted updates and bot doesn't have to proceed them.

    :param dp: Dispatcher
    :return: a list of registered handlers types
    """
    available_updates = (
        "callback_query_handlers", "channel_post_handlers", "chat_member_handlers",
        "chosen_inline_result_handlers", "edited_channel_post_handlers", "edited_message_handlers",
        "inline_query_handlers", "message_handlers", "my_chat_member_handlers", "poll_answer_handlers",
        "poll_handlers", "pre_checkout_query_handlers", "shipping_query_handlers"
    )
    return [item.replace("_handlers", "") for item in available_updates
            if len(dp.__getattribute__(item).handlers) > 0]


async def main():
    # Настройка логирования в stdout
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    # Объявление и инициализация объектов бота и диспетчера,
    # а также извлечение переменных окружения с приведением к нужным типам
    token = getenv("BOT_TOKEN", None)
    if not token:
        raise ValueError("Не указан токен. Бот не может быть запущен.")

    admin_chat_id = getenv("ADMIN_CHAT_ID", None)
    if not admin_chat_id:
        raise ValueError("Не указан идентификатор чата для пересылки сообщений. Бот не может быть запущен.")
    try:
        admin_chat_id = int(admin_chat_id)
    except ValueError:
        raise ValueError(f'Идентификатор "{admin_chat_id}" не является числом. Бот не может быть запущен.')

    bot = Bot(token=token)
    bot["admin_chat_id"] = admin_chat_id  # Добавление айдишника к объекту bot
    dp = Dispatcher(bot)

    # Регистрация хэндлеров
    register_adminmode_handlers(dp, admin_chat_id)
    register_common_handlers(dp)
    register_usermode_handlers(dp)

    # Регистрация /-команд в интерфейсе
    await set_bot_commands(bot)

    logger.info("Starting bot")

    # Запуск поллинга
    # await dp.skip_updates()  # пропуск накопившихся апдейтов (необязательно)
    try:
        await dp.start_polling(allowed_updates=get_handled_updates_list(dp))
    finally:
        await bot.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except ValueError as ex:
        logger.error(ex)
        exit(1)
