import functools

import aiogram

from loader import dp, bot
from interface.text import cmd
from typehints import (
    Command,
    CommandHelp,
    CommandStart,
    Text,
    ANYTYPE
)
from settings import settings

from .special import jsonify_message, get_current_state
from .help import help_command_handler
from .start import start_command
from .menu import menu_command
from .private_command import private_command_called_from_public_chat
from .unknown import unknown_command


if settings.ADMIN_ID != 0:
    dp.register_message_handler(
        jsonify_message,
        commands='str',
        user_id=settings.ADMIN_ID
    )
    dp.register_message_handler(
        get_current_state,
        commands='fsm',
        user_id=settings.ADMIN_ID
    )
dp.register_message_handler(
    help_command_handler,
    CommandHelp(),
)
dp.register_message_handler(
    functools.partial(start_command, bot=bot),
    CommandStart(),
    chat_type=aiogram.types.ChatType.PRIVATE,
)
dp.register_message_handler(
    menu_command,
    Command('menu'),
)
dp.register_message_handler(
    private_command_called_from_public_chat,
    commands=cmd.get_private(),
    chat_type=(
        aiogram.types.ChatType.GROUP,
        aiogram.types.ChatType.SUPERGROUP,
        aiogram.types.ChatType.CHANNEL,
    )
)
dp.register_message_handler(
    unknown_command,
    Text(startswith='/'),
    content_types=ANYTYPE,
)
