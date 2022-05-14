from aiogram import Router


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
