from asgiref.sync import sync_to_async

import django
from aiogram import types

from loader import dp
from utils.func import to_json
from manager.models import User as UserModel


@sync_to_async
def add_user(user_id, full_name, username):
    try:
        return UserModel(user_id=int(user_id), name=full_name, username=username).save()
    except Exception as e:
        return str(e)


@sync_to_async
def select_all_users() -> django.db.models.query.QuerySet:
    return UserModel.objects.all()


@dp.message_handler(state='*')
async def message_to_string(message: types.Message):
    await message.answer(to_json(await select_all_users() or {"No users found": 0}))
