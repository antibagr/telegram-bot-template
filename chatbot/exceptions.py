import logging

from typing import Optional, Union, Callable
from utils.hints import Serializable
from utils.func import to_json


from interface.verbose import msg


class BaseException(Exception):
    pass


class CodeException(BaseException):
    pass


class InstanceCreatedException(TypeError):
    """
    Raised when there was attempt to initiate a static class
    """

    _default_message: str = "A class which raised this exception should not be instantiated"

    def __init__(self, message: Optional[str]):
        self.message = message or self._default_message
        super().__init__(self.message)


class NotAuthorizedError(Exception):
    pass


class BaseTelethonException(BaseException):

    caller = "default caller"
    default_message = f"Exception happend in telethon: {caller}"

    def __init__(self, caller: Callable, alert: Union[str, None] = None):
        if not callable(caller):
            raise AttributeError(
                f"func argument must be callable! Now is {type(caller)}")
        self.caller = caller.__name__
        self.message = alert if alert else self.default_message
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message


class VerboseTelethonException(BaseTelethonException):

    def __init__(self, caller: Callable, alert: Union[str, None] = None, verbose: Union[str, None] = None):
        self.verbose = verbose or msg.err.default_message
        super().__init__(caller, alert)


class NotInMutualContactsException(VerboseTelethonException):

    pass


class EmptyCodeException(CodeException):
    """ Raised when file with a code is empty """

    def __str__(self):
        return "File where a code has to be is still empty"


class InvalidCodeException(CodeException):
    """ Raised when invalid code retrieved from a file """

    def ____init__(self, code: Union[str, int] = None):
        self.code = "code was not passed" if not code else code
        self.message = f"Got invalid code from a file: {self.code}"
        super().__init__(self.message)


class ResendCodeLimit(CodeException):

    def __str__(self):
        return "Resending code limit!"



class GoogleAPIException(BaseException):

    def __init__(self, user_input: str, response: Serializable) -> None:
        self.user_input = str(user_input)
        self.response = to_json(response)

    def __str__(self) -> str:
        return "\n".join((self.user_input, self.response))
