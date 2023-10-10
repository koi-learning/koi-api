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

from . import Dummy, make_empty_model, make_empty_instance
from typing import Tuple
from flask.testing import FlaskClient


def test_make_request_and_get(auth_client: Tuple[FlaskClient, str]):
    client, header = auth_client
    model = make_empty_model(auth_client)
    instance = make_empty_instance(auth_client, model["model_uuid"])

    # add an sample and make a request
    response = client.post(
        f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/sample",
        headers=header,
        json={},
    )
    assert response.status_code == 200
    sample = response.json

    response = client.post(
        f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/label_request",
        headers=header,
        json={"sample_uuid": sample["sample_uuid"]},
    )
    assert response.status_code == 200
    
    response = client.get(
        f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/label_request",
        headers=header,
    )
    assert response.status_code == 200
    assert len(response.json) == 1

    response = client.get(
        f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/label_request?obsolete=1",
        headers=header,
    )
    assert response.status_code == 200
    assert len(response.json) == 0


def test_post_request_wrong_sample(auth_client: Tuple[FlaskClient, str]):
    client, header = auth_client
    model = make_empty_model(auth_client)
    instance = make_empty_instance(auth_client, model["model_uuid"])

    response = client.post(
        f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/label_request",
        headers=header,
        json={},
    )
    assert response.status_code == 400

    response = client.post(
        f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/label_request",
        headers=header,
        json={"sample_uuid": "not a uuid"},
    )
    assert response.status_code == 400

    response = client.post(
        f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/label_request",
        headers=header,
        json={"sample_uuid": "00000000-0000-0000-0000-000000000000"},
    )
    assert response.status_code == 404

def test_forbidden(auth_client: Tuple[FlaskClient, str]):
    client, header = auth_client
    model = make_empty_model(auth_client)
    instance = make_empty_instance(auth_client, model["model_uuid"])

    # put and delete are forbidden
    response = client.put(
        f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/label_request",
        headers=header,
        json={},
    )
    assert response.status_code == 405

    response = client.delete(
        f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/label_request",
        headers=header,
    )
    assert response.status_code == 405


def test_single_request(auth_client: Tuple[FlaskClient, str]):
    client, header = auth_client
    model = make_empty_model(auth_client)
    instance = make_empty_instance(auth_client, model["model_uuid"])

    # add an sample and make a request
    response = client.post(
        f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/sample",
        headers=header,
        json={},
    )
    assert response.status_code == 200
    sample = response.json

    response = client.post(
        f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/label_request",
        headers=header,
        json={"sample_uuid": sample["sample_uuid"]},
    )
    assert response.status_code == 200
    request = response.json

    # get the request
    response = client.get(
        f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/label_request/{request['label_request_uuid']}",
        headers=header,
    )
    assert response.status_code == 200

    # get the request with a wrong uuid
    response = client.get(
        f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/label_request/00000000-0000-0000-0000-000000000000",
        headers=header,
    )
    assert response.status_code == 404

    # get the request with a malformed uuid
    response = client.get(
        f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/label_request/not a uuid",
        headers=header,
    )
    assert response.status_code == 400

    # close the request with a field
    response = client.put(
        f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/label_request/{request['label_request_uuid']}",
        headers=header,
        json={"obsolete": "eins"},
    )

    # close the request
    response = client.put(
        f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/label_request/{request['label_request_uuid']}",
        headers=header,
        json={"obsolete": 1},
    )
    assert response.status_code == 200

    # close the request with a wrong uuid
    response = client.put(
        f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/label_request/00000000-0000-0000-0000-000000000000",
        headers=header,
        json={"obsolete": 1},
    )
    assert response.status_code == 404

    # close the request with a malformed uuid
    response = client.put(
        f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/label_request/not a uuid",
        headers=header,
        json={"obsolete": 1},
    )
    assert response.status_code == 400

    # delete the request
    response = client.delete(
        f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/label_request/{request['label_request_uuid']}",
        headers=header,
    )
    assert response.status_code == 200

    # delete the request again
    response = client.delete(
        f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/label_request/{request['label_request_uuid']}",
        headers=header,
    )
    assert response.status_code == 404

    # delete the request with a wrong uuid
    response = client.delete(
        f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/label_request/00000000-0000-0000-0000-000000000000",
        headers=header,
    )
    assert response.status_code == 404

    # delete the request with a malformed uuid
    response = client.delete(
        f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/label_request/not a uuid",
        headers=header,
    )
    assert response.status_code == 400


def test_post_request(auth_client: Tuple[FlaskClient, str]):
    client, header = auth_client
    model = make_empty_model(auth_client)
    instance = make_empty_instance(auth_client, model["model_uuid"])

    # add an sample and make a request
    response = client.post(
        f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/sample",
        headers=header,
        json={},
    )
    assert response.status_code == 200
    sample = response.json

    response = client.post(
        f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/label_request",
        headers=header,
        json={"sample_uuid": sample["sample_uuid"]},
    )
    assert response.status_code == 200
    request = response.json

    # post the request and check if the sample has a new label
    response = client.post(
        f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/label_request/{request['label_request_uuid']}",
        headers=header,
        data=b"test",
    )
    assert response.status_code == 200

    response = client.get(
        f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/sample/{sample['sample_uuid']}/label",
        headers=header,
    )
    assert response.status_code == 200
    assert len(response.json) == 1

    response = client.post(
        f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/label_request/{request['label_request_uuid']}",
        headers=header,
        data=b"test",
    )
    assert response.status_code == 200

    response = client.get(
        f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/sample/{sample['sample_uuid']}/label",
        headers=header,
    )
    assert response.status_code == 200
    assert len(response.json) == 2

    # post the request with a wrong uuid
    response = client.post(
        f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/label_request/00000000-0000-0000-0000-000000000000",
        headers=header,
        data=b"test",
    )
    assert response.status_code == 404

    # post the request with a malformed uuid
    response = client.post(
        f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/label_request/not a uuid",
        headers=header,
        data=b"test",
    )
    assert response.status_code == 400
