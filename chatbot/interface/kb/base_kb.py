from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from interface.verbose import btns
from aiogram.utils.callback_data import CallbackData

from typing import Union, Optional


class Markup(InlineKeyboardMarkup):
    """
    Extension to InlineKeyboardMarkup with some helpful methods

    """

    def Insert(self, text: str, cb: CallbackData) -> "Markup":
        self.insert(InlineKeyboardButton(
                            text=text,
                            callback_data=cb))
        return self

    def AddBackButton(self, cb: CallbackData, text: Optional[str] = btns.back) -> "Markup":
        """
        Add back button to the keyboard

        :param InlineKeyboardMarkup markup: .
        :param CallbackData callback: .
        :param Optional[str] text: . Defaults to btns.back.
        :return: InlineKeyboardMarkup

        """
        self.Insert(text=text, cb=cb)

        return self



class BaseMarkup:
    """
    Base class to work with InlineKeyboardMarkup.
    Implements some helpful methods

    All methods of class are static
    """

    def GetKeyboard(row_width: Optional[int] = 1) -> Markup:
        """
        Create new keyboard

        :param Optional[int] row_width: . Defaults to 1.
        :return: InlineKeyboardMarkup

        """
        # return InlineKeyboardMarkup(row_width=row_width)
        return Markup(row_width=row_width)

    def _GenerateCallback(cb: CallbackData,
                          level,
                          action: Union[str, int] = "n",
                          id: Union[str, int] = "n",
                          _e: Union[str, int] = "n",
                          _s: Union[str, int] = "n",
                          **kw) -> CallbackData:
        """
        Private method to generate new CallbackData object

        :return: CallbackData
        """
        return cb.new(lev=level, a=action, id=id, _e=_e, _s=_s, **kw)
