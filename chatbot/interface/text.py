import typing

from utils.telegram import get_link_to_bot


class cmd:
    '''
    Class to store bot's commands
    '''

    __all__ = ('start', 'menu', 'help')

    start = 'start'
    help = 'help'
    menu = 'menu'

    @classmethod
    def get_all(cls) -> typing.Tuple[str, ...]:
        return tuple(getattr(cls, attr) for attr in cls.__all__)

    @classmethod
    def get_private(cls) -> typing.Tuple[str, ...]:
        return ('start',)


class btns:
    ''''
    A class to store title for the buttons
    '''


class msg:
    '''
    A container that stores all the text messages
    '''

    bot_started = "Hey-ho!"
    start = "Let's do it, baby!"
    unknown_command = "That's not the command I know..."
    help = "It's my help message! (not so helpful for now)"
    menu = "Do you wanna some pasta or pizza?"
    command_is_private = (
        "The command {command!r} is only available from my private chat "
        + get_link_to_bot("[click here to open 🔓]")
    )

    class err:
        default_error_answer = "Heck! I've crashed! Did you hear that? 🤖 "
