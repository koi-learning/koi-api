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


def test_forbidden_instance(auth_client: Tuple[FlaskClient, dict]):
    client, header = auth_client
    model = make_empty_model(auth_client)
    instance = make_empty_instance(auth_client, model['model_uuid'])
    
    ret = client.put(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/parameter", headers=header, json={})
    assert ret.status_code == 405

    ret = client.delete(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/parameter", headers=header, json={})
    assert ret.status_code == 405


def test_get_parameter_instance(auth_client: Tuple[FlaskClient, dict]):
    client, header = auth_client
    model = make_empty_model(auth_client)
    instance = make_empty_instance(auth_client, model['model_uuid'])
    
    ret = client.get(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/parameter", headers=header, json={})
    assert ret.status_code == 200


def test_post_paramater_instance(auth_client: Tuple[FlaskClient, dict]):
    client, header = auth_client
    model = make_empty_model(auth_client)
    instance = make_empty_instance(auth_client, model['model_uuid'])
    
    #get a parameter uuid
    ret = client.get(f"/api/model/{model['model_uuid']}/parameter", headers=header, json={})
    assert ret.status_code == 200
    param_uuid = ret.json[0]['param_uuid']

    # test empty call
    ret = client.post(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/parameter", headers=header, json={})
    assert ret.status_code == 400

    # test with maformed uuid
    ret = client.post(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/parameter", headers=header, json={
        "param_uuid": "not a uuid",
    })
    assert ret.status_code == 400

    # test with non existing uuid
    ret = client.post(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/parameter", headers=header, json={
        "param_uuid": "00000000-0000-0000-0000-000000000000",
    })
    assert ret.status_code == 404

    # test with existing uuid, no value
    ret = client.post(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/parameter", headers=header, json={
        "param_uuid": param_uuid,
    })
    assert ret.status_code == 200

    # test with existing uuid, value
    ret = client.post(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/parameter", headers=header, json={
        "param_uuid": param_uuid,
        "value": "test",
    })
    assert ret.status_code == 200

    # test with existing uuid, value, but wrong type
    ret = client.post(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/parameter", headers=header, json={
        "param_uuid": param_uuid,
        "value": [],
    })
    assert ret.status_code == 400

    # delete then post
    ret = client.get(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/parameter", headers=header, json={})
    assert ret.status_code == 200
    value_uuid = ret.json[0]['value_uuid']

    ret = client.delete(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/parameter/{value_uuid}", headers=header, json={})
    assert ret.status_code == 200

    ret = client.post(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/parameter", headers=header, json={
        "param_uuid": param_uuid,
        "value": "test",
    })
    assert ret.status_code == 200


def test_post_forbidden(auth_client: Tuple[FlaskClient, dict]):
    client, header = auth_client
    model = make_empty_model(auth_client)
    instance = make_empty_instance(auth_client, model['model_uuid'])

    #get a parameter uuid
    ret = client.get(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/parameter", headers=header, json={})
    assert ret.status_code == 200
    param_uuid = ret.json[0]['value_uuid']

    # test forbidden post to a specific parameter
    ret = client.post(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/parameter/{param_uuid}", headers=header, json={})
    assert ret.status_code == 405


def test_get_specific_param(auth_client: Tuple[FlaskClient, dict]):
    client, header = auth_client
    model = make_empty_model(auth_client)
    instance = make_empty_instance(auth_client, model['model_uuid'])

    #get a parameter uuid
    ret = client.get(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/parameter", headers=header, json={})
    assert ret.status_code == 200
    param_uuid = ret.json[0]['value_uuid']

    # get the specific parameter
    ret = client.get(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/parameter/{param_uuid}", headers=header, json={})
    assert ret.status_code == 200

    # get the specific parameter with a malformed uuid
    ret = client.get(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/parameter/not a uuid", headers=header, json={})
    assert ret.status_code == 400

    # get the specific parameter with a non existing uuid
    ret = client.get(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/parameter/00000000-0000-0000-0000-000000000000", headers=header, json={})
    assert ret.status_code == 404


def test_delete_specific_paramater(auth_client: Tuple[FlaskClient, dict]):
    client, header = auth_client
    model = make_empty_model(auth_client)
    instance = make_empty_instance(auth_client, model['model_uuid'])

    #get a parameter uuid
    ret = client.get(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/parameter", headers=header, json={})
    assert ret.status_code == 200
    param_uuid = ret.json[0]['value_uuid']
    num_params = len(ret.json)

    # delete the specific parameter
    ret = client.delete(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/parameter/{param_uuid}", headers=header, json={})
    assert ret.status_code == 200

    # check that the parameter is gone
    ret = client.get(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/parameter", headers=header, json={})
    assert ret.status_code == 200
    assert len(ret.json) == num_params - 1

    # delete the specific parameter with a malformed uuid
    ret = client.delete(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/parameter/not a uuid", headers=header, json={})
    assert ret.status_code == 400

    # delete the specific parameter with a non existing uuid
    ret = client.delete(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/parameter/00000000-0000-0000-0000-000000000000", headers=header, json={})
    assert ret.status_code == 404


def test_put_specific_parameter(auth_client: Tuple[FlaskClient, dict]):
    client, header = auth_client
    model = make_empty_model(auth_client)
    instance = make_empty_instance(auth_client, model['model_uuid'])

    #get a parameter uuid
    ret = client.get(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/parameter", headers=header, json={})
    assert ret.status_code == 200
    param_uuid = ret.json[0]['value_uuid']

    # put with malformed uuid
    ret = client.put(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/parameter/not a uuid", headers=header, json={})
    assert ret.status_code == 400

    # put with non existing uuid
    ret = client.put(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/parameter/00000000-0000-0000-0000-000000000000", headers=header, json={})
    assert ret.status_code == 404

    # put with existing uuid, no value
    ret = client.put(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/parameter/{param_uuid}", headers=header, json={})
    assert ret.status_code == 200

    # put with existing uuid, value
    ret = client.put(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/parameter/{param_uuid}", headers=header, json={
        "value": "test",
    })
    assert ret.status_code == 200

    # put with existing uuid, value, but wrong type
    ret = client.put(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/parameter/{param_uuid}", headers=header, json={
        "value": [],
    })
    assert ret.status_code == 400