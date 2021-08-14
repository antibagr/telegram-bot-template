import os
import pathlib
import inspect
import asyncio

import random
from typing import Union, Optional, Awaitable, Any, Tuple

from aiogram import types
from loader import bot
from config import MEDIA_ROOT

from handlers.errors.send_exception import send_exception
from interface.verbose import msg
from utils.async_func import async_task

# GLOBAL VARIABLE
sticker_pack = {
    "bear_dancing": "CAACAgQAAxkBAAEGXW9fgvffXDsttHPDK4iNIAaHedWjswACYAQAAktp7hDFwzTSAS5DvRsE",
    "bear_typing": "CAACAgQAAxkBAAEGXXFfgvir-8B4Xec1z6mPJhqavOdtgwACfRIAAtqjlSzhfCXx5J4OCRsE",
    "dog_sorry": "CAACAgIAAxkBAAEGXjtfg0m4DVV2_cphAW1T4zeBUxyRuwACPwADrWW8FIT4R4kksisgGwQ",
    "message_sent": [
        "CgACAgQAAxkBAAEGa-hfidD8GEWSb5VZ4VSYZPCY3-Ly1gACawIAApJB5VMInvJw1tNUGhsE",
        "CgACAgQAAxkBAAEGa-pfidEjTRgqTFW0iZcYYxkaa0rnPAACEwIAAr2ajVIiqbjEDF9qbRsE",
        "CgACAgQAAxkBAAEGa-xfidEy4yYxLz6f0JTzi0monYM0eAACVQIAAnE9xFKIjNyEnNGGrBsE"
    ],
    "duck_burns": "CAACAgIAAxkBAAEGimpfl_slR2wPmunkY2P7J5r33Xx39gACBQEAAladvQq35P22DkVfdxsE"
}


async def send_some_sticker(message: Union[types.CallbackQuery, types.Message, int], /, mood: str = None) -> Optional[types.Message]:
    """
    Send random sticker to the chat.

    :param message: Can be chat id, message object or callbackquery object
    :param str mood: One of the sticker dictionary key
    :returns: Sent message on success
    """

    stickers = {
        "hello": ["CAACAgQAAxkBAAEHOlBf06qatSAMXEgHcE4sjElBCdwX7AACPxMAAtqjlSy1yk0T3I_OkR4E"],
        "question": ["CAACAgQAAxkBAAEGI9ZfaXMu77s1t4zAjdpy9nmtQEkR0wAChQADS2nuELg_1TGNapL_GwQ",
                     "CAACAgIAAxkBAAEGI9JfaXL1BVkPUW1ZhiBFJzosqSm_jgACGAADwDZPE9b6J7-cahj4GwQ",
                     # Zebra
                     "CAACAgEAAxkBAAEGLoJfbg6UcOnl61gc5KM_4nqV7u7usQACKAADOA6CEeJAhB3GAAE0IhsE"],
        "happy": ["CAACAgIAAxkBAAEGK3RfbMmW1MOjs9AAAfAFn_CyL30dsrAAAhoAA_cCyA-vLwlpco42yxsE",
                  "CAACAgIAAxkBAAEGK3ZfbMnF8M16pYUU-6QVsryKufg1tQACKgADFkJrCmgXzyFhnidgGwQ",
                  "CAACAgIAAxkBAAEGI9xfaXNTHbQjTc8epAlGJ7zgV-LEnQACFgADwDZPE2Ah1y2iBLZnGwQ"],
        "sad": ["CAACAgQAAxkBAAEGI9pfaXND_0IeP96M3OdGXAJm518cJAACjAADS2nuEI29k5Ob9ulEGwQ",
                "CAACAgIAAxkBAAEGI9RfaXMie_EnOxr0GcrCR2fWkJ43WQACDgADwDZPEyNXFESHbtZlGwQ"]
    }

    # Choose sticker
    if mood is not None and mood not in stickers.keys():
        sticker = random.choice(stickers[random.choice(list(stickers.keys()))])
    else:
        sticker = random.choice(stickers[mood])

    # Choose target chat id
    if isinstance(message, types.Message):
        target = message.chat.id
    elif isinstance(message, types.CallbackQuery):
        target = message.message.chat.id
    else:
        target = message

    await bot.send_sticker(target, sticker)


async def download_file(file_id: str, destination=None, timeout=30, chunk_size=65536, seek=True, make_dirs=True):
    """
    Download file from Telegram.
    Based on aiogram.types.mixins.Downloadable

    :param file_id: unique id of file which stored on Telegram
    :param destination: filename or instance of :class:`io.IOBase`. For e. g. :class:`io.BytesIO`
    :param timeout: Integer
    :param chunk_size: Integer
    :param seek: Boolean - go to start of file when downloading is finished.
    :param make_dirs: Make dirs if not exist
    :return: destination
    """

    file: types.file.File = await bot.get_file(file_id)

    print(file)

    is_path = True
    if destination is None:
        destination = file.file_path
    elif isinstance(destination, (str, pathlib.Path)) and os.path.isdir(destination):
        destination = os.path.join(destination, file.file_path)
    else:
        is_path = False

    if is_path:

        if os.path.exists(destination):
            raise FileExistsError()

        if make_dirs:
            os.makedirs(os.path.dirname(destination), exist_ok=True)

    print(file.file_path)
    print(destination)
    print(type(destination))

    return await bot.download_file(file_path=file.file_path,
                                   destination=destination, timeout=timeout,
                                   chunk_size=chunk_size, seek=seek)


async def download_user_document(user_id: int, file_id: str, overwrite: Optional[bool] = False) -> None:
    """
    Downloads user's document to MEDIA_ROOT as {user_id}.jpg

    :param int user_id: User id
    :param str file_id: Telegram unique file id
    :param Optional[bool] overwrite: If false and file exists FileExistsError will be raised

    """
    file: types.file.File = await bot.get_file(file_id)

    destination = os.path.join(MEDIA_ROOT, f"{user_id}.jpg")

    if os.path.exists(destination) and not overwrite:
        raise FileExistsError()

    await bot.download_file(
        file_path=file.file_path,
        destination=destination)
