import asyncio

from aiogram import types

from asgiref.sync import sync_to_async
from manager.models import OrderModel, EventChoice, ChatModel
from utils.TeleAPI import TelethonClass
from aiogram.utils.exceptions import ChatNotFound
from loader import bot
from interface.kb.member_kb import m

from datetime import datetime
from typing import Tuple


async def kick_all_members(order: OrderModel) -> None:

    if not order.chat:
        return

    aiogram_chat = await bot.get_chat(order.chat.id)

    for participant in await TelethonClass.get_all_members(order.chat.id):
        await aiogram_chat.kick(participant.id)
        await aiogram_chat.unban(participant.id)


async def get_order_chat(order: OrderModel) -> Tuple[ChatModel, types.Chat]:

    free_chat = await sync_to_async(ChatModel.objects.filter)(order__isnull=True)
    if free_chat:
        free_chat = free_chat[0]

        aiogram_chat = await bot.get_chat(free_chat.id)

        if aiogram_chat.title != f"Заказ {order}":
            await aiogram_chat.set_title(f"Заказ {order}")

        if aiogram_chat.description != order.get_description():
            await aiogram_chat.set_description(order.get_description())

        try:
            chat_members = await TelethonClass.get_all_members(free_chat.id)
        except ValueError:
            await sync_to_async(free_chat.delete)()
            raise

        for participant in await TelethonClass.get_all_members(free_chat.id):

            if (order.customer and participant.id == order.customer.telegram_id) or \
                (order.carrier and participant.id == order.carrier.telegram_id):
                continue

            await aiogram_chat.kick(participant.id)

        order.chat = free_chat
        await sync_to_async(order.save)()

        new_chat = free_chat

    else:

        new_chat_id = await TelethonClass.create_private_chat(order)
        aiogram_chat = await bot.get_chat(new_chat_id)

        new_chat = await sync_to_async(ChatModel.objects.create)(id=new_chat_id, order=order)

    return new_chat, aiogram_chat


async def setup_dialog_chat(order: OrderModel, user_id: int) -> Tuple[int, str]:

    chat, aiogram_chat = await get_order_chat(order)

    try:
        invite_link = await aiogram_chat.export_invite_link()
    except ChatNotFound:
        chat.delete()
        return await setup_dialog_chat(order, user_id)

    await aiogram_chat.unban(user_id, only_if_banned=True)

    return (chat.id, invite_link)
