'''
Main module where bot is executed
'''

from aiogram import executor
from loguru import logger

from handlers.connect import dp
from load.launch_bot import on_startup, on_shutdown
from settings import settings


def start_bot() -> None:
    '''
    Entry point of an application.
    Runs the event loop.
    '''
    logger.info(
        f'Running in {"DEBUG" if settings.DEBUG else "PRODUCTION"} mode'
    )
    executor.start_polling(
        dp,
        on_startup=on_startup,
        on_shutdown=on_shutdown
    )


if __name__ == '__main__':
    start_bot()
