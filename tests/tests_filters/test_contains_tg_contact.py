import pytest

from filters import ContainsTelegramContact


@pytest.fixture
def message(mock_message):
    message.text = "Ordinary text"
    return mock_message


@pytest.fixture(scope="session")
def filter_obg():
    return ContainsTelegramContact()


def test_false_if_no_text_message(do_filter, message):
    message.text = None
    assert do_filter(message) is False


@pytest.mark.parametrize(
    "text",
    [
        "Hello there!",
        "OMG look at my email omg@bbq.wtf",
        "sobaka@sobaka",
    ]
)
def test_false_if_no_contact(do_filter, message, text):
    message.text = text

    assert do_filter(message) is False


@pytest.mark.parametrize(
    "text",
    [
        "write me a message @bbqomg",
        "@contact_me",
    ]
)
def test_true_if_contact(do_filter, message, text):
    message.text = text

    assert do_filter(message) is True
