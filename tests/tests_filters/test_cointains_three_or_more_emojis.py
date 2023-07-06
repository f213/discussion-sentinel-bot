import pytest

from filters import ContainsThreeOrMoreEmojies


@pytest.fixture
def message(mock_message):
    mock_message.text = None
    return mock_message


@pytest.fixture(scope="session")
def filter_obj():
    return ContainsThreeOrMoreEmojies()


def test_false_if_empty_message(do_filter, message):
    assert do_filter(message) is False


@pytest.mark.parametrize(
    "text",
    [
        "Shalom 👋🏾",
        "Ou ui 👀🙃",
        "No emojis actually",
        "🐍",
        " ",
    ]
)
def test_false_if_less_than_3_emojis(do_filter, message, text):
    message.text = text

    assert do_filter(message) is False


@pytest.mark.parametrize(
    "text",
    [
        "Shalom 👋🏾👀🙃",
        "😅😎🧑🏿‍🦱👨‍👨‍👧‍👧",
        "😅😎🧑🏿‍🦱👨‍👨‍👧‍👧🐍 some text 👋🏾👀🙃",
    ]
)
def test_true_if_more_than_2_emojis(do_filter, message, text):
    message.text = text

    assert do_filter(message) is True
