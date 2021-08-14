from states.BaseState import BaseState, State

class OrderState(BaseState):
    """
    State group for making new order
    """

    SelectTitle = State()
    SelectFullname = State()
    SelectGender = State()
    SelectAge = State()
    SelectPhone = State()
    SelectAddress = State()
    SelectApartment = State()
    SelectPrice = State()
    AddDescription = State()
    Confirm = State()

    SendLocation = State()
