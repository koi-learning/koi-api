from flask.testing import FlaskClient
from typing import Tuple


def test_get(auth_client: Tuple[FlaskClient, dict]):
    client, _ = auth_client
    ret = client.get("/health")
    assert ret.status_code == 200


def test_post(auth_client: Tuple[FlaskClient, dict]):
    client, _ = auth_client
    ret = client.post("/health")
    assert ret.status_code == 405


def test_put(auth_client: Tuple[FlaskClient, dict]):
    client, _ = auth_client
    ret = client.put("/health")
    assert ret.status_code == 405


def test_delete(auth_client: Tuple[FlaskClient, dict]):
    client, _ = auth_client
    ret = client.delete("/health")
    assert ret.status_code == 405
