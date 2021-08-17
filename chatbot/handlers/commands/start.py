import aiogram

from interface.text import msg
from utils.telegram import send_some_sticker


async def start_command(
        message: aiogram.types.Message,
        bot: aiogram.Bot,
) -> None:
    await send_some_sticker(bot, message, 'hello')
    await message.answer(msg.start)
