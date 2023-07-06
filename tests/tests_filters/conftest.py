from typing import Callable

import pytest


@pytest.fixture
def do_filter(filter_obg) -> Callable[[], bool]:
    return lambda message: filter_obg.filter(message)
