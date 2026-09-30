import os
import tempfile

import pytest

@pytest.fixture
def client():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.environ["STUDYLOG_DB"] = path

    from app import create_app
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client

    os.close(fd)
    os.unlink(path)
