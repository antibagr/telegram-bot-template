import asyncio

import aiogram
from loguru import logger

from interface.text import msg
from settings import settings
from typehints import Dispatcher


async def set_default_bot_commands(dp: Dispatcher) -> None:
    '''
    Send request to set default bot's commands
    There will be shortcuts in chat where bot is added
    There is a little lag (up to 1 minute)
    before commands will change in telegram.

    dp: Dispatcher

    '''
    logger.debug('Set default commands')
    await dp.bot.set_my_commands([
            aiogram.types.BotCommand('start', 'Start a chat. Go on!'),
            aiogram.types.BotCommand('menu', 'Show my commands.'),
            aiogram.types.BotCommand('help', 'Show my help message.'),
    ])


async def on_startup(dp: Dispatcher) -> None:
    '''
    Called when the bot is started from app.start_bot

    Args:
        dp (Dispatcher): Dispatcher object
    Raises:
        BotBlocked: If bot was blocked by admin

    '''
    logger.warning('Start polling')
    try:
        await asyncio.gather(
            dp.bot.send_message(
                settings.ADMIN_ID,
                msg.bot_started,
                disable_notification=True
            ),
            set_default_bot_commands(dp),
        )
    except aiogram.utils.exceptions.ChatNotFound:
        logger.error(
            'Probably you set incorrect ADMIN_ID or '
            'don\'t have a conversation with the bot yet - '
            'unable to send a startup message.'
        )


async def on_shutdown(dp: Dispatcher) -> None:
    logger.warning('So long!')
