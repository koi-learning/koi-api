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
