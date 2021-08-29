import asyncio
import logging
from os import getenv

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.dispatcher.webhook import configure_app
from aiogram.types import BotCommand

from bot.configreader import load_config, Config
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
    config: Config = load_config()
    if not config.bot.token:
        raise ValueError("Не указан токен. Бот не может быть запущен.")

    if not config.bot.admin_chat_id:
        raise ValueError("Не указан идентификатор чата для пересылки сообщений. Бот не может быть запущен.")
    if not isinstance(config.bot.admin_chat_id, int):
        raise ValueError(f'Идентификатор "{config.bot.admin_chat_id}" не является числом. Бот не может быть запущен.')

    bot = Bot(token=config.bot.token)
    bot["admin_chat_id"] = config.bot.admin_chat_id  # Добавление айдишника к объекту bot
    dp = Dispatcher(bot)

    # Регистрация хэндлеров
    register_adminmode_handlers(dp, config.bot.admin_chat_id)
    register_common_handlers(dp)
    register_usermode_handlers(dp)

    # Регистрация /-команд в интерфейсе
    await set_bot_commands(bot)

    me = await bot.get_me()
    logger.info(f"Starting @{me.username}")

    # Запуск поллинга или вебхуков
    if config.app.webhook_enabled:
        app = web.Application()
        configure_app(dp, app, config.app.webhook_path)
        runner = web.AppRunner(app)
        await runner.setup()
        await bot.set_webhook(f"https://{config.app.webhook_domain}{config.app.webhook_path}")
        site = web.TCPSite(runner, config.app.host, config.app.port)
        print("Starting webhook")
        try:
            await site.start()
            while True:
                await asyncio.sleep(3600)  # Нужно для поддержания сервера
        finally:
            await dp.storage.close()
            await dp.storage.wait_closed()
            await bot.session.close()
            await runner.cleanup()
    else:
        try:
            print("Starting polling")
            await dp.reset_webhook()
            # await dp.skip_updates()  # пропуск накопившихся апдейтов (необязательно)
            await dp.start_polling(allowed_updates=get_handled_updates_list(dp))
        finally:
            await dp.storage.close()
            await dp.storage.wait_closed()
            await bot.session.close()


asyncio.run(main())
