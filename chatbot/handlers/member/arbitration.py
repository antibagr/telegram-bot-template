import asyncio
from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from aiogram.utils.markdown import quote_html

from loader import dp, CarriersQueue, CarrierAppointment, EventManager


from manager.models import OrderModel, EventChoice, OrderStatusChoices

from orm import MemberWrapper, OrderWrapper

from handlers.addons import retrieve_order, notify_customer, carrier_was_changed

from interface.callback import delivery_data, offer_data, arbitration_data
from interface.verbose import msg
from interface.kb.member_kb import m

from states.DeliveryState import DeliveryState
from states.CustomerState import CustomerState

from utils.func import tag
from utils.hints import ANYTYPE


@dp.callback_query_handler(delivery_data.filter(checkpoint='arrived_troubleshoot'))
@dp.callback_query_handler(delivery_data.filter(checkpoint='processing_troubleshoot'))
@dp.callback_query_handler(delivery_data.filter(checkpoint='payment_troubleshoot'))
async def arbitraty(call: types.CallbackQuery, callback_data: dict, state: FSMContext):

    order_id, order = await retrieve_order(callback_data)

    if order.cancelled:
        return await call.message.edit_text(msg.member.order_cancelled.format(order=order))
    elif order.status in (OrderStatusChoices.Arbitration, OrderStatusChoices.Failed, OrderStatusChoices.Cancelled, OrderStatusChoices.Finished,):
        return await call.answer(msg.call.restricted)
    elif await carrier_was_changed(order, call):
        return None

    await asyncio.gather(

        state.update_data(order_id=order_id),
        # CarriersQueue.remove_carrier(call.message.chat.id),
        call.message.delete_reply_markup(),
        call.message.answer(msg.member.open_arb),
        DeliveryState.Arbitration.set(),
    )


@dp.message_handler(state=DeliveryState.Arbitration)
async def arbitraty_message(message: types.Message, state: FSMContext):

    data = await state.get_data()

    order_id, order = await retrieve_order(data)

    carrier = await MemberWrapper.get_or_exception(telegram_id=message.from_user.id)

    previous_status = order.status

    step = {
        1: 'Исполнитель уточняет информацию',
        2: 'Исполнитель направляется на адрес',
        3: 'Исполнитель выполняет заказ',
        4: 'Заказ завершён. Оплата'

    }[previous_status]

    await asyncio.gather(
        notify_customer(order, OrderStatusChoices.Arbitration),
        EventManager.new_event(
            header=msg.event.arb_header.format(state=previous_status),
            content=msg.event.arb_content.format(carrier=carrier, state=step, details=message.text),
            type=EventChoice.Arbitration,
            action_required=True,
            order=order,
            details=message.text,
        ),
        state.finish(),
        message.answer(msg.carrier.arbitration_started),
    )


@dp.callback_query_handler(arbitration_data.filter())
async def customer_opens_arbitration(call: types.CallbackQuery, callback_data: dict, state: FSMContext):

    order_id, order = await retrieve_order(callback_data)

    if order.status not in (OrderStatusChoices.Completed, OrderStatusChoices.PaymentInfo):
        return await call.message.edit_text(msg.member.cannot_open_arb.format(order=order))

    await asyncio.gather(
        state.update_data(order_id=order_id),
        call.message.edit_text("\n\n".join( (
                order.get_status(),
                order.get_full_information(html=True),
                tag(msg.member.open_arb, 'i')
            )
        ), reply_markup=m.GetBackToOrder(order)),
        CustomerState.Arbitration.set(),
    )


@dp.message_handler(state=CustomerState.Arbitration)
async def customer_sent_arbitration_details(message: types.Message, state: FSMContext):

    data = await state.get_data()
    order_id, order = await retrieve_order(data)

    await asyncio.gather(
        EventManager.new_event(
            header=msg.event.arb_payment,
            content=msg.event.arb_content.format(carrier=order.carrier, state=order.get_status(), details=message.text),
            type=EventChoice.Arbitration,
            action_required=True,
            order=order,
            details=message.text,
        ),
        message.answer(msg.member.arbitration_started.format(order=order)),
        state.finish(),
    )
