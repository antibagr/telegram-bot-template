import aiogram

from interface.text import msg
from utils.telegram import single_stickers


async def help_command_handler(
        message: aiogram.types.Message,
) -> None:
    await message.answer_sticker(single_stickers.bear_typing)
    await message.answer(msg.help)
