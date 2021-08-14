import io
import asyncio
from typing import Optional

from aiogram import types

from orm.user import UserWrapper
from interface.verbose import msg
from handlers.addons import send_some_sticker
from utils.async_func import async_task


async def answer_robot_txt(message: types.Message) -> Optional[types.message.Message]:
    """
    Handler just for fun. If for some reasone
    message sender doens't have field from_user
    that means it's another bot so we'll treat him
    Like usually do with robots.

    """
    robots_txt = types.input_file.InputFile(io.BytesIO(b"User-agent: * Disallow: /"), filename="robots.txt")
    return await message.answer_document(robots_txt)


async def handler_unregister_user(message: types.Message):
    """Short summary.

    :param types.Message message: .

    """
    if message.from_user and not message.from_user.is_bot:

        user = await UserWrapper.get(message.from_user.id)

        if not user:
            async_task(UserWrapper.add(message.from_user))
            await message.answer(msg.default_message)
        else:
            # await send_some_sticker(message, mood='happy')
            await message.answer(
                f"Привет, {message.from_user.get_mention(as_html=True)} 👋!",
                parse_mode=types.ParseMode.HTML,
    )
    else:

        await answer_robot_txt(message)
