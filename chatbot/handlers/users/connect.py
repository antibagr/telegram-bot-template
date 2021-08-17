from loader import dp

from .echo import echo_handler


dp.register_message_handler(
    echo_handler,
)
