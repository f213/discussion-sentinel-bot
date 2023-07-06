import pytest

from filters import ContainsLink


class FakeMessageEntity:
    def __init__(self, type: str):
        self.type = type


@pytest.fixture
def mock_message_entity(mocker):
    return lambda type_str: FakeMessageEntity(type_str)


@pytest.fixture
def message(mock_message, mock_message_entity):
    # To see all possible types look at telegram.MessageEntity Attributes
    message.text = "I'm not empty inside"
    code = mock_message_entity("code")
    phone_number = mock_message_entity("phone_number")
    mock_message.entities = [code, phone_number]
    return mock_message


@pytest.fixture(scope="session")
def filter_obg():
    return ContainsLink()


def test_false_if_no_links_message(do_filter, message):
    assert do_filter(message) is False


@pytest.mark.parametrize(
    "link_type",
    [
        "url",
        "text_link",
    ]
)
def test_true_if_has_link(do_filter, message, mock_message_entity, link_type):
    message_entity = mock_message_entity(link_type)
    message.entities.append(message_entity)

    assert do_filter(message) is True


@pytest.mark.parametrize(
    "link_types",
    [
        ["text_link", "url"],
        ["text_link", "text_link"],
        ["url", "url"],
    ]
)
def test_true_if_has_many_links(do_filter, message, mock_message_entity, link_types):
    for link_type in link_types:
        message_entity = mock_message_entity(link_type)
        message.entities.append(message_entity)

    assert do_filter(message) is True
