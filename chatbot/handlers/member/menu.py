import asyncio
import logging

from datetime import datetime, timedelta

from aiogram import types
from aiogram.dispatcher.handler import SkipHandler
from aiogram.dispatcher.storage import FSMContext
from aiogram.utils.exceptions import MessageToDeleteNotFound, MessageCantBeDeleted

from loader import dp, bot, CarriersQueue, CarrierAppointment

from exceptions import NotAuthorizedError

from manager.models import OrderModel

from interface.verbose import msg, btns
from interface.kb.member_kb import m
from interface.callback import menu_data, dropdown_menu_data, cancel_data

from orm import MemberWrapper
from states.OrderState import OrderState
from states.CarrierState import CarrierSessionState

from utils.func import to_json
from utils.hints import ANYTYPE
from utils.exception_utils import log

from handlers.shared.user_menu import edit_message_to_private_menu


@dp.message_handler(
    chat_type=types.ChatType.PRIVATE,
    content_types='location',
    state=CarrierSessionState.WaitingLocationMessage)
async def location_message_received(message: types.Message) -> None:

    if not message.location.live_period:
        return await message.answer(msg.carrier.live_location_required)

    member = await MemberWrapper.get(message.from_user.id)

    if not member or not member.can_deliver():
        raise NotAuthorizedError()


    current_offer = message.from_user.id in CarrierAppointment.current_offer

    await asyncio.gather(
        # bot.pin_chat_message(message.chat.id, message.message_id, disable_notification=True),
        CarrierSessionState.OnDuty.set(),
        message.answer(msg.menu, reply_markup=m.GetMenu(1, current_offer=current_offer)),
        MemberWrapper.update(member, is_on_duty=True),
        CarriersQueue.carrier_activated(message, member),
    )


@dp.edited_message_handler(
    # state=CarrierSessionState.OnDuty,
    chat_type=types.ChatType.PRIVATE,
    content_types='location')
async def update_carrier_location(message: types.Message) -> None:

    await CarriersQueue.update_current_location(message)


@dp.callback_query_handler(menu_data.filter(action='status', s='0'))
async def carrier_start_session(call: types.CallbackQuery, callback_data: dict):

    logging.info(f"Carrier {call.message.chat.id} is about to start session")

    text = msg.carrier.enable_location
    if call.message.chat.id in CarriersQueue._inactive_updates:
        text += '\n\n' + msg.carrier.inactive_updater

    member = await MemberWrapper.get(call.message.chat.id)

    if not member:
        raise NotAuthorizedError()

    if not member.is_approved:
        await call.answer(msg.call.restricted)
        return await call.message.answer(msg.wait_for_approve)
    elif not member.is_carrier:
        return await call.answer(msg.call.not_a_carrier)
    elif member.is_deleted:
        return await call.answer(msg.call.account_deleted)


    """ MOCKING """
    # await CarriersQueue.carrier_activated_directly(member, live_period=900)
    # CarriersQueue._carriers_location[member.telegram_id] = (59.9150517,30.3158993)
    # await call.answer("On duty")

    await asyncio.gather(
        CarrierSessionState.WaitingLocationMessage.set(),
        call.message.edit_text(text, reply_markup=m.ShowTutorial()),
    )


@dp.callback_query_handler(menu_data.filter(action='status', s='1'))
async def carrier_end_session(call: types.CallbackQuery, callback_data: dict):

    chat_id = call.message.chat.id

    member = await MemberWrapper.get(chat_id)

    current_offer = chat_id in CarrierAppointment.current_offer

    await asyncio.gather(
        CarriersQueue.remove_carrier(chat_id),
        call.message.edit_reply_markup(reply_markup=m.GetMenu(0, current_offer=current_offer)),
        MemberWrapper.update(member, is_on_duty=False),
    )


@dp.callback_query_handler(dropdown_menu_data.filter(cat='car_tut', s='1'))
async def carrier_show_tutorial(call: types.CallbackQuery, callback_data: dict):

    await call.message.edit_text("\n\n".join([call.message.text, msg.carrier.tutorial]), reply_markup=m.HideTutorial())


@dp.callback_query_handler(dropdown_menu_data.filter(cat='car_tut', s='0'))
async def carrier_hide_tutorial(call: types.CallbackQuery, callback_data: dict):

    text = msg.carrier.enable_location
    if call.message.chat.id in CarriersQueue._inactive_updates:
        text += '\n\n' + msg.carrier.inactive_updater

    await call.message.edit_text(text, reply_markup=m.ShowTutorial())


@dp.callback_query_handler(cancel_data.filter(ctx='car_ses'))
async def carrier_cancel_session(call: types.CallbackQuery, callback_data: dict, state: FSMContext):

    current_offer = call.message.chat.id in CarrierAppointment.current_offer

    markup = m.GetMenu(0, current_offer=current_offer)

    await asyncio.gather(
        call.answer(msg.cancelled),
        call.message.edit_text(msg.menu, reply_markup=markup),
    )


@dp.callback_query_handler(menu_data.filter(action='order'))
async def make_new_order(call: types.CallbackQuery, callback_data: dict):

    member = await MemberWrapper.get(call.message.chat.id)

    if member:
        if member.is_approved:
            await asyncio.gather(
                call.message.edit_text(msg.member.select_title, reply_markup=m.ReturnToMenu()),
                OrderState.SelectTitle.set()
            )
        else:
            await call.message.answer(msg.wait_for_approve)
    else:
        await call.message.answer("Error")


@dp.callback_query_handler(menu_data.filter(action='cancel'), state="*")
async def edit_message_to_private_menu(call: types.CallbackQuery, state: FSMContext) -> None:

    member = await MemberWrapper.get(call.message.chat.id)

    current_offer = call.message.chat.id in CarrierAppointment.current_offer

    if not member:
        resp = msg.call.error
        await call.message.reply(msg.sign_up_overview)
    elif not member.is_approved:
        resp = msg.call.error
        await call.message.answer(msg.wait_for_approve)
    else:
        resp = ""
        await call.message.edit_text(msg.menu, reply_markup=m.GetMenu(member.is_on_duty, current_offer=current_offer))

    await call.answer(resp)

    # if state is not None:
    #     await state.finish()
