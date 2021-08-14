from states.BaseState import BaseState, State

class DeliveryState(BaseState):
    """
    State group for tracking a carrier
    """

    ConfirmInformation = State()
    StartDelivering = State()
    Arrived = State()
    ProcessingOrder = State()
    Payment = State()
    PaymentInfo = State()
    Arbitration = State()
