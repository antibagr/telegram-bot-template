import pytest


from chatbot.orm.user import UserWrapper, WrapperInterface


def test_inheritance():

    assert issubclass(UserWrapper, WrapperInterface)
