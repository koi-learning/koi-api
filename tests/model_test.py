from flask.testing import FlaskClient
from typing import Tuple
from . import Dummy


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
        "name": "test_model",
        "description": "test_description"
    })
    assert ret.status_code == 200

    # add a model without information

    ret = client.post("/api/model", headers=header, json={})
    assert ret.status_code == 200

    # check that the number of models has increased by 2
    ret = client.get("/api/model", headers=header)
    assert ret.status_code == 200
    assert len(ret.get_json()) == num_models + 2


def test_change_model(auth_client: Tuple[FlaskClient, dict]):
    client, header = auth_client
    
    # add a model without information
    ret = client.post("/api/model", headers=header, json={})
    assert ret.status_code == 200

    new_obj = ret.get_json()

    assert new_obj["model_name"] != "test_model"
    assert new_obj["model_description"] != "test_description"

    new_obj["model_name"] = "test_model"
    new_obj["model_description"] = "test_description"

    # change the model
    ret = client.put(f"/api/model/{new_obj['model_uuid']}", headers=header, json=new_obj)
    assert ret.status_code == 200

    # check that the model has changed
    ret = client.get(f"/api/model/{new_obj['model_uuid']}", headers=header)
    assert ret.status_code == 200
    assert ret.get_json()["model_name"] == "test_model"
    assert ret.get_json()["model_description"] == "test_description"


def test_finalized_model(auth_client: Tuple[FlaskClient, dict]):
    client, header = auth_client
    
    # add a model without information
    ret = client.post("/api/model", headers=header, json={})
    assert ret.status_code == 200

    new_obj = ret.get_json()

    assert new_obj["model_name"] != "test_model"
    assert new_obj["model_description"] != "test_description"

    d = Dummy()

    # add code to the model, or else it will not be finalized
    ret = client.post(f"/api/model/{new_obj['model_uuid']}/code", headers=header, data=d.toBytes())
    assert ret.status_code == 200

    # finalize the model
    new_obj["finalized"] = True

    # change the model
    ret = client.put(f"/api/model/{new_obj['model_uuid']}", headers=header, json=new_obj)
    assert ret.status_code == 200

    # check that the model has changed
    ret = client.get(f"/api/model/{new_obj['model_uuid']}", headers=header)
    assert ret.status_code == 200
    assert ret.get_json()["finalized"] == True
    
    # try to change the finalized model, which should fail
    new_obj["model_name"] = "test_model"
    new_obj["model_description"] = "test_description"
    ret = client.put(f"/api/model/{new_obj['model_uuid']}", headers=header, json=new_obj)

    assert ret.status_code == 400

