# built-in
import asyncio
from datetime import datetime, timedelta

# third-party
from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from aiogram.dispatcher.filters import Regexp
from django.db.utils import IntegrityError

# local
from exceptions import NotAuthorizedError
from loader import dp, bot, EventManager
from orm import MemberWrapper, UserWrapper

from locbot.chatbot.utils.exception_utils import log
from handlers.addons import send_some_sticker, download_user_document, sticker_pack
from interface.verbose import msg, btns
from interface.kb.user_kb import m
from interface.callback import sign_up_data, confirm_data, accept_terms_data
from states.SignupState import SignupState
from utils.hints import ANYTYPE


@dp.message_handler(Regexp(r'^([а-яА-ЯеЁё]{2,25}\s)([а-яА-ЯеЁa-zA-Z]{3,25}\s*){1,2}$'), state=SignupState.SelectFullname)
async def registration_select_fullname(message: types.Message, state: FSMContext):

    splitted_name = [x.title() for x in message.text.split()]

    if len(splitted_name) == 2:
        # No patronymic name
        splitted_name.append("Нет")

    parsed_name = dict(zip(['last_name', 'first_name', 'patronymic_name'], splitted_name))

    await asyncio.gather(
        message.answer(msg.registration_step_1_confirm.format(**parsed_name), reply_markup=m.ConfirmFullname()),
        state.update_data(name=parsed_name, user_id=message.from_user.id),
    )


@dp.message_handler(state=SignupState.SelectFullname, content_types=ANYTYPE)
async def registration_bad_full_name(message: types.Message, state: FSMContext):
    await message.answer(msg.registration_step_1_failed)


@dp.callback_query_handler(confirm_data.filter(ctx="signup_fullname"), state=SignupState.SelectFullname)
async def registration_confirm_fullname(call: types.CallbackQuery, callback_data: dict, state: FSMContext):

    await asyncio.gather(
        call.message.delete_reply_markup(),
        call.message.answer(msg.registration_step_2, reply_markup=m.ShareContactKeyboard()),
        SignupState.SelectPhone.set()
    )


@dp.message_handler(state=SignupState.SelectPhone, content_types=types.ContentType.CONTACT)
async def registration_select_phone(message: types.Message, state: FSMContext):

    if not message.contact.user_id or message.contact.user_id != message.from_user.id:
        await message.answer(msg.registration_step_2_not_owner_of_contact)
        return None

    await asyncio.gather(
        bot.send_chat_action(message.chat.id, 'typing'),
        state.update_data(phone_number=message.contact.phone_number),
        SignupState.ReadTerms.set(),
        message.answer(msg.registration_step_3, reply_markup=types.ReplyKeyboardRemove()),
    )


    await message.answer(msg.terms_of_use, reply_markup=m.AcceptTerms())


@dp.message_handler(state=SignupState.SelectPhone, content_types=ANYTYPE)
async def registration_select_phone_failed(message: types.Message, state: FSMContext):

    await message.answer(msg.registration_step_2_not_owner_of_contact)


@dp.callback_query_handler(accept_terms_data.filter(a="1"), state=SignupState.ReadTerms)
async def registration_terms_accepted(call: types.CallbackQuery, callback_data: dict, state: FSMContext):

    # if datetime.now() - call.message.date < timedelta(seconds=8):
    #     await call.answer(msg.please_read_terms, show_alert=True)
    #     return None

    dct = await state.get_data()

    user = await UserWrapper.get(dct['user_id'])

    if user is None:
        await asyncio.gather(
            SignupState.ReadTerms.set(),
            message.answer(msg.registration_step_3),
        )
        raise NotAuthorizedError()

    new_member = await MemberWrapper.add(dct, user)

    await asyncio.gather(
        EventManager.new_event(
            header="Новый участник",
            content=f"{new_member} зарегистрировался в системе",
            type=1,
            action_required=True,
            additional_id=user.telegram_id,
        ),
        call.message.answer_sticker(sticker_pack['bear_dancing']),
        call.message.answer(msg.registration_completed),
        call.message.delete_reply_markup(),
    )
