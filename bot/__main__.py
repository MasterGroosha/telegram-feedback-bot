import asyncio
import logging
from os import getenv

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.dispatcher.webhook import configure_app

from bot.configreader import load_config, Config
from bot.commandsworker import set_bot_commands
from bot.handlers.unsupported_reply import register_admin_reply_handler
from bot.handlers.admin_no_reply import register_admin_no_reply_handlers
from bot.handlers.usermode import register_usermode_handlers
from bot.handlers.adminmode import register_adminmode_handlers
from bot.handlers.bans import register_bans_handlers
from bot.handlers.common import register_common_handlers
from bot.updatesworker import get_handled_updates_list

logger = logging.getLogger(__name__)


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
    register_admin_reply_handler(dp, config.bot.admin_chat_id)
    register_bans_handlers(dp, config.bot.admin_chat_id)
    register_adminmode_handlers(dp, config.bot.admin_chat_id)
    register_admin_no_reply_handlers(dp, config.bot.admin_chat_id)
    register_common_handlers(dp)
    register_usermode_handlers(dp)

    # Регистрация /-команд в интерфейсе
    await set_bot_commands(bot, config.bot.admin_chat_id)

    me = await bot.get_me()
    logger.info(f"Starting @{me.username}")

    # Запуск поллинга или вебхуков
    if config.app.webhook_enabled:
        app = web.Application()
        configure_app(dp, app, config.app.webhook_path)
        runner = web.AppRunner(app, access_log=None)
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
