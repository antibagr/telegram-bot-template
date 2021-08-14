import asyncio
from aiogram import types
from asgiref.sync import sync_to_async
from aiogram.dispatcher.storage import FSMContext

from loader import dp, CarrierAppointment, EventManager

from manager.models import OrderModel, MemberModel, OrderStatusChoices, EventChoice
from orm import MemberWrapper, OrderWrapper

from interface.verbose import msg, btns
from interface.callback import menu_data, order_info_data
from interface.kb.member_kb import m

from states.CustomerState import CustomerState


@dp.callback_query_handler(menu_data.filter(action='my_orders'))
async def show_member_orders(call: types.CallbackQuery, callback_data: dict, state: FSMContext):

    member_id = call.message.chat.id

    if await OrderWrapper.count_orders(customer_id=member_id):

        orders = await sync_to_async(OrderModel.objects.filter)(customer_id=member_id)

        await call.message.edit_text(
            msg.member.orders_list,
            reply_markup=m.ListOrders(orders),
        )


    else:
        await call.answer(msg.carrier.orders_empty)



@dp.callback_query_handler(menu_data.filter(action='carrier_orders'))
async def show_member_offers(call: types.CallbackQuery, callback_data: dict, state: FSMContext):

    member = await MemberWrapper.get_or_exception(telegram_id=call.message.chat.id)

    if not member.can_deliver():
        return await call.answer(msg.call.not_a_carrier)

    carrier_orders = await sync_to_async(OrderModel.objects.filter(carrier=member).order_by)('-created_at')

    if not carrier_orders:
        return await call.answer(msg.carrier.orders_empty)


    await call.message.edit_text(
        msg.member.orders_list,
        reply_markup=m.ListOfCarrierOrders(carrier_orders),
    )


@dp.callback_query_handler(order_info_data.filter(role='cstm_cancel_state'))
async def show_selected_order(call: types.CallbackQuery, callback_data: dict, state: FSMContext):

    callback_data['role'] = 'cstm'

    await asyncio.gather(
        state.finish(),
        show_selected_order(call, callback_data, state),
    )


@dp.callback_query_handler(order_info_data.filter())
async def show_selected_order(call: types.CallbackQuery, callback_data: dict, state: FSMContext):

    try:
        order = await OrderWrapper.get(id=int(callback_data['id']))
    except Exception:
        await call.message.edit_text(msg.err.order_unavailable, reply_markup=m.BackToOrders())
        raise

    if state == CustomerState.Arbitration:
        await state.finish()

    await call.message.edit_text(
        order.get_status() + "\n\n" + order.get_full_information(html=True),
        reply_markup=m.BackToOrders(order, role=callback_data.get('role')),
    )


@dp.callback_query_handler(menu_data.filter(action='payment_received'))
async def payment_received(call: types.CallbackQuery, callback_data: dict, state: FSMContext):

    try:
        order = await OrderWrapper.get(id=int(callback_data.get('s')))
    except Exception:
        await call.answer(msg.call.cannot_find_order, show_alert=True)
        raise

    await asyncio.gather(
        OrderWrapper.update(order, status=OrderStatusChoices.Finished),
        EventManager.new_event(
            header=msg.event.payment_received_header,
            content=msg.event.payment_received_content.format(order=order),
            type=EventChoice.PaymentReceived,
            additional_id=order.id,
        ),
        call.message.edit_reply_markup(m.BackToOrders(role='cstm')),
        call.answer(msg.call.payment_received),
    )


@dp.callback_query_handler(menu_data.filter(action='cancel-order'))
async def cancel_order(call: types.CallbackQuery, callback_data: dict, state: FSMContext):

    order = await OrderWrapper.get_or_exception(pk=int(callback_data.get('s')))

    if not order.status:
        return await call.answer(msg.member.cannot_cancel_order, show_alert=True)

    await OrderWrapper.update(order, status=OrderStatusChoices.Cancelled, cancelled=True)
    await CarrierAppointment.cancel_order(order)
