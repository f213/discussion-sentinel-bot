import pytest

from filters import IsMessageOnBehalfOfChat


@pytest.fixture
def mock_chat():
    class MockChat:
        def __init__(self, chat_id: int) -> None:
            self.id = chat_id

    return lambda chat_id: MockChat(chat_id=chat_id)

@pytest.fixture
def message(mock_message, mock_chat):
    mock_message.sender_chat = None
    mock_message.chat = mock_chat(chat_id=7)
    return mock_message


@pytest.fixture(scope="session")
def filter_obj():
    return IsMessageOnBehalfOfChat()


def test_false_if_no_sender_chat(do_filter, message):
    assert do_filter(message) is False


def test_false_if_sender_chat_same_as_current(do_filter, message, mock_chat):
    message.sender_chat = message.chat

    assert do_filter(message) is False


def test_true_if_sender_chat(do_filter, message, mock_chat):
    message.sender_chat = mock_chat(chat_id=55)

    assert do_filter(message) is True
