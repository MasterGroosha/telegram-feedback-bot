import asyncio
import logging
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from bot.middlewares.config import ConfigMiddleware
from bot.handlers.usermode import register_usermode_handlers

logger = logging.getLogger(__name__)


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="help", description="Справка по использованию бота"),
    ]
    await bot.set_my_commands(commands)


async def main():
    # Настройка логирования в stdout
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    # Объявление и инициализация объектов бота и диспетчера
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
    dp = Dispatcher(bot)

    # Регистрация хэндлеров
    register_usermode_handlers(dp)

    # Регистрация мидлвари
    dp.middleware.setup(ConfigMiddleware(admin_chat_id))

    # Регистрация /-команд в интерфейсе
    await set_bot_commands(bot)

    logger.info("Starting bot")

    # Запуск поллинга
    # await dp.skip_updates()  # пропуск накопившихся апдейтов (необязательно)
    await dp.start_polling()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except ValueError as ex:
        logger.error(ex)
        exit(1)
