import aiogram

from .send_exception import send_exception, notify_user


async def errors_handler(
        update: aiogram.types.Update,
        exp: Exception,
) -> bool:
    """
    Default aiogram errors handler. Will handle all exceptions raised in
    any handler.
    If True is returned, the exception will no longer be received in updates.

    :param types.Update update: .
    :param Exception exp: .

    """

    if isinstance(exp, aiogram.utils.exceptions.MessageNotModified):
        return True
    await notify_user(update)
    message_sent = await send_exception(exp, update)
    if (
        message_sent is not None
        and isinstance(exp, (
                aiogram.utils.exceptions.BotBlocked,
                aiogram.utils.exceptions.Unauthorized,
                aiogram.utils.exceptions.InvalidQueryID,
                aiogram.utils.exceptions.TelegramAPIError,
                aiogram.utils.exceptions.CantDemoteChatCreator,
                aiogram.utils.exceptions.MessageToDeleteNotFound,
                aiogram.utils.exceptions.MessageTextIsEmpty,
                aiogram.utils.exceptions.RetryAfter,
                aiogram.utils.exceptions.CantParseEntities,
                aiogram.utils.exceptions.MessageCantBeDeleted,
            ))
    ):
        return True
    return False
