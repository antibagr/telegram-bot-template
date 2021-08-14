from loader import dp

from aiogram import types
from aiogram.dispatcher.filters import Command

from interface.verbose import msg

from utils.async_func import async_task


from config import MAGIC_ID


@dp.message_handler(Command("test"), state="*", chat_type='private', user_id=MAGIC_ID)
async def test_function(message: types.Message):

    from loader import OrderDispatcher
    from manager.models import OrderModel
    import random

    # orders = OrderModel.objects.all()
    # order = orders[random.randint(0, len(orders) - 1)]
    order = OrderModel.objects.get(title='Firstorder')

    OrderDispatcher.add_order(order)



@dp.message_handler(Command("code"), state="*", chat_type='private', user_id=MAGIC_ID)
async def EnterTelegramCode(message: types.Message):

    from utils.TeleAPI import ConnectionMaster
    from handlers.errors.send_exception import send_exception

    if not ConnectionMaster.is_waiting_code:
        return await message.answer(msg.admin.not_waiting_code)

    _, *code = message.text.split()
    if len(code) == 1:
        code = code[0]
        if code.isdigit() and len(code) == 5:
            with open(ConnectionMaster.PathToCode, 'w') as f:
                f.write(code)
            return await message.answer(msg.admin.code_sent)

    await message.answer(msg.admin.wrong_code)
