import asyncio
import typing

import aiogram
from loguru import logger

from loader import bot

from settings import settings
from interface.text import msg
from utils.exception_utils import exception_to_string


async def notify_user(update: aiogram.types.Update) -> None:
    if update.message:
        trg = update.message
    elif update.callback_query:
        trg = update.callback_query.message
    elif update.edited_message:
        trg = update.edited_message
    else:
        logger.error(f'Unknown sourse:\n\n{str(update)}')
        return None
    await trg.answer(msg.err.default_error_answer)


async def send_exception_to_chat(
        text: str
) -> typing.Optional[aiogram.types.Message]:
    '''
    Some description required.
    '''
    try:
        return await bot.send_message(
            chat_id=settings.ERROR_CHAT_ID,
            text=text,
        )
    except aiogram.utils.exceptions.RetryAfter as exc:
        logger.error(
            'Cannot send exception details.'
            f'Flood limit is exceeded. Sleep {exc.timeout} seconds.'
        )
        await asyncio.sleep(exc.timeout)
        return await send_exception_to_chat(text)
    except aiogram.utils.exceptions.CantParseEntities:
        return await send_exception_to_chat(
            aiogram.utils.markdown.quote_html(text)
        )


async def send_exception(
        exp: Exception,
        header: typing.Union[None, aiogram.types.Update, dict, str] = None,
) -> typing.Optional[aiogram.types.Message]:
    '''
    Send exception details to the person ERROR_CHAT_ID if set

    :param Exception exp: Exception that will be sent
    :param Optional[Union[types.Update, dict, str]] header: . Optional header of message
    :returns: Sent message on success
    '''

    logger.exception(str(exp), exc_info=True)

    if not settings.ERROR_CHAT_ID:
        return

    header = header or exp.__class__.__name__
    err: str = exception_to_string(exp, header)

    try:
        return await send_exception_to_chat(err)
    except aiogram.utils.exceptions.MessageIsTooLong:
        for part in aiogram.utils.parts.safe_split_text(err):
            last_message = await send_exception_to_chat(part)
        return last_message
    except Exception as send_exc:
        logger.exception(send_exc, exc_info=True)
