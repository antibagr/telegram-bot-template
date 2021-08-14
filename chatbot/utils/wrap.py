"""
Wrapping default handlers with baked parameters and additional logic
"""

from functools import wraps
from typing import Callable, Awaitable, Any, Union

from aiogram import types

from interface.verbose import msg


def bake(original_handler: Callable) -> Callable:
    """
    Pass state = '*' exception handler will define different value
    """
    def partial_decorator(*args, **kwargs) -> Callable:
        kwargs = {'state': '*', **kwargs}
        return original_handler(*args, **kwargs)
    return partial_decorator


def wrap_exception(f: Awaitable) -> Awaitable:
    """
    Decorator that will send to called msg.err.default_error_answer message
    in case exception raised from f
    """

    @wraps(f)
    async def decorator(trg: Union[types.Message, types.CallbackQuery], *args, **kwargs) -> Any:

        try:
            return await f(trg, *args, **kwargs)
        except Exception:
            user = trg if isinstance(trg, types.Message) else trg.message
            await user.answer(msg.err.default_error_answer)

            # Exception will be raised after a user has received
            # information about something bad happened
            # on a server side.
            raise

    return decorator


def get_updated_handler(original_handler: Callable):
    """
    What do we do here is wrapping every handler in a whole bot application
    with a wrap_exception decorator which simply tries to execute function
    And if something bad happend it will nofity whoever called the function
    That something bad happended and after it exception will be raised up
    to the Dispatcher error handler.

    :param Callable original_handler: .

    """

    def updated_handler(*handler_args, **handler_kwargs) -> Callable:
        """
        A function will be called instead of dp.message_handler
        And will return updated_decorator instead of inner aiogram
        Decorator
        """

        def updated_decorator(f: Awaitable) -> Awaitable:
            """
            Actially this function is returned when some handler
            called @dp.message_handler().
            A function still may think that it's the same as before
            But what actually happens is that we wrap it with our wrap_exception
            decorator.
            So when it will be called and if it will raise exception
            We can be sure about a user received an information about this exception
            Instead of waiting forever without knowning nobody gonna answer him.
            """
            handler_decorator = original_handler(*handler_args, **handler_kwargs)
            safe_call = handler_decorator(wrap_exception(f))
            return safe_call

        return updated_decorator

    return updated_handler
