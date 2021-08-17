'''
Helpful functions to handle exceptions without any dependencies
'''
import traceback
import typing

import aiogram

from .func import to_json, tag


def get_exception_details(exp: Exception) -> str:
    '''
    Return Exception details (traceback, type, etc)

    :param Exception exp: .
    :returns: str

    '''
    details = ''.join(traceback.format_exception(
        etype=type(exp),
        value=exp,
        tb=exp.__traceback__,
    ))
    return aiogram.utils.markdown.quote_html(details)


def exception_to_string(
        exp: Exception,
        header: typing.Union[dict, str, aiogram.types.Update]
) -> str:
    '''
    Return text formatted to HTML with header in 'b' tag and
    text representation of an exception object in 'pre' tag
    Helpful to proceed an exceptions from dp.errors_handler()

    :param Exception exp: .
    :param Union[dict, str, types.Update] header: .
    :returns: str
    '''
    if not isinstance(header, str):
        header = to_json(header)
    else:
        header = tag(header, 'b')
    return '\n\n'.join((
        exp.__class__.__name__,
        header,
        get_exception_details(exp),
    ))
