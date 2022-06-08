from asyncio import create_task, sleep

from aiogram import Router, F, Bot
from aiogram.dispatcher.filters import Command
from aiogram.types import ContentType
from aiogram.types import Message
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.blocklists import banned, shadowbanned
from bot.config_reader import config
from bot.filters import SupportedMediaFilter
from aiogram.methods.get_chat_member import GetChatMember
from bot.data import db
from bot.data.db import Database

db = Database('database.py')

bot = Bot(token=config.bot_token.get_secret_value())

router = Router()



async def _send_expiring_notification(message: Message):
    return




@router.message(Command(commands=["start"]))
async def cmd_start(message: Message):
    """
    Приветственное сообщение от бота пользователю

    :param message: сообщение от пользователя с командой /start
    """
    if message.chat.type == 'private':
        if not db.user_exists(message.from_user.id):
            db.add_user(message.from_user.id)
        await message.answer(
            "Саламалекум ✌️\n"
            "C моей помощью ты можешь связаться с моим хозяином и получить от него ответ. "
            "Просто напиши что-нибудь в этот диалог.")


@router.message(Command(commands=["sendall"]), F.reply_to_message)
async def cmd_sendall(message: Message):
    if message.chat.type == 'private':
        if message.from_user.id == 5181800215:
            text = message.reply_to_message.text
            photo = message.reply_to_message_id
            users = db.get_users()
            for row in users:
                if message.reply_to_message.text:
                    try:
                        await bot.send_message(row[0], text)
                    except Exception as e:
                        print(e)
                if message.reply_to_message.photo:
                    try:
                        await bot.send_photo(row[0], photo)
                    except Exception as e:
                        print(e)
                
                

           



@router.message(Command(commands=["help"]))
async def cmd_help(message: Message):
    """
    Справка для пользователя

    :param message: сообщение от пользователя с командой /help
    """
   
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="🕋 Владелец", url="https://t.me/ansdamn")
    )
    builder.row(InlineKeyboardButton(
        text="⛩ Вебсайт",
        url="https://yourmom.tk")
    )
    await message.answer(
        "За спам прописываю в ебало")
    
    

# urlkb = InlineKeyboardMarkup(row_width=1)
# urlButton = InlineKeyboardButton(text={message.from_user.first_name}, url='tg://user?id={message.from_user.id}')
# urlkb.add(urlButton)


@router.message(F.text)
async def text_message(message: Message, bot: Bot):
    """
    Хэндлер на текстовые сообщения от пользователя

    :param message: сообщение от пользователя для админа(-ов)
    """
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text=f"{message.from_user.first_name}", url=f"tg://user?id={message.from_user.id}")
    )
    
    builderz = InlineKeyboardBuilder()
    builderz.row(InlineKeyboardButton(
        text="🫂 Вступить", url="https://t.me/+Tr4jNXkJUjoxNDhl")
    )
    if len(message.text) > 4000:
        return await message.reply("К сожалению, длина этого сообщения превышает допустимый размер. "
                                   "Пожалуйста, сократи свою мысль и попробуй ещё раз.")
    
    check_member = await bot.get_chat_member(-1001565513038, message.from_user.id)
   
        

    if message.from_user.id in banned:
        await message.answer("К сожалению, автор бота решил тебя заблокировать, сообщения не будут доставлены. Лох.")
    elif message.from_user.id in shadowbanned:
        return
    elif check_member.status not in ["member", "creator"]:
        return await message.reply(f"<b>Перед тем как написать мне, вступите и ждите аппрува</b>", parse_mode="HTML", reply_markup=builderz.as_markup())
    else:
        await bot.send_message(
            config.admin_chat_id,
            message.html_text + f"\n\n<tg-spoiler>#id{message.from_user.id}</tg-spoiler>", parse_mode="HTML", reply_markup=builder.as_markup()
        )
        create_task(_send_expiring_notification(message))


@router.message(SupportedMediaFilter())
async def supported_media(message: Message):
    """
    Хэндлер на медиафайлы от пользователя.
    Поддерживаются только типы, к которым можно добавить подпись (полный список см. в регистраторе внизу)

    :param message: медиафайл от пользователя
    """
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text=f"{message.from_user.first_name}", url=f"tg://user?id={message.from_user.id}")
    )
    
    builderz = InlineKeyboardBuilder()
    builderz.row(InlineKeyboardButton(
        text="🫂 Вступить", url="https://t.me/+Tr4jNXkJUjoxNDhl")
    )
    check_member = await bot.get_chat_member(-1001565513038, message.from_user.id)

    if message.caption and len(message.caption) > 1000:
        return await message.reply("К сожалению, длина подписи медиафайла превышает допустимый размер. "
                                   "Пожалуйста, сократи свою мысль и попробуй ещё раз.")
    if message.from_user.id in banned:
        await message.answer("К сожалению, автор бота решил тебя заблокировать, сообщения не будут доставлены. Лох.")
    elif message.from_user.id in shadowbanned:
        return
    elif check_member.status not in ["member", "creator"]:
        return await message.reply(f"<b>Перед тем как написать мне, подпишитесь на канал и ждите аппрува</b>", parse_mode="HTML", reply_markup=builderz.as_markup())
    else:
        await message.copy_to(
            config.admin_chat_id,
            caption=((message.caption or "") + f"\n\n<tg-spoiler>#id{message.from_user.id}</tg-spoiler>"),
            parse_mode="HTML", reply_markup=builder.as_markup()
        )
        create_task(_send_expiring_notification(message))


@router.message()
async def unsupported_types(message: Message):
    """
    Хэндлер на неподдерживаемые типы сообщений, т.е. те, к которым нельзя добавить подпись

    :param message: сообщение от пользователя
    """
    # Игнорируем служебные сообщения
    if message.content_type not in (
            ContentType.NEW_CHAT_MEMBERS, ContentType.LEFT_CHAT_MEMBER, ContentType.VIDEO_CHAT_STARTED,
            ContentType.VIDEO_CHAT_ENDED, ContentType.VIDEO_CHAT_PARTICIPANTS_INVITED,
            ContentType.MESSAGE_AUTO_DELETE_TIMER_CHANGED, ContentType.NEW_CHAT_PHOTO, ContentType.DELETE_CHAT_PHOTO,
            ContentType.SUCCESSFUL_PAYMENT, "proximity_alert_triggered",  # в 3.0.0b3 нет поддержка этого контент-тайпа
            ContentType.NEW_CHAT_TITLE, ContentType.PINNED_MESSAGE):
        await message.reply("К сожалению, этот тип сообщения не поддерживается. Отправь что-нибудь другое.")
