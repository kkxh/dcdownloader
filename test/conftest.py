import time
from urllib.request import urlopen

import pytest

from test.testserver import server


@pytest.fixture(scope='session')
def test_server():
    server.launch()
    deadline = time.time() + 5
    while time.time() < deadline:
        try:
            with urlopen('http://localhost:32321/', timeout=0.2):
                return
        except OSError:
            time.sleep(0.1)
    raise RuntimeError('test server did not start')
