"""
Module where so-called reusable global objects are initialized
"""
import asyncio
import logging
import aiogram
# from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from config import BOT_TOKEN, REDIS_HOST
from utils.wrap import bake


logging.getLogger('aiogram').setLevel(logging.INFO)
logging.getLogger('root').setLevel(logging.DEBUG)


bot = aiogram.Bot(token=BOT_TOKEN, parse_mode=aiogram.types.ParseMode.HTML)

storage = RedisStorage2()
dp = aiogram.Dispatcher(bot, storage=storage)

dp.message_handler = bake(dp.message_handler)
dp.callback_query_handler = bake(dp.callback_query_handler)
