import aiogram


async def echo_handler(message: aiogram.types.Message) -> None:
    """
    Used only in testing
    """
    await message.answer(message.text)
