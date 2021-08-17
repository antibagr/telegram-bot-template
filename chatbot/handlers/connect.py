'''
Order of imports describes how user's messages will be proceeded
'''

from .errors.connect import dp
from .commands.connect import dp
from .users.connect import dp


__all__ = ['dp']
