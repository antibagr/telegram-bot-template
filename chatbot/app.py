"""
Main module where bot is executed
"""

import logging
from aiogram import executor
import asyncio

from config import DEBUG
from handlers.connect_handlers import dp
from loader import bot
from utils.func import to_json
from load.launch_bot import on_startup, on_shutdown
from load.sender_consumer import consume_new_messages
from utils.async_func import async_task
from handlers.errors.send_exception import send_exception


def start_bot() -> None:
    """
    Entry point of an application.
    Runs event loop
    """

    if DEBUG:
        logging.info("Running in DEBUG mode")
    else:
        logging.info("Running in PRODUCTION mode")

    async_task(consume_new_messages())

    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)


if __name__ == '__main__':
    start_bot()
