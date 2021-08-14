from states.BaseState import BaseState, State


class CustomerState(BaseState):
    """
    State group for dealing with customers
    """

    Arbitration = State()
