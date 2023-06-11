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


def test_forbidden(auth_client: Tuple[FlaskClient, dict]):
    client, header = auth_client

    ret = client.delete("/api/user", headers=header)
    assert ret.status_code == 405

    ret = client.put("/api/user", headers=header)
    assert ret.status_code == 405

    # create an empty user
    ret = client.post("/api/user", json={}, headers=header)
    assert ret.status_code == 200

    user_uuid = ret.get_json()["user_uuid"]

    ret = client.post(f"/api/user/{user_uuid}", json={}, headers=header)
    assert ret.status_code == 405


def test_add_user(auth_client: Tuple[FlaskClient, dict]):
    client, header = auth_client
    
    # get all users 
    ret = client.get("/api/user", headers=header)
    assert ret.status_code == 200

    users = ret.get_json()

    # add a new user with all information
    ret = client.post("/api/user", headers=header, json={
        "user_name": "test_user",
        "password": "test_password"
    })
    assert ret.status_code == 200

    # add a new user without any information
    ret = client.post("/api/user", headers=header, json={})
    assert ret.status_code == 200

    # add a new user, but user_name is already taken
    ret = client.post("/api/user", headers=header, json={
        "user_name": "test_user",
        "password": "test_password"
    })
    assert ret.status_code == 200

    # get all users again
    ret = client.get("/api/user", headers=header)
    assert ret.status_code == 200

    new_users = ret.get_json()

    # check if the new user is in the list

    assert len(new_users) == len(users) + 3


def test_change_user(auth_client: Tuple[FlaskClient, dict]):
    client, header = auth_client

    # create an empty user
    ret = client.post("/api/user", json={}, headers=header)
    assert ret.status_code == 200

    user_uuid = ret.get_json()["user_uuid"]

    # get the user details
    ret = client.get(f"/api/user/{user_uuid}", headers=header)
    assert ret.status_code == 200

    # change the name of the user
    ret = client.put(f"/api/user/{user_uuid}", headers=header, json={
        "user_name": "test_user_unique_never_used_before"
    })
    assert ret.status_code == 200

    # change the password of the user
    ret = client.put(f"/api/user/{user_uuid}", headers=header, json={
        "password": "test_password"
    })

    # change the name to something that is already taken
    ret = client.put(f"/api/user/{user_uuid}", headers=header, json={
        "user_name": "guest"
    })
    assert ret.status_code == 409


def test_delete_user(auth_client: Tuple[FlaskClient, str]):
    client, header = auth_client

    # create an empty user
    ret = client.post("/api/user", json={
        "user_name": "test_user_created_to_be_deleted",
        "password": "test_password"
    }, headers=header)
    assert ret.status_code == 200

    user_uuid = ret.get_json()["user_uuid"]

    # login as this user
    ret = client.post("/api/login", json={
        "user_name": "test_user_created_to_be_deleted",
        "password": "test_password"
    })
    assert ret.status_code == 200

    token = ret.get_json()["token"]

    # check if the session is working
    ret = client.get("/api/model", headers={"Authorization": f"Bearer {token}"})#
    assert ret.status_code == 200

    # delete the user
    ret = client.delete(f"/api/user/{user_uuid}", headers=header)
    assert ret.status_code == 200

    # check if the new users sessions are deleted
    ret = client.get("/api/model", headers={"Authorization": f"Bearer {token}"})
    assert ret.status_code == 401

    # try to delete a system user, which is not allowed
    ret = client.get("/api/user", headers=header)
    assert ret.status_code == 200

    users = ret.get_json()

    for user in users:
        if user["user_name"] == "admin":
            ret = client.delete(f"/api/user/{user['user_uuid']}", headers=header)
            assert ret.status_code == 405
