"""
Order of imports describes how user's messages will be proceeded
"""

from .errors.error_handler import dp
from .commands import dp
from .echo import dp


__all__ = ["dp"]
