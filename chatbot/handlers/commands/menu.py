import aiogram

from interface.text import msg


async def menu_command(message: aiogram.types.Message) -> None:
    await message.answer(msg.menu)
