# built-in
import asyncio
from datetime import datetime, timedelta

# third-party
from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from aiogram.dispatcher.filters import Regexp
from aiogram.dispatcher.handler import SkipHandler

from django.db.utils import IntegrityError


from manager.models import EventChoice
from orm import OrderWrapper

from loader import dp, bot, EventManager, OrderDispatcher
from exceptions import GoogleAPIException

from orders.geo_api import get_prediction_list, get_coordinates_from_text, get_reverse_geocoding

from interface.verbose import msg, btns
from interface.kb.member_kb import m
from interface.callback import gender_data, location_markup_data, confirm_location_data

from states.OrderState import OrderState
from utils.hints import ANYTYPE, TEXTTYPE, Serializable
from utils.async_func import async_task

from handlers.chats.chats import get_order_chat, setup_dialog_chat



@dp.message_handler(Regexp(r'^(.){8,128}$'), state=OrderState.SelectTitle)
async def order_select_title(message: types.Message, state: FSMContext):
    await asyncio.gather(
        state.update_data(title=message.text.title()),
        message.answer(msg.member.select_fullname),
        OrderState.SelectFullname.set()
    )


@dp.message_handler(state=OrderState.SelectTitle, content_types=ANYTYPE)
async def order_select_title_failed(message: types.Message, state: FSMContext):
    await message.answer(msg.member.select_title_failed)


@dp.message_handler(state=OrderState.SelectFullname)
async def order_select_fullname(message: types.Message, state: FSMContext):
    await asyncio.gather(
        state.update_data(full_name=message.text),
        message.answer(msg.member.select_gender, reply_markup=m.GetGenderSelection()),
        OrderState.SelectGender.set()
    )


@dp.message_handler(state=OrderState.SelectFullname, content_types=ANYTYPE)
async def order_select_fullname_failed(message: types.Message, state: FSMContext):
    await message.answer(msg.member.select_fullname_failed)


