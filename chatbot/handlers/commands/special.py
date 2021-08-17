import aiogram

from utils.func import to_json
from typehints import FSMContext


async def jsonify_message(
        message: aiogram.types.Message,
) -> None:
    """
    Bot answers with json representation of a message
    Debug purpose only
    """
    await message.answer(to_json(message))


async def get_current_state(
        message: aiogram.types.Message,
        state: FSMContext,
) -> None:
    """
    Bot answers with representation of current finite state macgine state
    Debug purpose only
    """
    state = await state.get_state()
    await message.answer(state or 'No current state.')
