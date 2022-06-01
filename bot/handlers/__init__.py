from aiogram import Router
from .private.broadcast import broadcast_command_handler, start_broadcast



def setup_routers() -> Router:
    from . import unsupported_reply, admin_no_reply, bans, adminmode, message_edit, usermode

    router = Router()
    router.include_router(unsupported_reply.router)
    router.include_router(bans.router)
    router.include_router(admin_no_reply.router)
    router.include_router(adminmode.router)
    router.include_router(message_edit.router)
    router.include_router(usermode.router)

    return router

def setup(dp):
    ...
    dp.register_message_handler(broadcast_command_handler, commands='broadcast')
    dp.register_message_handler(start_broadcast, state='broadcast_text', content_types=types.ContentTypes.ANY)
    logging.info("Handlers are successfully configured")
