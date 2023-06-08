from . import make_empty_model, make_empty_instance
from typing import Tuple
from flask.testing import FlaskClient


def test_forbidden(auth_client: Tuple[FlaskClient, str]):
    client, header = auth_client
    model = make_empty_model(auth_client)
    instance = make_empty_instance(auth_client, model["model_uuid"])

    # put and delete are forbidden for descriptors
    ret = client.put(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/descriptor", headers=header, json={})
    assert ret.status_code == 405

    ret = client.delete(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/descriptor", headers=header)
    assert ret.status_code == 405

    # create a descriptor
    ret = client.post(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/descriptor", headers=header, json={})
    assert ret.status_code == 200

    desc = ret.get_json()

    # post and delete are forbidden for descriptors

    ret = client.post(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/descriptor/{desc['descriptor_uuid']}", headers=header, json={})
    assert ret.status_code == 405

    ret = client.delete(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/descriptor/{desc['descriptor_uuid']}", headers=header)
    assert ret.status_code == 405

     # delete and put are not allowed for files
    ret = client.delete(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/descriptor/{desc['descriptor_uuid']}/file", headers=header)
    assert ret.status_code == 405

    ret = client.put(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/descriptor/{desc['descriptor_uuid']}/file", headers=header, data=b"test2")
    assert ret.status_code == 405


def test_create(auth_client: Tuple[FlaskClient, str]):
    client, header = auth_client
    model = make_empty_model(auth_client)
    instance = make_empty_instance(auth_client, model["model_uuid"])

    # create a descriptor
    ret = client.post(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/descriptor", headers=header, json={})
    assert ret.status_code == 200
    
    desc = ret.get_json()
    assert desc["descriptor_uuid"] is not None
    assert desc["has_file"] is False

    # create a descriptor with a key
    ret = client.post(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/descriptor", headers=header, json={"key": "test"})
    assert ret.status_code == 200

    # get all descriptors, should be 2
    ret = client.get(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/descriptor", headers=header)
    assert ret.status_code == 200
    assert len(ret.get_json()) == 2


def test_modify(auth_client: Tuple[FlaskClient, str]):
    client, header = auth_client

    model = make_empty_model(auth_client)
    instance = make_empty_instance(auth_client, model["model_uuid"])

    # create a descriptor
    ret = client.post(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/descriptor", headers=header, json={})
    assert ret.status_code == 200

    desc = ret.get_json()

    # modify the descriptor
    desc["key"] = "something_different"
    ret = client.put(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/descriptor/{desc['descriptor_uuid']}", headers=header, json=desc)
    assert ret.status_code == 200

    # read back the descriptor
    ret = client.get(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/descriptor/{desc['descriptor_uuid']}", headers=header)
    assert ret.status_code == 200

    desc = ret.get_json()
    assert desc["key"] == "something_different"

    # no make a head request, wich should always return 200
    ret = client.head(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/descriptor/{desc['descriptor_uuid']}", headers=header)
    assert ret.status_code == 200


def test_file(auth_client: Tuple[FlaskClient, str]):
    client, header = auth_client

    model = make_empty_model(auth_client)
    instance = make_empty_instance(auth_client, model["model_uuid"])

    # create a descriptor
    ret = client.post(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/descriptor", headers=header, json={})
    assert ret.status_code == 200

    desc = ret.get_json()

    # download the file, which should fail
    ret = client.get(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/descriptor/{desc['descriptor_uuid']}/file", headers=header)
    assert ret.status_code == 404

    # upload a file
    ret = client.post(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/descriptor/{desc['descriptor_uuid']}/file", headers=header, data=b"test")
    assert ret.status_code == 200

    # download the file
    ret = client.get(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/descriptor/{desc['descriptor_uuid']}/file", headers=header)
    assert ret.status_code == 200
    assert ret.data == b"test"

    # overwrite the file
    ret = client.post(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/descriptor/{desc['descriptor_uuid']}/file", headers=header, data=b"test2")
    assert ret.status_code == 200

    # download the file
    ret = client.get(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/descriptor/{desc['descriptor_uuid']}/file", headers=header)
    assert ret.status_code == 200
    assert ret.data == b"test2"

    # head request should always return 200
    ret = client.head(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/descriptor/{desc['descriptor_uuid']}/file", headers=header)
    assert ret.status_code == 200
