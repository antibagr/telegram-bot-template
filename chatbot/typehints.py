import io
import os
import pathlib
import typing

import aiogram
from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.storage import FSMContext
from aiogram.dispatcher.filters.builtin import CommandHelp, Text
from aiogram.dispatcher.filters import Command, CommandStart
from aiogram.dispatcher.handler import SkipHandler

ANYTYPE = aiogram.types.message.ContentType.ANY
TEXTTYPE = aiogram.types.message.ContentType.TEXT

URL = typing.NewType('_URL', str)

String = typing.TypeVar('String', bound=str)

Stickers = typing.Dict[
    String, typing.Union[typing.List[String], String]
]

PathLike = typing.Union[str, io.IOBase, pathlib.Path, os.PathLike]
