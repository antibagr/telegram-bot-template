"""
Module where so-called reusable global objects are initialized
"""
import asyncio
import logging
import aiogram
# from aiogram.contrib.fsm_storage.memory import MemoryStorage
# from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from loguru import logger

from settings import settings
from load.patcher import patch_dispatcher


logger.add('chatbot.log', level='INFO')

bot = aiogram.Bot(
    token=settings.BOT_TOKEN,
    parse_mode=aiogram.types.ParseMode.HTML
)
# if settings.REDIS_HOST == '':
if True:
    storage = MemoryStorage()
else:
    storage = RedisStorage2(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
    )

dp = patch_dispatcher(
    aiogram.Dispatcher(bot, storage=storage)
)
