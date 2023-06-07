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