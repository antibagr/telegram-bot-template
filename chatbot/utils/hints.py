from aiogram import types
from typing import Tuple, Union, Dict, Any, List

GeoCoords = Tuple[float, float]
Serializable = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]


ANYTYPE = types.message.ContentType.ANY
TEXTTYPE = types.message.ContentType.TEXT
