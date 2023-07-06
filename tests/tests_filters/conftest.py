from typing import Callable

import pytest


@pytest.fixture
def do_filter(filter_obj) -> Callable[[], bool]:
    return lambda message: filter_obj.filter(message)
