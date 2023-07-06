import pytest

from filters import ChatMessageOnly


@pytest.fixture(scope="session")
def filter_obg():
    return ChatMessageOnly()


def test_false_if_forwarded(do_filter, mock_message):
    mock_message.forward_from_message_id = "ordinary-id-yep"

    assert do_filter(mock_message) is False


def test_true_if_not_forwarded(do_filter, mock_message):
    mock_message.forward_from_message_id = None

    assert do_filter(mock_message) is True
