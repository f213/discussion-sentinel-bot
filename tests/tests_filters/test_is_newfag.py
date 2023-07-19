import pytest
import random

from filters import IsNewfag
from models import LogEntry

CHAT_ID = 1


def create_log_message(user_id: int, chat_id: int = CHAT_ID, action: str = '', message_id: int = random.randint(1, 9999)):
    return LogEntry.create(
        user_id=user_id,
        chat_id=chat_id,
        message_id=message_id,
        text='meh',
        meta={'tags': ["ou"]},
        raw={'text': 'meh'},
        action=action,
    )


@pytest.fixture
def user():
    class FakeUser:
        def __init__(self, id: int):
            self.id = id
    return FakeUser(10**9 + 1)


@pytest.fixture
def message(mock_message, user):
    mock_message.from_user = user
    mock_message.chat_id = CHAT_ID
    return mock_message


@pytest.fixture(scope="session")
def filter_obj():
    return IsNewfag()


@pytest.fixture
def valid_messages(user, filter_obj):
    message_id = 1
    for _ in range(3):
        create_log_message(user_id=user.id, message_id=message_id)
        message_id += 1


def test_true_if_no_valid_messages(do_filter, message):
    assert do_filter(message) is True


def test_true_if_not_from_user(do_filter, message):
    message.from_user = None

    assert do_filter(message) is True


def test_true_if_db_disabled(do_filter, message, mocker):
    mocker.patch("helpers.DB_ENABLED", return_value=False)

    assert do_filter(message) is True


def test_true_if_has_not_enough_valid_messages(do_filter, message, valid_messages):
    LogEntry.get(LogEntry.message_id == 1).delete_instance()

    assert do_filter(message) is True


@pytest.mark.parametrize(
    ("attribute", "value"),
    [
        ("action", "delete"),
        ("chat_id", 4815),
        ("user_id", 9911),
    ]
)
def test_true_if_user_has_not_enough_valid_messages(do_filter, message, valid_messages, attribute, value):
    log_entry = LogEntry.get(LogEntry.message_id == 1)
    setattr(log_entry, attribute, value)
    log_entry.save()

    assert do_filter(message) is True


def test_false_if_has_valid_messages(do_filter, message, valid_messages):
    assert do_filter(message) is False


def test_false_if_true_oldfag(do_filter, message):
    message.from_user.id = 987654321  # still less than 10^9

    assert do_filter(message) is False
