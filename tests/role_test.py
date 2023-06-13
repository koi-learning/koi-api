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

from typing import Tuple
from flask.testing import FlaskClient


paths = [
    "/api/userroles/general",
    "/api/userroles/model",
    "/api/userroles/instance",
]


def test_forbidden(auth_client: Tuple[FlaskClient, str]):
    client, header = auth_client

    for path in paths:
        # get all roles
        response = client.put(path, headers=header)
        assert response.status_code == 405

        response = client.delete(path, headers=header)
        assert response.status_code == 405

        response = client.post(f"{path}/00000000-0000-0000-0000-000000000000", headers=header)
        assert response.status_code == 405



def test_roles(auth_client: Tuple[FlaskClient, str]):
    client, header = auth_client

    for path in paths:
        # get all roles
        response = client.get(path, headers=header)
        assert response.status_code == 200
        
        roles = response.get_json()

        # add a role without information
        response = client.post(path, headers=header, json={})
        assert response.status_code == 200

        role = response.get_json()
        fields = [x for x in role.keys() if x not in ["role_uuid", "role_name", "role_description"]]

        # add a role with information
        new_obj = {x: True for x in fields}
        new_obj["role_name"] = "test"
        new_obj["role_description"] = "test"
        response = client.post(path, headers=header, json=new_obj)
        assert response.status_code == 200

        # get this role
        role2 = response.get_json()
        response = client.get(path + "/" + role2["role_uuid"], headers=header)
        assert response.status_code == 200
        
        role2 = response.get_json()

        # add role and force a parsing error
        for field in fields:
            ret = client.post(path, headers=header, json={field: [10, 11, 12]})
            assert ret.status_code == 400

        # modify a role
        for field in fields + ["role_name", "role_description"]:
            ret = client.put(path + "/" + role["role_uuid"], headers=header, json={field: True})
            assert ret.status_code == 200

        # modify a role and force a parsing error
        for field in fields:
            ret = client.put(path + "/" + role["role_uuid"], headers=header, json={field: [10, 11, 12]})
            assert ret.status_code == 400

        # get all roles
        response = client.get(path, headers=header)
        assert response.status_code == 200

        roles2 = response.get_json()

        assert len(roles2) == len(roles) + 2

        # delete the new roles
        ret = client.delete(path + "/" + role["role_uuid"], headers=header)
        assert ret.status_code == 200

        ret = client.delete(path + "/" + role2["role_uuid"], headers=header)
        assert ret.status_code == 200

        # delete again, should fail
        ret = client.delete(path + "/" + role["role_uuid"], headers=header)
        assert ret.status_code == 404

        for r in roles:
            if r["role_name"] in ["owner", "admin"]:
                # try to delete, should fail because it is a essential role
                ret = client.delete(path + "/" + r["role_uuid"], headers=header)
                assert ret.status_code == 400
        
        # get a role that does not exist
        ret = client.get(path + "/" + role["role_uuid"], headers=header)
        assert ret.status_code == 404

        # modify a role that does not exist
        ret = client.put(path + "/" + role["role_uuid"], headers=header, json={"role_name": "test"})
        assert ret.status_code == 404
