from aiogram import types

from loader import dp, CarrierAppointment

from interface.verbose import msg, cmd
from interface.kb.member_kb import m

from orm import MemberWrapper


@dp.message_handler(commands=cmd.menu, chat_type=types.ChatType.PRIVATE, state='*')
async def send_private_menu(message: types.Message) -> None:

    member = await MemberWrapper.get(message.from_user.id)

    current_offer = message.from_user.id in CarrierAppointment.current_offer

    if member:
        if member.is_approved:
            markup = m.GetMenu(member.is_on_duty, current_offer=current_offer)
            await message.answer(msg.menu, reply_markup=markup)
        else:
            await message.answer(msg.wait_for_approve)

    else:

        await message.reply(msg.sign_up_overview)
