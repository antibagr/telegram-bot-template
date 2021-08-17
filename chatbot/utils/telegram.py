import random
import typing

import aiogram

from .magic_json import Json
from typehints import Stickers
from settings import settings


def get_link_to_bot(text: str) -> str:
    return aiogram.utils.markdown.hlink(
        text,
        f't.me/{settings.BOT_USERNAME}',
    )


def get_command_name(text: str) -> str:
    return text.split('@')[0][1:]


STICKER_PACK: Stickers = {
    'bear_dancing': 'CAACAgQAAxkBAAEGXW9fgvffXDsttHPDK4iNIAaHedWjswACYAQAAktp7hDFwzTSAS5DvRsE',
    'bear_typing': 'CAACAgQAAxkBAAEGXXFfgvir-8B4Xec1z6mPJhqavOdtgwACfRIAAtqjlSzhfCXx5J4OCRsE',
    'dog_sorry': 'CAACAgIAAxkBAAEGXjtfg0m4DVV2_cphAW1T4zeBUxyRuwACPwADrWW8FIT4R4kksisgGwQ',
    'duck_burns': 'CAACAgIAAxkBAAEGimpfl_slR2wPmunkY2P7J5r33Xx39gACBQEAAladvQq35P22DkVfdxsE',
}

STICKERS_MOOD: Stickers = {
    'hello': [
        'CAACAgQAAxkBAAEHOlBf06qatSAMXEgHcE4sjElBCdwX7AACPxMAAtqjlSy1yk0T3I_OkR4E'
    ],
    'question': [
        'CAACAgQAAxkBAAEGI9ZfaXMu77s1t4zAjdpy9nmtQEkR0wAChQADS2nuELg_1TGNapL_GwQ',
        'CAACAgIAAxkBAAEGI9JfaXL1BVkPUW1ZhiBFJzosqSm_jgACGAADwDZPE9b6J7-cahj4GwQ',
        # Zebra
        'CAACAgEAAxkBAAEGLoJfbg6UcOnl61gc5KM_4nqV7u7usQACKAADOA6CEeJAhB3GAAE0IhsE'
    ],
    'happy': [
        'CAACAgIAAxkBAAEGK3RfbMmW1MOjs9AAAfAFn_CyL30dsrAAAhoAA_cCyA-vLwlpco42yxsE',
        'CAACAgIAAxkBAAEGK3ZfbMnF8M16pYUU-6QVsryKufg1tQACKgADFkJrCmgXzyFhnidgGwQ',
        'CAACAgIAAxkBAAEGI9xfaXNTHbQjTc8epAlGJ7zgV-LEnQACFgADwDZPE2Ah1y2iBLZnGwQ'
    ],
    'sad': [
        'CAACAgQAAxkBAAEGI9pfaXND_0IeP96M3OdGXAJm518cJAACjAADS2nuEI29k5Ob9ulEGwQ',
        'CAACAgIAAxkBAAEGI9RfaXMie_EnOxr0GcrCR2fWkJ43WQACDgADwDZPEyNXFESHbtZlGwQ'
    ]
}

single_stickers = Json(**STICKER_PACK)
stickers_by_mood = Json(**STICKERS_MOOD)


async def send_some_sticker(
        bot: aiogram.Bot,
        target: typing.Union[
            int,
            aiogram.types.CallbackQuery,
            aiogram.types.Message,
        ],
        /,
        mood: typing.Optional[str] = None,
) -> typing.Optional[aiogram.types.Message]:
    '''
    Send random sticker to the chat.

    :param message: Can be chat id, message object or callbackquery object
    :param str mood: One of the sticker dictionary key
    :returns: Sent message on success
    '''
    if (
        mood is None
        or mood not in stickers_by_mood.keys()
    ):
        random_mood = random.choice(list(stickers_by_mood.keys()))
        sticker = random.choice(stickers_by_mood[random_mood])
    else:
        sticker = random.choice(stickers_by_mood[mood])
    # Choose target chat id
    if isinstance(target, aiogram.types.Message):
        target = target.chat.id
    elif isinstance(target, aiogram.types.CallbackQuery):
        target = target.message.chat.id
    await bot.send_sticker(target, sticker)
