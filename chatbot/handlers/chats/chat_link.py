import asyncio
from datetime import datetime, timedelta

from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from aiogram.dispatcher.handler import SkipHandler

from loader import dp, bot

from interface.callback import invalid_invite_link_data
from interface.verbose import msg
from interface.kb.member_kb import m


@dp.callback_query_handler(invalid_invite_link_data.filter())
async def reload_broken_link(call: types.CallbackQuery, callback_data: dict, state: FSMContext):

    times = int(callback_data['times']) + 1
    timestamp = int(callback_data['timestamp'])

    if times > 3:
        raise SkipHandler()

    if (datetime.now() - datetime.fromtimestamp(timestamp)) > timedelta(hours=2):
        return await call.answer(msg.member.link_expired)

    chat_link = await bot.export_chat_invite_link(callback_data['id'])
    # chat_link = call.message.reply_markup['inline_keyboard'][0][0]['url']

    await asyncio.gather(
        call.answer("Всё работает!"),
        call.message.edit_reply_markup(m.GetInviteButton(
            invite_link=chat_link,
            chat_id=callback_data['id'],
            times=times,
            timestamp=timestamp,
            )
        ),
    )


@dp.callback_query_handler(invalid_invite_link_data.filter())
async def link_reloaded_too_many_times(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(msg.member.link_cannot_be_reloaded)
