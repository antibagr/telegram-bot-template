import asyncio

import random

from datetime import datetime, timedelta

from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from aiogram.dispatcher.handler import SkipHandler

from manager.models import OrderModel

from loader import dp, OrderDispatcher, CarriersQueue, EventManager

from interface.verbose import msg, cmd
from interface.kb.member_kb import m
from orm import MemberWrapper, OrderWrapper
from manager.models import EventChoice
from states.OrderState import OrderState

from utils.async_func import async_task
from utils.exception_utils import log


@dp.message_handler(state=OrderState.SendLocation, content_types='location')
async def create_new_order(message: types.Message, state):

    if message.location.live_period:
        return await message.answer("Пожалуйста, пришлите точку на карте, а не Live Location")

    await state.finish()

    # order_id = message.message_id
    # order_location = (message.location.latitude, message.location.longitude)

    order = OrderWrapper._model.objects.last()
    OrderDispatcher.add_order(order)


    await message.answer("order created!")
    await EventManager.new_event(
        header="Новый заказ",
        content=f'Добавлен заказ "{order.title}"',
        type=EventChoice.NewOrder,
        action_required=False,
    )



@dp.message_handler(commands=cmd.order)
async def make_new_order(message: types.Message):

    member = await MemberWrapper.get(message.from_user.id)

    if member:
        if member.is_approved:
            await asyncio.gather(
                message.answer(msg.member.select_title, reply_markup=m.ReturnToMenu()),
                OrderState.SelectTitle.set(),
            )
        else:
            await message.answer(msg.wait_for_approve)

    else:
        raise SkipHandler()


@dp.message_handler(commands=cmd.cancel, state=OrderState.All)
async def cancel_new_order(message: types.Message, state: FSMContext):
    await asyncio.gather(
        message.answer(msg.member.order_cancelled),
        state.reset_state(with_data=True)
    )
