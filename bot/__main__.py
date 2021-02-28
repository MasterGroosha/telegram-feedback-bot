import asyncio
import logging
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

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

    bot = Bot(token=token)
    dp = Dispatcher(bot)

    # Регистрация хэндлеров
    register_usermode_handlers(dp)

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
