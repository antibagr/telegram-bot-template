import aiogram

from interface.text import msg, cmd
# from handlers.stickers import send_some_sticker

from typehints import SkipHandler


async def unknown_command(message: aiogram.types.Message) -> None:
    if message.text.split()[0] not in cmd.get_all():
        # await send_some_sticker(message, 'question')
        await message.reply(msg.unknown_command)
        return
    raise SkipHandler()
