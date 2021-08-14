import logging
import asyncio
from datetime import datetime
from asgiref.sync import sync_to_async

from aiogram import types
from aiogram.utils.exceptions import InvalidQueryID
from aiogram.dispatcher.storage import FSMContext


from loader import dp, bot, CarrierAppointment, EventManager, DeliveryTimer

from manager.models import OrderModel, MemberModel, EventChoice, ChatModel, OrderStatusChoices
from orm import MemberWrapper, OrderWrapper

from handlers.addons import retrieve_order, notify_customer
from handlers.chats.chats import setup_dialog_chat
from handlers.errors.send_exception import send_exception

from states.DeliveryState import DeliveryState

from interface.callback import offer_data
from interface.verbose import msg, btns
from interface.kb.member_kb import m

from utils.TeleAPI import TelethonClass
from utils.func import tag


async def get_order_chat(order: OrderModel, carrier: MemberModel):

    if order.chat:
        order_chat_id = order.chat.id
        invite_link = await bot.export_chat_invite_link(order_chat_id)

    else:

        while True:
            try:
                order_chat_id, invite_link = await setup_dialog_chat(order, carrier.telegram_id)
            except Exception as e:
                await send_exception(e)
                await asyncio.sleep(5)
            else:
                break

    await (await bot.get_chat(order_chat_id)).unban(carrier.telegram_id, only_if_banned=True)

    return order_chat_id, invite_link


@dp.callback_query_handler(offer_data.filter(action='accept'))
async def accept_new_order(call: types.CallbackQuery, callback_data: dict):

    carrier = await MemberWrapper.get(telegram_id=call.message.chat.id)

    try:
        order_id, order = await retrieve_order(callback_data)
    except OrderModel.DoesNotExist:
        order_id = int(callback_data.get('order_id'))
        await call.message.edit_text(msg.carrier.order_not_found.format(order_id=order_id))
        CarrierAppointment.discard_offer(call.message.chat.id, order_id, is_backup=carrier.is_backup)
        return None

    if order.status and order.status != OrderStatusChoices.Failed:
        CarrierAppointment.discard_offer(call.message.chat.id, order_id, is_backup=carrier.is_backup)
        return await call.answer(msg.carrier.order_not_available.format(order_id=order_id))

    if order.cancelled:
        return await call.message.edit_text(msg.member.order_cancelled.format(order=order))

    order = await OrderWrapper.update(order, status=OrderStatusChoices.CarrierFound, carrier=carrier)

    try:
        order_chat_id, invite_link = await get_order_chat(order, carrier)
    except Exception as e:
        return await asyncio.gather(
            OrderWrapper.update(order, status=OrderStatusChoices.Created),
            send_exception(e),
            call.answer(msg.err.cannot_create_chat),
        )

    CarrierAppointment.accept_offer(call.message.chat.id, order_id)

    await asyncio.gather(
        EventManager.new_event(
            header=msg.event.carr_found_header,
            content=msg.event.carr_found_content.format(carrier=carrier, order=order),
            type=EventChoice.OrderChosen,
            additional_id=order_id,
        ),
        notify_customer(order, OrderStatusChoices.CarrierFound),
        DeliveryState.ConfirmInformation.set(),
        call.message.edit_text(msg.carrier.offed_applied.format(id=order_id, order=order.get_full_information(html=True)), reply_markup=m.GetConfirmationKeyboard(order_id)),
        call.message.answer_location(latitude=order.location[0], longitude=order.location[1]),
        call.message.answer(
            msg.member.chat_for_carrier,
            reply_markup=m.GetInviteButton(invite_link, order_chat_id, timestamp=round(datetime.now().timestamp())),
            disable_web_page_preview=True,
        ),
    )

    try:
        await call.answer(msg.call.accepted)
    except:
        pass


@dp.callback_query_handler(offer_data.filter(action='reject'))
async def reject_new_order(call: types.CallbackQuery, callback_data: dict):

    order_id, order = await retrieve_order(callback_data)
    carrier = await MemberWrapper.get_or_exception(telegram_id=call.message.chat.id)

    if not order.cancelled:
        CarrierAppointment.discard_offer(call.message.chat.id, order_id, is_backup=carrier.is_backup)

    await asyncio.gather(
        call.message.edit_text(msg.carrier.order_rejected.format(order=order)),
        call.answer(msg.call.order_rejected),
        call.message.unpin(),
    )


@dp.callback_query_handler(offer_data.filter(action='confirm'))
async def confirm_new_order(call: types.CallbackQuery, callback_data: dict):

    order_id, order = await retrieve_order(callback_data)
    carrier = await MemberWrapper.get_or_exception(telegram_id=call.message.chat.id)

    if order.cancelled:
        return await call.message.edit_text(msg.member.order_cancelled.format(order=order))

    markup = m.ArrivedMarkup(order_id)

    if not carrier.is_backup:
        DeliveryTimer.start_watching_delivery(call.message.chat.id, order_id)

    await asyncio.gather(
        OrderWrapper.update(order, carrier=carrier, status=OrderStatusChoices.Processing),
        notify_customer(order, OrderStatusChoices.Processing),
        EventManager.new_event(
            header=msg.event.order_confirmed_header,
            content=msg.event.order_confirmed_content.format(carrier=carrier, order=order),
            type=EventChoice.CarrierChosen,
            additional_id=order_id,
        ),
        DeliveryState.StartDelivering.set(),
        call.message.delete_reply_markup(),
        call.message.answer(msg.carrier.offer_confirmed.format(title=order.title), reply_markup=markup),
        call.answer(btns.confirmed),
    )


@dp.callback_query_handler(offer_data.filter(action='not_confirm'))
async def order_not_confirmed(call: types.CallbackQuery, callback_data: dict, state: FSMContext):

    order_id, order = await retrieve_order(callback_data)
    carrier = await MemberWrapper.get_or_exception(telegram_id=call.message.chat.id)

    if order.cancelled:
        return await call.message.edit_text(msg.member.order_cancelled.format(order=order))

    CarrierAppointment.discard_offer(carrier.telegram_id, order_id, is_backup=carrier.is_backup)

    await asyncio.gather(
        OrderWrapper.update(order, carrier=None, status=OrderStatusChoices.Created),
        notify_customer(order, -1),
        call.message.delete_reply_markup(),
    )

    aiogram_chat = await bot.get_chat(order.chat.id)
    await aiogram_chat.kick(carrier.telegram_id)
