import logging
import asyncio


from aiogram import types
from aiogram.dispatcher import Dispatcher

from config import ADMIN_ID
from interface.verbose import msg


async def set_default_bot_commands(dp: Dispatcher) -> None:
    """
    Send request to set default bot's commands
    There will be shortcuts in chat where bot is added
    There is a little lag (up to 1 minute) before commands will change in telegram.

    dp: Dispatcher
    """

    logging.debug("Set default commands")

    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Начать диалог со мной"),
            types.BotCommand("menu", "Открыть моё меню"),
            types.BotCommand("help", "Посмотреть все мои команды"),
        ]
    )


async def on_startup(dp: Dispatcher) -> None:
    """
    Called when the bot is started from app.start_bot

    Args:
        dp (Dispatcher): Dispatcher object
    Raises:
        BotBlocked: If bot was blocked by admin

    """
    logging.warning("Start polling")
    await asyncio.gather(
        dp.bot.send_message(ADMIN_ID, msg.bot_started, disable_notification=True),
        set_default_bot_commands(dp)
    )


async def on_shutdown(dp: Dispatcher) -> None:
    ...
