from . import make_empty_model, make_empty_instance
from typing import Tuple
from flask.testing import FlaskClient


def test_forbidden(auth_client: Tuple[FlaskClient, dict]):
    client, header = auth_client
    model = make_empty_model(auth_client)
    instance = make_empty_instance(auth_client, model["model_uuid"])

    # put, post and delete are forbidden for tags
    ret = client.put(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/tags", headers=header, json={})
    assert ret.status_code == 405

    ret = client.post(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/tags", headers=header, json={})
    assert ret.status_code == 405

    ret = client.delete(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/tags", headers=header)
    assert ret.status_code == 405


def test_head(auth_client: Tuple[FlaskClient, dict]):
    client, header = auth_client
    model = make_empty_model(auth_client)
    instance = make_empty_instance(auth_client, model["model_uuid"])

    # head should return 200
    ret = client.head(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/tags", headers=header)
    assert ret.status_code == 200


def test_get(auth_client: Tuple[FlaskClient, dict]):
    client, header = auth_client
    model = make_empty_model(auth_client)
    instance = make_empty_instance(auth_client, model["model_uuid"])

    # get should return empty list
    ret = client.get(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/tags", headers=header)
    assert ret.status_code == 200
    assert ret.json == []


def test_add_samples_with_tags_and_get(auth_client: Tuple[FlaskClient, dict]):
    client, header = auth_client
    model = make_empty_model(auth_client)
    instance = make_empty_instance(auth_client, model["model_uuid"])

    # add samples with tags
    sample_uuids = []
    sample_tags = [
        {
            "name": "tag1",
        },
        {
            "name": "tag2",
        },
        {
            "name": "tag1",
        },
    ]
    for _ in range(3):
        ret = client.post(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/sample", headers=header, json={})
        assert ret.status_code == 200
        sample_uuids.append(ret.json["sample_uuid"])
    assert len(sample_uuids) == 3

    for sample_uuid, tag in zip(sample_uuids, sample_tags):
        ret = client.put(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/sample/{sample_uuid}/tags", headers=header, json=[tag,])
        assert ret.status_code == 200

    # get should return all tags
    ret = client.get(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/tags", headers=header)
    assert ret.status_code == 200
    assert len(ret.json) == 2