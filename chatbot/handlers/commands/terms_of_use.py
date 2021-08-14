from aiogram import types

from loader import dp

from interface.verbose import msg, cmd


@dp.message_handler(commands=cmd.terms, chat_type=types.ChatType.PRIVATE, state='*')
async def terms_of_use(message: types.Message):
    await message.answer(msg.terms_of_use)
