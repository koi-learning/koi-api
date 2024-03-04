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
from . import make_empty_model, make_empty_instance


def get_paths(auth_client: Tuple[FlaskClient, dict]):
    model = make_empty_model(auth_client)
    instance = make_empty_instance(auth_client, model["model_uuid"])
    paths = [
        ("/api/access", "admin", "general"),
        (f"/api/model/{model['model_uuid']}/access", "owner", "model"),
        (f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/access", "owner", "instance"),
    ]

    return paths


def test_access_forbidden(auth_client: Tuple[FlaskClient, dict]):
    client, header = auth_client

    for path, _, _ in get_paths(auth_client):

        # put a general access
        ret = client.put(path, headers=header)
        assert ret.status_code == 405

        # delete a general access
        ret = client.delete(path, headers=header)
        assert ret.status_code == 405

        # post on a general access object
        ret = client.post(f"{path}/00000000-0000-0000-0000-000000000000", headers=header)
        assert ret.status_code == 405

        # put on a general access object
        ret = client.put(f"{path}/00000000-0000-0000-0000-000000000000", headers=header)
        assert ret.status_code == 405


def test_access(auth_client: Tuple[FlaskClient, dict]):
    client, header = auth_client
    
    # get the uuid of the user guest
    ret = client.get("/api/user", headers=header)
    assert ret.status_code == 200

    guest_uuid = None
    for user in ret.get_json():
        if user["user_name"] == "guest":
            guest_uuid = user["user_uuid"]
            break
    assert guest_uuid is not None

    paths = get_paths(auth_client)

    for path, role_name, role_path in paths:

        # get the uuid of the role admin
        ret = client.get(f"/api/userroles/{role_path}", headers=header)
        assert ret.status_code == 200

        admin_uuid = None
        for role in ret.get_json():
            if role["role_name"] == role_name:
                admin_uuid = role["role_uuid"]
                break
        assert admin_uuid is not None


        # enumerate the existing general accesses
        ret = client.get(path, headers=header)
        assert ret.status_code == 200

        # create a new general access without a user, should fail
        ret = client.post(path, headers=header, json={
            "role_uuid": admin_uuid,
        })
        assert ret.status_code == 400

        # create a new general access without a role, should fail
        ret = client.post(path, headers=header, json={
            "user_uuid": guest_uuid,
        })
        assert ret.status_code == 400

        # create a new general access with a non-existing user, should fail
        ret = client.post(path, headers=header, json={
            "user_uuid": "00000000-0000-0000-0000-000000000000",
            "role_uuid": admin_uuid,
        })
        assert ret.status_code == 404

        # create a new general access with a non-existing role, should fail
        ret = client.post(path, headers=header, json={
            "user_uuid": guest_uuid,
            "role_uuid": "00000000-0000-0000-0000-000000000000",
        })
        assert ret.status_code == 404

        # create a new general access, should succeed
        ret = client.post(path, headers=header, json={
            "user_uuid": guest_uuid,
            "role_uuid": admin_uuid,
        })
        assert ret.status_code == 200
        access = ret.get_json()

        # create a new general access, should fail because it already exists
        ret = client.post(path, headers=header, json={
            "user_uuid": guest_uuid,
            "role_uuid": admin_uuid,
        })
        assert ret.status_code == 409

        # get our new general access
        ret = client.get(f"{path}/{access['access_uuid']}", headers=header)
        assert ret.status_code == 200

        # delete the general access
        ret = client.delete(f"{path}/{access['access_uuid']}", headers=header)
        assert ret.status_code == 200

        # requery the object, should fail
        ret = client.get(f"{path}/{access['access_uuid']}", headers=header)
        assert ret.status_code == 404

        # delete again, should fail
        ret = client.delete(f"{path}/{access['access_uuid']}", headers=header)
        assert ret.status_code == 404
