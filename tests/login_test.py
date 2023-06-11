# Copyright (c) individual contributors.
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 3 of
# the License, or any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details. A copy of the
# GNU Lesser General Public License is distributed along with this
# software and can be found at http://www.gnu.org/licenses/lgpl.html

from flask.testing import FlaskClient
from datetime import datetime
from typing import Tuple
from time import sleep


def test_forbidden(auth_client: Tuple[FlaskClient, dict]):
    client, _ = auth_client

    ret = client.get("/api/logout")
    assert ret.status_code == 405

    ret = client.put("/api/logout")
    assert ret.status_code == 405

    ret = client.delete("/api/logout")
    assert ret.status_code == 405

    ret = client.get("/api/login")
    assert ret.status_code == 405

    ret = client.put("/api/login")
    assert ret.status_code == 405

    ret = client.delete("/api/login")
    assert ret.status_code == 405


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


def test_incomplete(auth_client: Tuple[FlaskClient, dict]):
    client, _ = auth_client
    ret = client.post("/api/login", json={
        "user_name": "guest",
        })
    assert ret.status_code == 400

    ret = client.post("/api/login", json={
        "password": "guest",
        })
    assert ret.status_code == 400


def test_unknown_user(auth_client: Tuple[FlaskClient, dict]):
    client, _ = auth_client
    ret = client.post("/api/login", json={
        "user_name": "unknown",
        "password": "guest"
        })
    assert ret.status_code == 404


def test_exhausted_tokenspace(auth_client: Tuple[FlaskClient, dict], monkeypatch):
    client, _ = auth_client

    # monkeypatch the token_hex generator to alwyas return the same value
    with monkeypatch.context() as m:
        m.setattr("secrets.token_hex", lambda _: "0" * 32)

        # login 1
        ret = client.post("/api/login", json={
            "user_name": "guest",
            "password": "guest"
        })
        
        assert ret.status_code == 200

        # login 2

        ret = client.post("/api/login", json={
            "user_name": "guest",
            "password": "guest"
        })

        assert ret.status_code == 500
