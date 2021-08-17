from __future__ import annotations

import typing

import aiogram

from interface.text import btns


class Markup(aiogram.types.InlineKeyboardMarkup):
    """
    Extension to InlineKeyboardMarkup with some helpful methods
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.overloaded_insert = self.insert
        self.insert = self.insert_overload

    def insert_overload(
            self,
            text: str,
            cb: aiogram.utils.callback_data.CallbackData,
    ) -> Markup:
        self.overloaded_insert(
            aiogram.types.InlineKeyboardButton(
                text=text,
                callback_data=cb,
            )
        )
        return self

    def add_back_button(
            self,
            cb: aiogram.utils.callback_data.CallbackData,
            text: str = btns.back,
    ) -> Markup:
        """
        Add back button to the keyboard

        :param InlineKeyboardMarkup markup: .
        :param CallbackData callback: .
        :param typing.Optional[str] text: . Defaults to btns.back.
        :return: InlineKeyboardMarkup

        """
        self.insert(text=text, cb=cb)
        return self


class BaseMarkup:
    """
    Base class to work with InlineKeyboardMarkup.
    Implements some helpful methods

    All methods of class are static
    """

    @staticmethod
    def get_keyboard(row_width: int = 1) -> Markup:
        """
        Create new keyboard

        :param typing.Optional[int] row_width: . Defaults to 1.
        :return: InlineKeyboardMarkup

        """
        return Markup(row_width=row_width)

    @staticmethod
    def _get_callback(
            cb: aiogram.utils.callback_data.CallbackData,
            **kw: typing.Any,
    ) -> aiogram.utils.callback_data.CallbackData:
        """
        Go ahead - add some keyword arguments with default values!

        :return: CallbackData
        """
        return cb.new(**kw)
