from states.BaseState import BaseState, State


class CarrierSessionState(BaseState):
    """
    State group for dealing with sessions
    """

    WaitingLocationMessage = State()
    OnDuty = State()
