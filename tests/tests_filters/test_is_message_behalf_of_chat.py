import pytest

from filters import IsMessageOnBehalfOfChat


@pytest.fixture
def message(mock_message):
    mock_message.sender_chat = None
    return mock_message


@pytest.fixture(scope="session")
def filter_obg():
    return IsMessageOnBehalfOfChat()


def test_false_if_no_sender_chat(do_filter, message):
    assert do_filter(message) is False


def test_true_if_sender_chat(do_filter, message):
    message.sender_chat = "very-suspicious-id"

    assert do_filter(message) is True
