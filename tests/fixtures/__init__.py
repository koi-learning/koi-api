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

import pytest
from koi_api import create_app
from flask import Flask
from flask.testing import FlaskClient
from typing import Tuple


@pytest.fixture(scope="session")
def app() -> Flask:
    app = create_app()
    app.config.update({
        "TESTING": True,
    })

    # other setup can go here

    yield app

    # clean up / reset resources here


@pytest.fixture(scope="session")
def auth_client(app: Flask) -> Tuple[FlaskClient, dict]:
    c = app.test_client()

    ret = c.post("/api/login", json={
        "user_name": "admin",
        "password": "admin",
    })

    assert ret.status_code == 200
    token = ret.json["token"]
    header = {
        "Authorization": f"Bearer {token}",
    }
    return app.test_client(), header
