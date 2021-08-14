from typing import Optional, List
from datetime import datetime

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from manager.models import OrderModel, OrderStatusChoices


from utils.hints import Serializable, GeoCoords

from .base_kb import BaseMarkup, Markup
from interface.callback import (menu_data, gender_data, dropdown_menu_data,
                                cancel_data, offer_data, delivery_data, invalid_invite_link_data,
                                location_markup_data, confirm_location_data,
                                order_info_data, delivery_timer_data, arbitration_data)
from interface.verbose import btns


class m(BaseMarkup):
    """
    � A class to create user keyboards.
    Should not be created or inherited.
    All class methods are static
    """

    def GetMenu(is_on_duty: int, current_offer: Optional[bool] = False, current_order: Optional[bool] = False) -> Markup:

        status = btns.user_status_on if is_on_duty else btns.user_status_off

        markup = m.GetKeyboard(row_width=1)

        markup.Insert(
            status,
            menu_data.new(action='status', s=int(is_on_duty))
        )

        markup.Insert(
            btns.menu[0],
            menu_data.new(action='my_orders', s=0)
        )

        my_orders_button = btns.menu[1]

        if current_offer:
            my_orders_button += " ❕"
        elif current_order:
            my_orders_button += " 🌀"

        markup.Insert(
            my_orders_button,
            menu_data.new(action='carrier_orders', s=0)
        )

        markup.Insert(
            btns.menu[2],
            menu_data.new(action='order', s=0)
        )


        return markup

    def GetGenderSelection() -> Markup:

        markup = m.GetKeyboard(row_width=2)

        markup.Insert(
            btns.gender[0],
            gender_data.new(g='m')
        )
        markup.Insert(
            btns.gender[1],
            gender_data.new(g='f')
        )
        return markup

    def GetPassDescriptionButton() -> Markup:
        return m.GetKeyboard().Insert(btns.skip, 'skip_description')

    def GetPassApartmentButton() -> Markup:
        return m.GetKeyboard().Insert(btns.skip, 'skip_apartment')

    def GetConfirmation() -> Markup:
        return m.GetKeyboard().Insert(btns.confirm, 'confirm')

    def ShowTutorial() -> Markup:
        return m.GetKeyboard().Insert(
            btns.show_more,
            dropdown_menu_data.new('car_tut', 1)
            ).Insert(
            btns.cancel,
            cancel_data.new(ctx='car_ses')
        )

    def HideTutorial() -> Markup:
        return m.GetKeyboard().Insert(
            btns.show_less,
            dropdown_menu_data.new('car_tut', 0)
            ).Insert(
            btns.cancel,
            cancel_data.new(ctx='car_ses')
        )


    def RequireCurrentLocation():
        return ReplyKeyboardMarkup(
            one_time_keyboard=True,
            resize_keyboard=True,
            keyboard=[[
                KeyboardButton(btns.share_location, request_location=True)
            ]]
        )

    def OfferMarkup(order_id: int) -> Markup:
        return m.GetKeyboard().Insert(
            btns.order_offer[0],
            offer_data.new(order_id=order_id, action='accept')
            ).Insert(
            btns.order_offer[1],
            offer_data.new(order_id=order_id, action='reject')
        )

    def ReturnToMenu() -> Markup:
        return m.GetKeyboard().Insert(btns.cancel, menu_data.new(action='cancel', s='0'))


    def GetConfirmationKeyboard(order_id: int) -> Markup:

        return m.GetKeyboard().Insert(
            btns.order_confirm[0],
            offer_data.new(order_id=order_id, action='confirm')
        ).Insert(
            btns.order_confirm[1],
            offer_data.new(order_id=order_id, action='not_confirm')
        )

    def ArrivedMarkup(order_id: int) -> Markup:
        return m.GetKeyboard().Insert(
            btns.arrived[0],
            delivery_data.new(order_id=order_id, checkpoint='arrived')
        ).Insert(
            btns.arrived[1],
            delivery_data.new(order_id=order_id, checkpoint='arrived_troubleshoot')
        )

    def ProcessingOrderMarkup(order_id: int) -> Markup:
        return m.GetKeyboard().Insert(
            btns.processing[0],
            delivery_data.new(order_id=order_id, checkpoint='processing')
        ).Insert(
            btns.processing[1],
            delivery_data.new(order_id=order_id, checkpoint='processing_troubleshoot')
        )

    def PaymentMarkup(order_id: int) -> Markup:
        return m.GetKeyboard().Insert(
            btns.processing[1],
            delivery_data.new(order_id=order_id, checkpoint='payment_troubleshoot')
        )

    def ListOrders(orders: List[OrderModel]) -> Markup:

        markup = m.GetKeyboard()

        for order in orders:
            markup.Insert(
                str(order),
                cb=order_info_data.new(id=order.id, role="cstm"),
            )

        markup.AddBackButton(menu_data.new(action='cancel', s=0))

        return markup

    def ListOfCarrierOrders(carrier_orders: List[OrderModel]) -> Markup:

        markup = m.GetKeyboard()

        for order in carrier_orders:

            if order.status < OrderStatusChoices.Arbitration:
                title = "🌀 " + str(order)
            else:
                title = str(order)

            markup.Insert(
                title,
                cb=order_info_data.new(id=order.id, role="carr"),
            )

        markup.AddBackButton(menu_data.new(action='cancel', s=0))

        return markup



    def BackToOrders(
        order: Optional[OrderModel] = None,
        role: Optional[str] = 'cstm',
        text: Optional[str] = btns.back,
        s: Optional[str] = '0'
    ) -> Markup:
        markup = m.GetKeyboard()
        if role == 'cstm':

            if order and order.status in (OrderStatusChoices.Completed, OrderStatusChoices.PaymentInfo):
                markup.Insert(btns.payment_received, menu_data.new(action='payment_received', s=order.id))
                markup.Insert(btns.open_arbitration, arbitration_data.new(order_id=order.id))

            return markup.Insert(text, menu_data.new(action='my_orders', s=s))
        else:
            return markup.Insert(text, menu_data.new(action='carrier_orders', s=s))

    def GetBackToOrder(order: OrderModel) -> Markup:
        return m.GetKeyboard().Insert(btns.back, cb=order_info_data.new(id=order.id, role="cstm_cancel_state"))


    def GetInviteButtonShort(invite_link: str) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup()
        markup.insert(
            InlineKeyboardButton(
                btns.go_to_chat,
                url=invite_link,
            )
        )
        return markup


    def GetInviteButton(invite_link: str, chat_id: int, text: Optional[str] = None, times: Optional[int] = 1, timestamp: Optional[str] = None) -> Markup:
        markup = InlineKeyboardMarkup()

        timestamp = timestamp or round(datetime.now().timestamp())

        markup.insert(
            InlineKeyboardButton(
                text or btns.go_to_chat,
                url=invite_link,
            )
        )
        # markup.insert(
        #     InlineKeyboardButton(
        #         btns.invalid_invite_link,
        #         callback_data=invalid_invite_link_data.new(id=chat_id, times=times, timestamp=timestamp),
        #     ),
        # )
        return markup

    def GetLocationMarkup(locations: Serializable) -> Markup:

        markup = m.GetKeyboard()

        for sequence_id, location in enumerate(locations['predictions']):

            markup.Insert(
                text=location['description'],
                cb=location_markup_data.new(ctx='new-order', sqid=sequence_id),
            )

        return markup

    def LocationConfirmationMarkup(coords: GeoCoords) -> Markup:
        return m.GetKeyboard().Insert(
            text=btns.confirm_location[0],
            cb=confirm_location_data.new(coords=",".join([str(x) for x in coords.values()]), a=1),
        ).Insert(
            text=btns.confirm_location[1],
            cb=confirm_location_data.new(coords="n", a=0)
        )

    def LatenessButton(order_id: int) -> Markup:
        return m.GetKeyboard().Insert(
            text=btns.everything_is_allright,
            cb=delivery_timer_data.new(order_id=order_id),
        )
