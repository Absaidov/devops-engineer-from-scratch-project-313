import pytest
from fastapi.testclient import TestClient

from main import create_app


@pytest.fixture
def client(tmp_path):
    database_file = tmp_path / "test.db"
    app = create_app(
        database_url=f"sqlite:///{database_file}",
        base_url="https://short.io",
    )
    with TestClient(app) as test_client:
        yield test_client
