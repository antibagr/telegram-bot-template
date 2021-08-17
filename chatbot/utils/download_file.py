import io
import os
import typing

import aiogram

from typehints import PathLike
from settings import settings


async def download_file(
        bot: aiogram.Bot,
        file_id: str,
        destination: typing.Optional[PathLike] = None,
        /,
        timeout: int = 30,
        chunk_size: int = 65536,
        seek: bool = True,
        make_dirs: bool = True,
) -> typing.Union[io.BytesIO, io.FileIO]:
    '''
    Download file from Telegrram.
    Based on aiogram.types.mixins.Downloadable

    :param file_id: unique id of file which stored on Telegram
    :param destination: filename or instance of :class:`io.IOBase`.
        For e. g. :class:`io.BytesIO`
    :param timeout: Integer
    :param chunk_size: Integer
    :param seek: Boolean - go to start of file when downloading is finished.
    :param make_dirs: Make dirs if not exist
    :return: destination
    '''
    file: aiogram.types.file.File = await bot.get_file(file_id)
    is_path = False
    destination = destination or file.file_path
    if (
        isinstance(destination, PathLike.__args__)
        and os.path.isdir(destination)
    ):
        is_path = True
        destination = os.path.join(destination, file.file_path)

    if is_path:
        if os.path.exists(destination):
            raise FileExistsError()
        if make_dirs:
            os.makedirs(os.path.dirname(destination), exist_ok=True)
    return await bot.download_file(
        file_path=file.file_path,
        destination=destination,
        timeout=timeout,
        chunk_size=chunk_size,
        seek=seek,
    )


async def download_user_document(
        bot: aiogram.Bot,
        user_id: int,
        file_id: str,
        overwrite: bool = False,
        destination: PathLike = settings.BASE_DIR
) -> typing.Union[io.BytesIO, io.FileIO]:
    '''
    Downloads user's document to MEDIA_ROOT as {user_id}.jpg

    :param int user_id: User id
    :param str file_id: Telegram unique file id
    :param Optional[bool] overwrite: If false and file exists FileExistsError
    will be raised

    '''
    file: aiogram.types.file.File = await bot.get_file(file_id)
    destination = os.path.join(destination, f'{user_id}.jpg')
    if os.path.exists(destination) and not overwrite:
        raise FileExistsError()
    return await bot.download_file(
        file_path=file.file_path,
        destination=destination
    )
