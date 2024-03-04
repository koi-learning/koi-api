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
from . import Dummy, make_empty_model

def test_forbidden(auth_client: Tuple[FlaskClient, dict]):
    # the model endpoint does not allow to use put and delete
    client, header = auth_client
    ret = client.put("/api/model", headers=header)
    assert ret.status_code == 405

    ret = client.delete("/api/model", headers=header)
    assert ret.status_code == 405

    # one individual model does not allow to call post
    model = make_empty_model(auth_client)
    ret = client.post(f"/api/model/{model['model_uuid']}", json={}, headers=header)
    assert ret.status_code == 405

    #code, visual plugin and request plugin endpoints do not allow to use put and delete
    endpoints = [
        "code",
        "visualplugin",
        "requestplugin",
    ]

    for endpoint in endpoints:
        ret = client.put(f"/api/model/{model['model_uuid']}/{endpoint}", headers=header)
        assert ret.status_code == 405

        ret = client.delete(f"/api/model/{model['model_uuid']}/{endpoint}", headers=header)
        assert ret.status_code == 405


def test_head(auth_client: Tuple[FlaskClient, dict]):
    # head for the model endpoint should return 200, always
    client, header = auth_client
    ret = client.head("/api/model", headers=header)
    assert ret.status_code == 200

    # head for an individual model should return 200 if the model exists
    model = make_empty_model(auth_client)
    ret = client.head(f"/api/model/{model['model_uuid']}", headers=header)
    assert ret.status_code == 200


def test_unauthenticated_models(auth_client: Tuple[FlaskClient, dict]):
    client, _ = auth_client
    ret = client.get("/api/model")
    assert ret.status_code == 401


def test_models(auth_client: Tuple[FlaskClient, dict]):
    client, header = auth_client
        
    ret = client.get("/api/model", headers=header)
    assert ret.status_code == 200


def test_create_model(auth_client: Tuple[FlaskClient, dict]):
    client, header = auth_client
    ret = client.get("/api/model", headers=header)

    assert ret.status_code == 200
    num_models = len(ret.get_json())

    # add a model with information
    ret = client.post("/api/model", headers=header, json={
        "model_name": "test_model",
        "model_description": "test_description"
    })
    assert ret.status_code == 200
    assert ret.get_json()["model_name"] == "test_model"
    assert ret.get_json()["model_description"] == "test_description"

    # add a model without information
    ret = client.post("/api/model", headers=header, json={})
    assert ret.status_code == 200

    # check that the number of models has increased by 2
    ret = client.get("/api/model", headers=header)
    assert ret.status_code == 200
    assert len(ret.get_json()) == num_models + 2


def test_modify_model(auth_client: Tuple[FlaskClient, dict]):
    client, header = auth_client
    
    # add a model without information
    ret = client.post("/api/model", headers=header, json={})
    assert ret.status_code == 200

    model = ret.get_json()

    assert model["model_name"] != "test_model"
    assert model["model_description"] != "test_description"

    model["model_name"] = "test_model"
    model["model_description"] = "test_description"

    # change the model
    ret = client.put(f"/api/model/{model['model_uuid']}", headers=header, json=model)
    assert ret.status_code == 200

    # check that the model has changed
    ret = client.get(f"/api/model/{model['model_uuid']}", headers=header)
    assert ret.status_code == 200
    assert ret.get_json()["model_name"] == "test_model"
    assert ret.get_json()["model_description"] == "test_description"

    # models cannot be finalized if the finalized field does not contain a boolean
    model["finalized"] = "test"
    ret = client.put(f"/api/model/{model['model_uuid']}", headers=header, json=model)
    assert ret.status_code == 400

    # models cannot be finalized if code is missing
    model["finalized"] = True
    ret = client.put(f"/api/model/{model['model_uuid']}", headers=header, json=model)
    assert ret.status_code == 400

    # add code to the model, or else it will not be finalized
    d = Dummy()
    ret = client.post(f"/api/model/{model['model_uuid']}/code", headers=header, data=d.toBytes())
    assert ret.status_code == 200

    # finalize the model
    model["finalized"] = True
    ret = client.put(f"/api/model/{model['model_uuid']}", headers=header, json=model)
    assert ret.status_code == 200

    # check that the model has changed (is finalized)
    ret = client.get(f"/api/model/{model['model_uuid']}", headers=header)
    assert ret.status_code == 200
    assert ret.get_json()["finalized"] == True
    
    # try to change the finalized model, which should fail
    model["model_name"] = "test_model"
    model["model_description"] = "test_description"
    ret = client.put(f"/api/model/{model['model_uuid']}", headers=header, json=model)
    assert ret.status_code == 400


