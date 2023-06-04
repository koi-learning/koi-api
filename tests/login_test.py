from flask.testing import FlaskClient
from datetime import datetime
from typing import Tuple


def test_correct(auth_client: Tuple[FlaskClient, dict]):
    client, _ = auth_client
    ret = client.post("/api/login", json={
        "user_name": "guest",
        "password": "guest"
        })
    assert ret.status_code == 200

    token = ret.get_json()["token"]
    expires = ret.get_json()["expires"]

    assert token is not None
    assert expires is not None
    assert datetime.fromisoformat(expires) > datetime.utcnow()

    ret = client.post("/api/logout", headers={
        "Authorization": f"Bearer {token}",
        })
    
    assert ret.status_code == 200


def test_wrong_password(auth_client: Tuple[FlaskClient, dict]):
    client, _ = auth_client
    ret = client.post("/api/login", json={
        "user_name": "guest",
        "password": "wrong"
        })
    assert ret.status_code == 401