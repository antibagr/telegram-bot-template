import logging
import asyncio
from typing import Optional, Union

from aiogram import types
from aiogram.utils.exceptions import RetryAfter, MessageIsTooLong, CantParseEntities
from aiogram.utils.parts import safe_split_text
from aiogram.utils.markdown import quote_html

from loader import bot

from config import MAGIC_ID, ERROR_CHAT_ID
from interface.verbose import msg
from exceptions import NotAuthorizedError
from utils.exception_utils import exception_to_string, log


async def notify_user(update: types.Update, exp: Exception) -> None:
    if update.message:
        trg = update.message
    elif update.callback_query:
        trg = update.callback_query.message
    elif update.edited_message:
        trg = update.edited_message
    else:
        logging.error(f"Unknown sourse\n\n{str(update)}")
        return None

    if isinstance(exp, NotAuthorizedError):
        await trg.answer(msg.err.not_authorized)
    else:
        await trg.answer(msg.err.default_error_answer)


async def send_exception(exp: Exception, header: Optional[Union[types.Update, dict, str]] = None) -> Optional[types.Message]:
    """
    Send exception details to the person with id defined in MAGIC_ID variable

    :param Exception exp: Exception that will be sent
    :param Optional[Union[types.Update, dict, str]] header: . Optional header of message
    :returns: Sent message on success
    """

    async def _send_exception(text: str) -> Optional[types.Message]:

        try:
            return await bot.send_message(ERROR_CHAT_ID, text)
        except RetryAfter as e:
            logging.error(f"Cannot send exception details. Flood limit is exceeded. Sleep {e.timeout} seconds.")
            await asyncio.sleep(e.timeout)
            return await _send_exception(text)
        except CantParseEntities:
            return await _send_exception(quote_html(text))

    header = header or exp.__class__.__name__

    err: str = exception_to_string(exp, header)

    log(exp)

    try:
        return await _send_exception(err)
    except MessageIsTooLong:
        for part in safe_split_text(err):
            last_message = await _send_exception(part)
        return last_message

    except Exception as sending_exp:
        logging.exception(sending_exp, exc_info=True)
