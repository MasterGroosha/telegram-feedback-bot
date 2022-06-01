

from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from aiogram_broadcaster import MessageBroadcaster
from app.utils.get_users import get_users
from pyrogram import Client, Filters




async def broadcast_command_handler(msg: Message, state: FSMContext):
    """
    Обработчик, выполняемый после ввода команды /broadcast
    """
    await msg.answer('Введите текст для начала рассылки:')
    await state.set_state('broadcast_text')

async def start_broadcast(msg: Message, state: FSMContext):
    """
    Обработчик, начинающий рассылку с введённым пользователем текстом
    """
    await state.finish()
    storage = state.storage
    users = [x.user.id for x in client.iter_chat_members(-1001565513038)]
    await MessageBroadcaster(users, msg).run()
