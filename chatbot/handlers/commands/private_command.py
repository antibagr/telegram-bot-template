from aiogram import types
from aiogram.dispatcher.handler import SkipHandler

from loader import dp

from interface.verbose import msg, bot_private_commands


@dp.message_handler(commands=bot_private_commands, state='*')
async def private_command_called_from_public_chat(message: types.Message) -> None:
    """
    Called when somebody tries to call private command from group / supergroup / channel
    """

    if message.from_user and message.from_user.id == message.chat.id:
        # called from private chat
        raise SkipHandler()

    await message.reply(msg.command_is_private.format(command=message.text), disable_web_page_preview=True)
