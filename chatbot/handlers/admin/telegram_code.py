import asyncio
import logging

from config import MAGIC_ID

from interface.verbose import msg

from loader import bot

async def SendCodeFailedMessage(text: str) -> None:

    logging.warning("Code sending failed... ")

    await asyncio.gather(
        bot.send_message(MAGIC_ID, text),
        )


async def SendCodeRequest(time_until: str = None) -> None:

    logging.debug("Sending code request to admin ...")

    await asyncio.gather(
        bot.send_message(MAGIC_ID, msg.admin.code_request.format(until=time_until)),
    )
