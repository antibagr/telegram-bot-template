import aiogram

from interface.text import msg
from utils.telegram import get_command_name


async def private_command_called_from_public_chat(
    message: aiogram.types.Message,
) -> None:
    """
    Called when somebody tries to call private
    command from group / supergroup / channel
    """
    await message.reply(
        msg.command_is_private.format(
            command=get_command_name(message.text)
        ),
        disable_web_page_preview=True,
    )
