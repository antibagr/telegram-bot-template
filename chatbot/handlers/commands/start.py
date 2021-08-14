import asyncio
import logging

from aiogram import types
from aiogram.dispatcher.filters import CommandStart

from loader import dp
from orm import UserWrapper

from interface.verbose import msg

from utils.async_func import async_task

from handlers.user.unregister import answer_robot_txt
from handlers.addons import send_some_sticker

from handlers.addons import create_user_if_not_exists

from orm import UserWrapper, MemberWrapper


@dp.message_handler(CommandStart(), chat_type=types.ChatType.PRIVATE)
async def start_command_called(message: types.Message) -> None:

    if not message.from_user or message.from_user.is_bot:
        await answer_robot_txt(message)
        return None

    create_user_if_not_exists(message.from_user)

    member = await MemberWrapper.get(message.from_user.id)

    if member:
        if member.is_approved:
            await message.answer(msg.service_overview)
        else:
            await message.answer(msg.wait_for_approve)

    else:
        await send_some_sticker(message, "hello")
        await message.answer(msg.sign_up_overview)
