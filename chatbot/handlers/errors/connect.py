from loader import dp

from .error_handler import errors_handler


dp.register_errors_handler(
    errors_handler,
)
