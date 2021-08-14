import asyncio
from aiogram import types
from aiogram.dispatcher.storage import FSMContext

from loader import dp

from interface.verbose import msg, cmd
from interface.kb.user_kb import m
from states.SignupState import SignupState
from interface.callback import accept_terms_data
from handlers.addons import create_user_if_not_exists

from utils.async_func import async_task

from orm import UserWrapper, MemberWrapper


@dp.message_handler(commands=cmd.cancel, state=SignupState.All, chat_type=types.ChatType.PRIVATE)
async def cancel_signup(message: types.Message, state: FSMContext):
    await asyncio.gather(
        message.answer(msg.registration_cancelled, reply_markup=types.ReplyKeyboardRemove()),
        state.reset_state(with_data=True)
    )



@dp.callback_query_handler(accept_terms_data.filter(a="0"), state=SignupState.ReadTerms)
async def cancel_signup_from_terms(call: types.CallbackQuery, callback_data: dict, state: FSMContext):

    await asyncio.gather(
        call.message.delete_reply_markup(),
        cancel_signup(call.message, state)
    )


@dp.message_handler(commands=cmd.signup, state='*', chat_type=types.ChatType.PRIVATE)
async def start_signup(message: types.Message, state: FSMContext):

    create_user_if_not_exists(message.from_user)

    member = await MemberWrapper.get(message.from_user.id)

    if member:
        if member.is_approved:
            await message.answer(msg.already_a_member_approved)
        else:
            await message.answer(msg.already_a_member)

        return None

    await asyncio.gather(
        message.answer(msg.registration_step_1),
        SignupState.SelectFullname.set()
    )
