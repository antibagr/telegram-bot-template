from aiogram import types
from loader import dp


@dp.message_handler()
async def echo(message: types.Message):
    """
    Used only in testing
    """

    await message.answer(message.text)