@dp.callback_query_handler(gender_data.filter(), state=OrderState.SelectGender)
async def order_select_gender(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await asyncio.gather(
        state.update_data(gender=callback_data.get('g')),
        call.message.delete_reply_markup(),
        call.message.answer(msg.member.select_age),
        OrderState.SelectAge.set()
    )


@dp.message_handler(lambda message: message.text.isdigit(), state=OrderState.SelectAge)
async def order_select_age(message: types.Message, state: FSMContext):

    if int(message.text) >= 100:
        return await message.answer(msg.member.wrong_age)

    await asyncio.gather(
        state.update_data(age=message.text),
        message.answer(msg.member.select_phone),
        OrderState.SelectPhone.set()
    )


@dp.message_handler(state=OrderState.SelectAge, content_types=ANYTYPE)
async def order_select_age_failed(message: types.Message, state: FSMContext):
    await message.answer(msg.member.select_age_failed)


@dp.message_handler(Regexp(r'^([\d\,\s\-\+]){8,20}$'), state=OrderState.SelectPhone)
async def order_select_phone(message: types.Message, state: FSMContext):
    await asyncio.gather(
        state.update_data(phone_number=message.text),
        message.answer(msg.member.select_location),
        OrderState.SelectAddress.set()
    )


@dp.message_handler(state=OrderState.SelectPhone, content_types=ANYTYPE)
async def order_select_phone_failed(message: types.Message, state: FSMContext):
    await message.answer(msg.member.select_phone_failed)


@dp.message_handler(state=OrderState.SelectAddress, content_types=TEXTTYPE)
async def order_select_location_with_text(message: types.Message, state: FSMContext):

    user_input = message.text[:300]

    locations_json = await get_prediction_list(user_input)
    status = locations_json['status']

    if status == 'ZERO_RESULTS':
        return await message.answer(msg.member.select_location_no_results)
    elif status != 'OK':
        await message.answer(msg.err.google_api_error)
        raise GoogleAPIException(user_input=user_input, response=locations_json)

    markup = m.GetLocationMarkup(locations_json)

    await message.answer(msg.member.select_location_markup, reply_markup=markup)


@dp.message_handler(state=OrderState.SelectAddress, content_types=['location', 'venue'])
async def order_select_location_by_geo(message: types.Message, state: FSMContext):
    if message.location.live_period is not None:
        return await message.answer(msg.member.select_location_is_live_location)

    location = {'lat': message.location.latitude, 'lng': message.location.longitude}

    if message.venue:
        location_text = message.venue.address
    else:
        location_text = await get_reverse_geocoding(list(location.values()))



    markup = m.LocationConfirmationMarkup(location)
    await asyncio.gather(
        state.update_data(location_text=location_text),
        message.answer(msg.member.select_location_confirm.format(location=location_text), reply_markup=markup),
    )



@dp.message_handler(state=OrderState.SelectAddress, content_types=ANYTYPE)
async def order_select_location_failed(message: types.Message, state: FSMContext):

    await message.answer(msg.member.select_location)


@dp.callback_query_handler(location_markup_data.filter(ctx='new-order'), state=OrderState.SelectAddress)
async def location_is_selected(call: types.CallbackQuery, callback_data: dict, state: FSMContext):

    await call.answer(msg.call.selected)
    location_button_id = int(callback_data['sqid'])

    location_text = call.message.reply_markup['inline_keyboard'][location_button_id][0]['text']

    coords = await get_coordinates_from_text(location_text)

    markup = m.LocationConfirmationMarkup(coords)

    await call.message.answer_location(
        latitude=coords['lat'],
        longitude=coords['lng']
    )
    await asyncio.gather(
        state.update_data(location_text=location_text),
        call.message.answer(msg.member.select_location_confirm.format(location=location_text), reply_markup=markup)
    )


@dp.callback_query_handler(confirm_location_data.filter(a='1'), state=OrderState.SelectAddress)
async def select_location_is_confirmed(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await asyncio.gather(
        call.message.delete_reply_markup(),
        state.update_data(location=callback_data['coords']),
        call.message.answer(msg.member.add_apartment, reply_markup=m.GetPassApartmentButton()),
        OrderState.SelectApartment.set(),
    )


@dp.callback_query_handler(confirm_location_data.filter(a='0'), state=OrderState.SelectAddress)
async def select_location_is_wrong(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await call.message.edit_text(msg.member.select_location_is_wrong)


@dp.message_handler(state=OrderState.SelectApartment, content_types=TEXTTYPE)
async def order_select_apartment(message: types.Message, state: FSMContext):

    if len(message.text) > 300:
        raise SkipHandler()

    await asyncio.gather(
        state.update_data(apartment=message.text),
        message.answer(msg.member.select_price),
        OrderState.SelectPrice.set(),
    )


@dp.message_handler(state=OrderState.SelectApartment, content_types=ANYTYPE)
async def order_select_apartment_failed(message: types.Message, state: FSMContext):
    await message.answer(msg.member.add_apartment_failed)


@dp.message_handler(lambda message: message.text.isdigit(), state=OrderState.SelectPrice)
async def order_select_price(message: types.Message, state: FSMContext):

    await asyncio.gather(
        state.update_data(initial_price=message.text),
        message.answer(msg.member.add_description, reply_markup=m.GetPassDescriptionButton()),
        OrderState.AddDescription.set(),
    )


@dp.message_handler(state=OrderState.SelectPrice, content_types=ANYTYPE)
async def order_select_price_failed(message: types.Message, state: FSMContext):
    await message.answer(msg.member.select_price_failed)


@dp.callback_query_handler(lambda c: c.data.startswith('skip'), state=[OrderState.AddDescription, OrderState.SelectApartment])
async def order_skip_description(call: types.CallbackQuery, state: FSMContext):

    if call.data == 'skip_description':

        await state.update_data(description=None)

        await asyncio.gather(
            call.message.delete_reply_markup(),
            confirm_order(call.message, state),
            OrderState.Confirm.set()
        )

    elif call.data == 'skip_apartment':

        await state.update_data(apartment="")

        await asyncio.gather(
            call.message.delete_reply_markup(),
            call.message.answer(msg.member.select_price),
            OrderState.SelectPrice.set(),
        )



@dp.message_handler(Regexp(r'^(.){8,1024}$'), state=OrderState.AddDescription)
async def order_add_description(message: types.Message, state: FSMContext):

    if len(message.text) > 1024:
        return await message.answer(msg.member.description_is_too_long)

    await state.update_data(description=message.text)

    await asyncio.gather(
        confirm_order(message, state),
        OrderState.Confirm.set()
    )


@dp.message_handler(state=OrderState.AddDescription, content_types=ANYTYPE)
async def order_add_description_failed(message: types.Message, state: FSMContext):
    if message.text:
        await message.answer(msg.member.add_description_failed)
    else:
        await message.answer(msg.member.add_description)


async def confirm_order(message: types.Message, state: FSMContext) -> None:

    data = await state.get_data()

    description = data.pop('description') or "Нет дополнительного описания"
    gender = "мужчина" if data.pop('gender') == "m" else "женщина"
    address = "Квартира не указана" if data.get('apartment') == "" else f"Квартира: {data.get('apartment')}"

    await message.answer(
        msg.member.order_confirmation.format(**data, gender=gender, description=description, address=address),
        reply_markup=m.GetConfirmation())


@dp.callback_query_handler(lambda c: c.data == 'confirm', state=OrderState.Confirm)
async def order_confirmation(call: types.CallbackQuery, state: FSMContext):

    async_task(
        call.answer(msg.call.new_order),
        call.message.answer(msg.member.order_created),
        call.message.delete_reply_markup(),
    )

    order = await OrderWrapper.add(call.message.chat.id, await state.get_data())

    OrderDispatcher.add_order(order)

    await EventManager.new_event(
        header=msg.event.new_order_header,
        content=msg.event.new_order_content.format(order=order),
        type=EventChoice.NewOrder,
        additional_id=order.id,
    )

    chat_id, invite_link = await setup_dialog_chat(order, call.message.chat.id)

    timestamp = round(datetime.now().timestamp())
    await call.message.answer(
        msg.member.chat_for_customer,
        reply_markup=m.GetInviteButton(invite_link, chat_id, timestamp=timestamp),
        disable_web_page_preview=True,
    )
