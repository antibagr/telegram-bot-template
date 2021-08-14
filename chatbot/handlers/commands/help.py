from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from loader import dp

from interface.verbose import msg
from handlers.addons import sticker_pack


@dp.message_handler(CommandHelp(), state='*')
async def help_command_handler(message: types.Message):

    await message.answer_sticker(sticker_pack['bear_typing'])
    await message.answer(msg.help)
