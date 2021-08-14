import logging
from aiogram import types
from aiogram.utils.exceptions import (Unauthorized, InvalidQueryID, TelegramAPIError,
                                      CantDemoteChatCreator, MessageNotModified,
                                      MessageToDeleteNotFound,
                                      MessageTextIsEmpty, RetryAfter,
                                      CantParseEntities, MessageCantBeDeleted,
                                      MessageIsTooLong, BotBlocked)

from loader import dp
from handlers.errors.send_exception import send_exception, notify_user


@dp.errors_handler()
async def errors_handler(update: types.Update, exp: Exception) -> bool:
    """
    Default aiogram errors handler. Will handle all exceptions raised in any handler.
    If True is returned, the exception will no longer be received in updates.

    :param types.Update update: .
    :param Exception exp: .

    """

    if isinstance(exp, MessageNotModified):
        return True

    await notify_user(update, exp)
    message_sent = await send_exception(exp, update)

    if message_sent and isinstance(exp, (BotBlocked, Unauthorized, InvalidQueryID, TelegramAPIError,
                                         CantDemoteChatCreator, MessageToDeleteNotFound, MessageTextIsEmpty,
                                         RetryAfter, CantParseEntities, MessageCantBeDeleted)):
        return True

    return False
