import pytest

from equicafi.providers.demo import DemoProvider


@pytest.fixture
def demo_data():
    return DemoProvider().fetch("DEMO")
