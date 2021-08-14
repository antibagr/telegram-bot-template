from aiogram import types
from loader import dp
from utils.func import to_json


@dp.message_handler(state='*', content_types=types.message.ContentType.ANY)
async def message_to_string(message: types.Message):
    # await message.answer("Okay, fine")
    # return await message.answer(to_json(message))
    loc: types.location.Location = message.location
    if not loc:
        return None

    print(loc.longitude, loc.latitude, loc.horizontal_accuracy,
          loc.live_period, loc.heading, loc.proximity_alert_radius)


# @dp.message_handler(content_types=types.location.Location, state='*')
# async def get_location(message: types.Message):
#     pass
