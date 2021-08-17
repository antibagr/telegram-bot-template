import pytest

from unittest.mock import AsyncMock
from chatbot.handlers.users.echo import echo


@pytest.mark.asyncio
async def test_echo_handler():
    text_mock = 'repeat me'
    message_mock = AsyncMock(text=text_mock)
    await echo(message=message_mock)
    message_mock.answer.assert_called_with(text_mock)
