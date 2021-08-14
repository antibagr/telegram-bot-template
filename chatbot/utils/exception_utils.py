"""
Helpful functions to handle exceptions without any dependencies
"""
import logging
import traceback

from aiogram import types
from aiogram.utils.markdown import quote_html

from typing import Union

from .func import to_json, tag


def log(exp: Exception) -> None:
    """
    Wrapper to log exception.
    Centralize managing logging calls

    :param Exception exp: Exception to be logged

    """
    logging.exception(exp, exc_info=True)


def get_exception_details(exp: Exception) -> str:
    """
    Return Exception details (traceback, type, etc)

    :param Exception exp: .
    :returns: str

    """
    details = ''.join(traceback.format_exception(etype=type(exp), value=exp, tb=exp.__traceback__))
    return quote_html(details)


def exception_to_string(exp: Exception, header: Union[dict, str, types.Update]) -> str:
    """
    Return text formatted to HTML with header in "b" tag and
    text representation of an exception object in "pre" tag
    Helpful to proceed an exceptions from dp.errors_handler()

    :param Exception exp: .
    :param Union[dict, str, types.Update] header: .
    :returns: str
    """

    header = to_json(header) if not isinstance(header, str) else tag(header, 'b')
    return "\n\n".join([exp.__class__.__name__, header, get_exception_details(exp)])
