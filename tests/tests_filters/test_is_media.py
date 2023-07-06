import pytest

from filters import IsMedia


@pytest.fixture
def message(mock_message):
    mock_message.photo = []
    mock_message.document = None
    mock_message.audio = None
    mock_message.voice = None
    mock_message.video_note = None
    return mock_message


@pytest.fixture(scope="session")
def filter_obg():
    return IsMedia()


def test_false_if_empty_message(do_filter, message):
    assert do_filter(message) is False


@pytest.mark.parametrize(
    "photo",
    [
        "http://photo.com/",
        ["http://localhost/photo", "some-id-like-123"]
    ]
)
def test_true_if_has_photos(do_filter, message, photo):
    message.photo.append(photo)

    assert do_filter(message) is True


@pytest.mark.parametrize(
    "attribute",
    [
        "document",
        "audio",
        "voice",
        "video_note",
    ]
)
def test_true_if_has_media_attr(do_filter, message, attribute):
    setattr(message, attribute, "Here we are born to be kings")

    assert do_filter(message) is True
