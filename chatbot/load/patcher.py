import typing
import functools

from typehints import Dispatcher


def default_any_state(func: typing.Callable) -> typing.Callable:
    return functools.partial(func, state='*')


def patch_dispatcher(dp: Dispatcher) -> Dispatcher:
    '''
    Makes Dispatcher to work with any state by default.
    '''
    for func in (
        attr
        for attr in dir(dp)
        if (
            'handler' in attr
            and 'error' not in attr
            and callable(getattr(dp, attr))
        )
    ):
        setattr(dp, func, default_any_state(getattr(dp, func)))
    return dp
