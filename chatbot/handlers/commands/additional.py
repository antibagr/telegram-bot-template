from aiogram import types
from aiogram.dispatcher.storage import FSMContext

from loader import dp

from utils.func import to_json

from config import MAGIC_ID


@dp.message_handler(commands='str', user_id=MAGIC_ID)
async def jsonify_message(message: types.Message) -> None:
    """
    Bot answers with json representation of a message
    Debug purpose only
    """
    await message.answer(to_json(message))


@dp.message_handler(commands='fsm', user_id=MAGIC_ID)
async def terms_of_use(message: types.Message, state: FSMContext) -> None:
    """
    Bot answers with representation of current finite state macgine state
    Debug purpose only
    """
    await message.answer(await state.get_state())
