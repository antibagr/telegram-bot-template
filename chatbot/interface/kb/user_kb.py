from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

from .base_kb import BaseMarkup, Markup
from interface.callback import sign_up_data, confirm_data, accept_terms_data
from interface.verbose import btns


class m(BaseMarkup):
    """
    � A class to create user keyboards.
    Should not be created or inherited.
    All class' methods are static
    """

    def ConfirmFullname() -> Markup:

        cb = confirm_data.new(ctx="signup_fullname")
        return m.GetKeyboard(row_width=2).Insert(btns.confirm, cb)

    def ShareContactKeyboard() -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            one_time_keyboard=True,
            resize_keyboard=True,
            keyboard=[[
                KeyboardButton(btns.share_phone, request_contact=True)
            ]]
        )

    def AcceptTerms() -> Markup:

        accept = accept_terms_data.new(a=1)
        reject = accept_terms_data.new(a=0)
        return m.GetKeyboard(row_width=1).Insert(btns.accept_terms, accept).Insert(btns.reject, reject)
