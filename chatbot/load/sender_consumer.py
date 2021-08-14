import asyncio
import logging

import aioredis

from config import REDIS_MESSAGE_CHANNEL, REDIS_URI
from loader import bot
from handlers.errors.send_exception import send_exception


async def consume_new_messages():
    redis = await aioredis.create_redis_pool(REDIS_URI)
    messages_channel = (await redis.subscribe(REDIS_MESSAGE_CHANNEL))[0]

    logging.info("Messages consumer initialized")

    while (await messages_channel.wait_message()):

        msg = await messages_channel.get_json()

        try:
            await bot.send_message(msg['user_id'], msg['message'])
        except Exception as e:
            await send_exception(e, header=f"Failed to send consumed message..")
