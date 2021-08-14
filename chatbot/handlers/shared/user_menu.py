from typing import Optional

from aiogram import types
from aiogram.dispatcher.storage import FSMContext

from interface.verbose import msg
from interface.kb.member_kb import m

from orm import MemberWrapper


async def send_private_menu(message: types.Message) -> None:

    member = await MemberWrapper.get(message.from_user.id)

    if member:
        if member.is_approved:
            markup = m.GetMenu(member.is_on_duty)
            await message.answer(msg.menu, reply_markup=markup)
        else:
            await message.answer(msg.wait_for_approve)

    else:

        await message.reply(msg.sign_up_overview)


async def edit_message_to_private_menu(call: types.CallbackQuery, state: Optional[FSMContext] = None) -> None:

    member = await MemberWrapper.get(call.message.chat.id)

    if not member:

        resp = msg.call.error
        await call.message.reply(msg.sign_up_overview)

    elif not member.is_approved:

        resp = msg.call.error
        await call.message.answer(msg.wait_for_approve)

    else:

        resp = ""
        await call.message.edit_text(msg.menu, reply_markup=m.GetMenu(member.is_on_duty))

    await call.answer(resp)

    if state is not None:
        await state.finish()
