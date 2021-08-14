from aiogram import types
from aiogram.dispatcher.handler import SkipHandler
from aiogram.dispatcher.filters.builtin import Text


from loader import dp

from interface.verbose import msg, bot_commands
from handlers.addons import send_some_sticker
from utils.hints import ANYTYPE


@dp.message_handler(Text(startswith="/"), content_types=ANYTYPE, state='*')
async def unknown_command_handler(message: types.Message):
    if message.text.split()[0] not in bot_commands:
        await send_some_sticker(message, 'question')
        await message.reply(msg.unknown_command)
    else:
        raise SkipHandler()
