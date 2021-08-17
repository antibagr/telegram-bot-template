'''
Main module where bot is executed
'''

from aiogram import executor
from loguru import logger

from handlers.connect import dp
# from loader import bot
# from utils.func import to_json
from load.launch_bot import on_startup, on_shutdown
# from load.sender_consumer import consume_new_messages
# from utils.async_func import async_task
# from handlers.errors.send_exception import send_exception

from settings import settings


def start_bot() -> None:
    '''
    Entry point of an application.
    Runs the event loop.
    '''
    logger.info(
        f'Running in {"DEBUG" if settings.DEBUG else "PRODUCTION"} mode'
    )
    # async_task(consume_new_messages())
    executor.start_polling(
        dp,
        on_startup=on_startup,
        on_shutdown=on_shutdown
    )


if __name__ == '__main__':
    start_bot()
