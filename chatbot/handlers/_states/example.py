from states.base import Base, State


class SignUp(Base):
    '''
    Example of how you can create a state group
    '''
    email = State()
    phone_number = State()