def test_delete(auth_client: Tuple[FlaskClient, dict]):
    client, header = auth_client
    
    # get the number of current models
    ret = client.get("/api/model", headers=header)
    assert ret.status_code == 200
    num_models = len(ret.get_json())

    # add a model without information
    ret = client.post("/api/model", headers=header, json={})
    assert ret.status_code == 200

    new_obj = ret.get_json()

    # check that the number of models has increased by 1
    ret = client.get("/api/model", headers=header)
    assert ret.status_code == 200
    assert len(ret.get_json()) == num_models + 1

    # delete the model
    ret = client.delete(f"/api/model/{new_obj['model_uuid']}", headers=header)
    assert ret.status_code == 200

    # check that the model has been deleted
    ret = client.get(f"/api/model/{new_obj['model_uuid']}", headers=header)
    assert ret.status_code == 404

    # check that the number of models has decreased by 1
    ret = client.get("/api/model", headers=header)
    assert ret.status_code == 200
    assert len(ret.get_json()) == num_models


def test_code(auth_client: Tuple[FlaskClient, dict]):
    client, header = auth_client

    # add a model without information
    ret = client.post("/api/model", headers=header, json={})
    assert ret.status_code == 200

    model = ret.get_json()

    # try to get the model code, which should fail
    ret = client.get(f"/api/model/{model['model_uuid']}/code", headers=header)
    assert ret.status_code == 404

    # add a broken zipfile, which should fail
    ret = client.post(f"/api/model/{model['model_uuid']}/code", headers=header, data=b"not a valid zip file")
    assert ret.status_code == 400

    # add a valid zipfile
    d = Dummy()
    ret = client.post(f"/api/model/{model['model_uuid']}/code", headers=header, data=d.toBytes())
    assert ret.status_code == 200

    # finalize the model and reupload the code, which should fail
    model["finalized"] = True
    ret = client.put(f"/api/model/{model['model_uuid']}", headers=header, json=model)
    assert ret.status_code == 200

    ret = client.post(f"/api/model/{model['model_uuid']}/code", headers=header, data=d.toBytes())
    assert ret.status_code == 400

    # get the model code, which should succeed
    ret = client.get(f"/api/model/{model['model_uuid']}/code", headers=header)
    assert ret.status_code == 200
    assert ret.data == d.toBytes()

    # head request to model
    ret = client.head(f"/api/model/{model['model_uuid']}/code", headers=header)
    assert ret.status_code == 200


def test_plugins(auth_client: Tuple[FlaskClient, dict]):
    # plugins can be changed at any time (even if finalized)
    # visual and request plugins are handled the same way

    client, header = auth_client
    
    model = make_empty_model(auth_client)

    plugins = [
        "visualplugin",
        "requestplugin",
    ]

    for plugin in plugins:
        ret = client.get(f"/api/model/{model['model_uuid']}/{plugin}", headers=header)
        assert ret.status_code == 404

        ret = client.post(f"/api/model/{model['model_uuid']}/{plugin}", headers=header, data=b"pattern")
        assert ret.status_code == 200

        ret = client.get(f"/api/model/{model['model_uuid']}/{plugin}", headers=header)
        assert ret.status_code == 200
        assert ret.get_data() == b"pattern"

