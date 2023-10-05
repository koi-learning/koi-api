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
from . import make_empty_model


def test_forbidden_model(auth_client: Tuple[FlaskClient, dict]):
    # the model parameter endpoint does not allow to use put, post and delete
    client, header = auth_client
    model = make_empty_model(auth_client)
    
    ret = client.put(f"/api/model/{model['model_uuid']}/parameter", headers=header, json={})
    assert ret.status_code == 405

    ret = client.post(f"/api/model/{model['model_uuid']}/parameter", headers=header, json={})
    assert ret.status_code == 405

    ret = client.delete(f"/api/model/{model['model_uuid']}/parameter", headers=header, json={})
    assert ret.status_code == 405


def test_get_all_parameters(auth_client: Tuple[FlaskClient, dict]):
    # get all parameters for a model
    client, header = auth_client
    model = make_empty_model(auth_client)

    ret = client.get(f"/api/model/{model['model_uuid']}/parameter", headers=header)
    assert ret.status_code == 200

    # check if the response is a list
    assert isinstance(ret.json, list)


def test_forbidden_specific_parameter(auth_client: Tuple[FlaskClient, dict]):
    # the model parameter endpoint does not allow to use put and delete
    client, header = auth_client
    model = make_empty_model(auth_client)

    ret = client.put(f"/api/model/{model['model_uuid']}/parameter/123", headers=header, json={})
    assert ret.status_code == 405

    ret = client.post(f"/api/model/{model['model_uuid']}/parameter/123", headers=header, json={})
    assert ret.status_code == 405

    ret = client.delete(f"/api/model/{model['model_uuid']}/parameter/123", headers=header, json={})
    assert ret.status_code == 405


def test_get_specific_parameter(auth_client: Tuple[FlaskClient, dict]):
    client, header = auth_client
    model = make_empty_model(auth_client)

    # get all parameters for a model
    ret = client.get(f"/api/model/{model['model_uuid']}/parameter", headers=header)
    assert ret.status_code == 200

    param_uuid = ret.json[0]['param_uuid']

    ret = client.get(f"/api/model/{model['model_uuid']}/parameter/{param_uuid}", headers=header)
    assert ret.status_code == 200

    # check if the response is a dict
    assert isinstance(ret.json, dict)

    # check access to non-existing parameter
    ret = client.get(f"/api/model/{model['model_uuid']}/parameter/00000000-0000-0000-0000-000000000000", headers=header)
    assert ret.status_code == 404

    # check access to non-valid uuid
    ret = client.get(f"/api/model/{model['model_uuid']}/parameter/123", headers=header)
    assert ret.status_code == 400
