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

from . import Dummy, make_empty_instance, make_empty_model
from typing import Tuple
from flask.testing import FlaskClient


def test_create(auth_client: Tuple[FlaskClient, str]):
    client, header = auth_client
    model = make_empty_model(auth_client)
    inst = make_empty_instance(auth_client, model["model_uuid"])
    assert inst["instance_uuid"] is not None

    samples = []

    # create 10 samples
    for _ in range(10):
        sample = client.post(
            f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample",
            json={},  # empty sample
            headers=header,
        )
        assert sample.status_code == 200
        samples.append(sample.get_json())

    # check that the sample is there
    ret = client.get(
        f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample",
        headers=header,
    )
    assert ret.status_code == 200
    ret = ret.get_json()
    assert len(ret) == 10

def test_sample_tags_forbidden(auth_client: Tuple[FlaskClient, str]):
    client, header = auth_client

    model = make_empty_model(auth_client)
    inst = make_empty_instance(auth_client, model["model_uuid"])
    assert inst["instance_uuid"] is not None

    sample = client.post(
        f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample",
        json={},  # empty sample
        headers=header,
    )
    assert sample.status_code == 200
    sample = sample.get_json()

    # post on a sample tag is forbidden
    ret = client.post(
        f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample/{sample['sample_uuid']}/tags",
        json={"tag": "test"},
        headers=header,
    )
    assert ret.status_code == 405

    # put, post, and get on a specific sample tag are forbidden
    ret = client.put(
        f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample/{sample['sample_uuid']}/tags/test",
        headers=header,
    )
    assert ret.status_code == 405

    ret = client.post(
        f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample/{sample['sample_uuid']}/tags/test",
        headers=header,
    )
    assert ret.status_code == 405

    ret = client.get(
        f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample/{sample['sample_uuid']}/tags/test",
        headers=header,
    )
    assert ret.status_code == 405


def test_sample_tags(auth_client: Tuple[FlaskClient, str]):
    client, header = auth_client

    model = make_empty_model(auth_client)
    inst = make_empty_instance(auth_client, model["model_uuid"])
    assert inst["instance_uuid"] is not None

    sample = client.post(
        f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample",
        json={},  # empty sample
        headers=header,
    )
    assert sample.status_code == 200
    sample = sample.get_json()

    def get_tags():
        ret = client.head(
            f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample/{sample['sample_uuid']}/tags",
            headers=header,
        )
        assert ret.status_code == 200

        ret = client.get(
            f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample/{sample['sample_uuid']}/tags",
            headers=header,
        )
        assert ret.status_code == 200
        return ret.get_json()

    # get the tags
    assert get_tags() == []

    # add a tag
    ret = client.put(
        f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample/{sample['sample_uuid']}/tags",
        json=[{"name": "test"}],
        headers=header,
    )
    assert ret.status_code == 200

    # add multiple tags
    ret = client.put(
        f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample/{sample['sample_uuid']}/tags",
        json=[{"name": "test2"}, {"name": "test3"}],
        headers=header,
    )
    assert ret.status_code == 200

    # get the tags
    assert get_tags() == [{"name": "test"}, {"name": "test2"}, {"name": "test3"}]

    # delete a tag
    ret = client.delete(
        f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample/{sample['sample_uuid']}/tags/test2",
        headers=header,
    )
    assert ret.status_code == 200

    # get the tags
    assert get_tags() == [{"name": "test"}, {"name": "test3"}]

    # delete all tags
    ret = client.delete(
        f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample/{sample['sample_uuid']}/tags",
        headers=header,
    )
    assert ret.status_code == 200

    # get the tags
    assert get_tags() == []


def test_sample_filtering(auth_client: Tuple[FlaskClient, str]):
    client, header = auth_client
    model = make_empty_model(auth_client)
    inst = make_empty_instance(auth_client, model["model_uuid"])
    assert inst["instance_uuid"] is not None

    def add_sample(tags, finalize=False):
        ret = client.post(
            f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample",
            json={},
            headers=header,
        )
        assert ret.status_code == 200
        sample = ret.get_json()

        if finalize:
            ret = client.put(
                f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample/{sample['sample_uuid']}",
                headers=header,
                json={"finalized": True},
            )
            assert ret.status_code == 200

        tag_dict = [{"name": t} for t in tags]    
        ret = client.put(
            f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample/{sample['sample_uuid']}/tags",
            json=tag_dict,
            headers=header,
        )
        assert ret.status_code == 200

    for _ in range(1):
        add_sample(["A"])

    for _ in range(3):
        add_sample(["A", "B"], finalize=True)

    for _ in range(5):
        add_sample(["B"])

    all_a = client.get(
        f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample?inc_tags=A",
        headers=header,
    )
    assert all_a.status_code == 200    
    all_a = all_a.get_json()
    assert len(all_a) == 1+3

    all_b = client.get(
        f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample?inc_tags=B",
        headers=header,
    )
    assert all_b.status_code == 200
    all_b = all_b.get_json()
    assert len(all_b) == 3+5
    
    only_a = client.get(
        f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample?inc_tags=A&exc_tags=B",
        headers=header,
    )
    assert only_a.status_code == 200
    only_a = only_a.get_json()
    assert len(only_a) == 1

    only_b = client.get(
        f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample?inc_tags=B&exc_tags=A",
        headers=header,
    )
    assert only_b.status_code == 200
    only_b = only_b.get_json()
    assert len(only_b) == 5
