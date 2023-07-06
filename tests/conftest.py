import pytest

from models import create_tables, db, drop_tables


@pytest.fixture(scope="session")
def test_db():
    create_tables()

    yield db

    drop_tables()


@pytest.fixture(scope='function', autouse=True)
def _rollback_transactions(test_db):
    test_db.begin()

    yield

    test_db.rollback()

@pytest.fixture
def mock_message(mocker):
    return mocker.patch("telegram.Message", autospec=True).return_value
