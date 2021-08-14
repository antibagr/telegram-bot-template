from aiogram.dispatcher.filters.state import StatesGroup, State

from typing import List


class BaseState(StatesGroup):
    """
    Wrapper of StatesGroup
    with additional property-method All
    """

    @classmethod
    @property
    def All(cls) -> List[State]:
        """
        Returns all states of a state group
        """

        return [x for x in vars(cls).values() if isinstance(x, State)]
