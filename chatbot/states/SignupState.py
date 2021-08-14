from states.BaseState import BaseState, State

class SignupState(BaseState):
    """
    State group for registration new member
    """

    SelectRole = State()
    SelectFullname = State()
    SelectPhone = State()
    ReadTerms = State()
