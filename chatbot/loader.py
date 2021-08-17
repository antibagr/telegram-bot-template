"""
Module where so-called reusable global objects are initialized
"""
import aiogram
from aiogram.contrib.fsm_storage import memory, redis
from loguru import logger

from settings import settings
from load.patcher import patch_dispatcher


logger.add('chatbot.log', level='INFO')

bot = aiogram.Bot(
    token=settings.BOT_TOKEN,
    parse_mode=aiogram.types.ParseMode.HTML
)
if settings.REDIS_HOST == '':
    storage = memory.MemoryStorage()
else:
    storage = redis.RedisStorage2(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            prefix='chatbot',
    )

dp = patch_dispatcher(
    aiogram.Dispatcher(bot, storage=storage)
)
