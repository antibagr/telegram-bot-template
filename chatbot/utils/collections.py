import os
import asyncio

from typing import Dict, Optional, Awaitable, Any
import json
from functools import wraps

import aiofiles

from config import SRC_DIR

from utils.async_func import async_task

def get_source_path(classname: str, extension: Optional[str] = 'collection') -> str:
    return os.path.join(SRC_DIR, 'collections', f'{classname}.{extension}')


def write(func: Awaitable) -> Awaitable:

    @wraps(func)
    async def decorator(self, *args, **kwargs) -> Any:
        result = await func(self, *args, **kwargs)
        async with aiofiles.open(self.source, 'w') as f:
            await f.write(json.dumps(self._collection))
        return result

    return decorator


class SingleMessageCollection:

    _collection: Dict[int, int]

    def __init__(self, /, **kwargs) -> None:
        print("MessageCollection created")
        self._collection = kwargs
        self.source = get_source_path(self.__class__.__name__)
        async_task(self._load_data())

    async def _load_data(self) -> None:
        async with aiofiles.open(self.source, 'r') as f:
            cached_collection = json.loads(await f.read())
            cached_collection = {int(k): int(v) for k, v in cached_collection.items()}
            self._collection |= cached_collection

        print(self._collection)


    @write
    async def add(self, key: int, value: int, overwrite: Optional[bool] = False) -> None:

        if key in self._collection and not overwrite:
            raise KeyError(f"{key} already in {self.__class__.__name__}")

        self._collection[key] = value

        print(self._collection)

    @write
    async def delete(self, key) -> int:

        if key not in self._collection:
            raise KeyError(f"{key} is not in {self.__class__.__name__}")

        return self._collection.pop(key)


    async def get(self, key) -> Optional[int]:
        return self._collection[key] if key in self._collection else None


class TaskCollection:

    _collection: Dict[int, asyncio.Task]

    def __init__(self, callback: Awaitable, **kwargs: Dict[int, asyncio.Task]) -> None:
        self._collection = kwargs
        self.source = get_source_path(self.__class__.__name__, extension='pickle')
        self.callback = self._create_callback(callback)

    def _create_callback(self, callback: Awaitable) -> Awaitable:

        async def compiled_callback(timeout, *args, **kwargs) -> Any:
            try:
                await asyncio.sleep(timeout)
                return await callback(*args, **kwargs)
            except asyncio.CancelledError:
                print("Callback was cancelled")
                return None

        return compiled_callback


    def add(self, chat_id: int, message_id: int, timeout: int) -> asyncio.Task:

        if chat_id in self._collection:
            self.cancel(chat_id)
        return self._add(chat_id, message_id, timeout)

    def _add(self, chat_id: int, message_id: int, timeout: int) -> asyncio.Task:
        print("Add new callback in TaskCollection")
        self._collection[chat_id] = async_task(self.callback(timeout, chat_id, message_id))
        return self._collection[chat_id]

    def cancel(self, chat_id: int) -> None:
        if chat_id in self._collection:
            print("Cancelling callback in TaskCollection")
            self._collection[chat_id].cancel()

    def delete(self, chat_id: int, skip_cancelling: Optional[bool] = False) -> None:
        if chat_id not in self._collection:
            raise KeyError(f"{chat_id} is not in collection!")

        if not skip_cancelling:
            self.cancel(chat_id)

        self._collection.pop(chat_id)
