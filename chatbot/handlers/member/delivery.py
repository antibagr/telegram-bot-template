import asyncio
from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from aiogram.utils.markdown import quote_html

from typing import Tuple

from loader import dp, bot, CarriersQueue, CarrierAppointment, EventManager, DeliveryTimer

from manager.models import OrderModel, EventChoice, OrderStatusChoices

from orm import MemberWrapper, OrderWrapper

from orders.geo import Location

from states.DeliveryState import DeliveryState
from states.CarrierState import CarrierSessionState

from interface.callback import delivery_data, delivery_timer_data
from interface.verbose import msg
from interface.kb.member_kb import m

from utils.func import tag
from utils.hints import ANYTYPE

from handlers.addons import retrieve_order, notify_customer, carrier_was_changed
from handlers.chats.chats import kick_all_members



@dp.callback_query_handler(delivery_timer_data.filter())
async def carrier_is_late(call: types.CallbackQuery, callback_data: dict, state: FSMContext):

    DeliveryTimer.carrier_back_online(call.message.chat.id)

    await asyncio.gather(
        call.answer(msg.carrier.lateness_clicked),
        call.message.delete(),
    )


@dp.callback_query_handler(delivery_data.filter(checkpoint='arrived'))
async def carrier_arrived(call: types.CallbackQuery, callback_data: dict, state: FSMContext):

    order_id, order = await retrieve_order(callback_data)

    if await carrier_was_changed(order, call):
        return

    if order.cancelled:
        return await call.message.edit_text(msg.member.order_cancelled.format(order=order))
    elif order.status != OrderStatusChoices.Processing:
        return await call.answer(msg.call.restricted)

    carrier_location = CarriersQueue.get_location(call.message.chat.id)
    carrier = await MemberWrapper.get_or_exception(telegram_id=call.message.chat.id)

    if not carrier_location:
        return await call.answer(msg.carrier.cannot_receive_location, show_alert=True)

    # if False: # await Location.get_distance(carrier_location, order.location) > 1:
    #     data = await state.get_data()
    #     if 'arr_msg_sent' not in data:
    #         await asyncio.gather(
    #             state.update_data(arr_msg_sent=True),
    #             call.message.answer(msg.carrier.too_far_from_checkpoint),
    #             call.answer(),
    #         )
    #     else:
    #         await call.answer(msg.carrier.too_far_from_checkpoint_short, show_alert=True)
    #
    #     return None

    DeliveryTimer.carrier_back_online(call.message.chat.id)

    await OrderWrapper.update(order, status=OrderStatusChoices.CarrierArrived, carrier=carrier)

    await asyncio.gather(
        DeliveryState.ProcessingOrder.set(),
        notify_customer(order, OrderStatusChoices.CarrierArrived),
        EventManager.new_event(
            header=msg.event.carr_arrived_header,
            content=msg.event.carr_arrived_content.format(carrier=carrier, order=order),
            type=EventChoice.CarrierArrived,
            additional_id=order_id,
        ),
        call.message.edit_text(msg.carrier.processing_order, reply_markup=m.ProcessingOrderMarkup(order_id)),
        call.answer(),
    )

@dp.callback_query_handler(delivery_data.filter(checkpoint='processing'))
async def order_completed(call: types.CallbackQuery, callback_data: dict, state: FSMContext):

    order_id, order = await retrieve_order(callback_data)

    if await carrier_was_changed(order, call):
        return

    await asyncio.gather(
        notify_customer(order, OrderStatusChoices.Completed),
        state.update_data(order_id=order_id),
        DeliveryState.PaymentInfo.set(),
        call.message.edit_text(msg.carrier.payment_info, reply_markup=m.PaymentMarkup(order_id)),
    )


@dp.message_handler(state=DeliveryState.PaymentInfo)
async def payment_information(message: types.Message, state: FSMContext):

    carrier = await MemberWrapper.get_or_exception(telegram_id=message.chat.id)

    data = await state.get_data()

    order_id, order = await retrieve_order(data)

    details = quote_html(message.text[:2048])

    CarrierAppointment.discard_offer(message.chat.id, order_id, is_backup=carrier.is_backup)

    if await carrier_was_changed(order, message):
        await state.finish()
        return

    await OrderWrapper.update_status(order, OrderStatusChoices.PaymentInfo)

    await asyncio.gather(
        MemberWrapper.update(carrier, rating=carrier.rating + 1),
        EventManager.new_event(
            header=msg.event.carr_completed_header,
            content=msg.event.carr_completed_content.format(carrier=carrier, order=order, details=details),
            type=EventChoice.OrderDone,
            additional_id=order_id,
        ),
        CarrierSessionState.OnDuty.set(),
        notify_customer(order, OrderStatusChoices.PaymentInfo, details=details),
        message.answer(msg.carrier.order_delivered),
        kick_all_members(order),
    )



@dp.message_handler(state=DeliveryState.PaymentInfo, content_types=ANYTYPE)
async def payment_information(message: types.Message, state: FSMContext):
    await message.answer(msg.carrier.payment_info_failed)
