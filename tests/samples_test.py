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


def test_sample_forbidden(auth_client: Tuple[FlaskClient, str]):
    client, header = auth_client

    model = make_empty_model(auth_client)
    inst = make_empty_instance(auth_client, model["model_uuid"])
    assert inst["instance_uuid"] is not None

    # put on sample is forbidden
    ret = client.put(
        f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample",
        headers=header,
    )
    assert ret.status_code == 405

    # delete on sample is forbidden
    ret = client.delete(
        f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample",
        headers=header,
    )
    assert ret.status_code == 405

    # generate a sample
    sample = client.post(
        f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample",
        json={},  # empty sample
        headers=header,
    )
    assert sample.status_code == 200

    sample = sample.get_json()

    # post on specific sample is forbidden
    ret = client.post(
        f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample/{sample['sample_uuid']}",
        json={},  # empty sample
        headers=header,
    )
    assert ret.status_code == 405



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

    # add a misformed tag
    ret = client.put(
        f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample/{sample['sample_uuid']}/tags",
        json=[{"name": 123}],
        headers=header,
    )
    assert ret.status_code == 400

    ret = client.put(
        f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample/{sample['sample_uuid']}/tags",
        json=[{"not_name": "test"},],
        headers=header,
    )
    assert ret.status_code == 400

    ret = client.put(
        f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample/{sample['sample_uuid']}/tags",
        json={"name": "test"},
        headers=header,
    )
    assert ret.status_code == 400

    ret = client.put(
        f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample/{sample['sample_uuid']}/tags",
        json=["test", ],
        headers=header,
    )
    assert ret.status_code == 400

def test_head_sample(auth_client: Tuple[FlaskClient, str]):
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

    # head on sample
    ret = client.head(
        f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample/{sample['sample_uuid']}",
        headers=header,
    )
    assert ret.status_code == 200

    # finalize sample
    ret = client.put(
        f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample/{sample['sample_uuid']}",
        json={"finalized": True},
        headers=header,
    )
    assert ret.status_code == 200

    # head on finalized sample
    ret = client.head(
        f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample/{sample['sample_uuid']}",
        headers=header,
    )
    assert ret.status_code == 200

    ret = client.head(
        f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample",
        headers=header,
    )
    assert ret.status_code == 200


def test_finalize_and_delete(auth_client: Tuple[FlaskClient, str]):
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

    # finalize sample, but fail
    ret = client.put(
        f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample/{sample['sample_uuid']}",
        json={"finalized": "abc"},
        headers=header,
    )
    assert ret.status_code == 400

    # get the sample
    ret = client.get(
        f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample/{sample['sample_uuid']}",
        headers=header,
    )
    assert ret.status_code == 200
    sample = ret.get_json()

    # finalize sample
    ret = client.put(
        f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample/{sample['sample_uuid']}",
        json={"finalized": True},
        headers=header,
    )
    assert ret.status_code == 200

    # get the sample
    ret = client.get(
        f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample/{sample['sample_uuid']}",
        headers=header,
    )
    assert ret.status_code == 200

    # delete sample
    ret = client.delete(
        f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample/{sample['sample_uuid']}",
        headers=header,
    )
    assert ret.status_code == 200

    # delete sample again
    ret = client.delete(
        f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample/{sample['sample_uuid']}",
        headers=header,
    )
    assert ret.status_code == 404

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



def create_change_finalize_delete(auth_client: Tuple[FlaskClient, str], base_url, fails_on_finalized, key):
    client, header = auth_client

    # head
    ret = client.head(base_url, headers=header)
    assert ret.status_code == 200

    # get all existing
    ret = client.get(base_url, headers=header)
    assert ret.status_code == 200

    old_datas = ret.get_json()

    # create new
    ret = client.post(base_url, json={}, headers=header)
    if fails_on_finalized:
        assert ret.status_code == 400
    else:
        assert ret.status_code == 200
    
    # get all existing
    ret = client.get(base_url, headers=header)
    assert ret.status_code == 200
    
    new_datas = ret.get_json()

    if not fails_on_finalized:
        assert len(new_datas) == len(old_datas) + 1
    else:
        assert len(new_datas) == len(old_datas)
    
    # edit all existing
    for idx, data in enumerate(new_datas):
        ret = client.head(f"{base_url}/{data[key]}", headers=header)
        assert ret.status_code == 200

        ret = client.get(f"{base_url}/{data[key]}", headers=header)
        assert ret.status_code == 200

        ret = client.put(f"{base_url}/{data[key]}", json={"key":str(idx)}, headers=header)
        if fails_on_finalized:
            assert ret.status_code == 400
        else:
            assert ret.status_code == 200

        ret = client.post(f"{base_url}/{data[key]}", json={"key":str(idx)}, headers=header)
        assert ret.status_code == 405
    
    # delete all existing
    for data in new_datas:
        ret = client.delete(f"{base_url}/{data[key]}", headers=header)
        if fails_on_finalized:
            assert ret.status_code == 400
        else:
            assert ret.status_code == 200



def test_data_label(auth_client: Tuple[FlaskClient, str]):
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

    urls= [
        (f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample/{sample['sample_uuid']}/data", "data_uuid", True),
        (f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample/{sample['sample_uuid']}/label", "label_uuid", False),
    ]

    for url, _, _ in urls:
        # post new data/label
        ret = client.post(
            url,
            json={"key": "preset"},
            headers=header,
        )
        assert ret.status_code == 200

        ret = client.put(
            url,
            json={"key": "preset"},
            headers=header,
        )
        assert ret.status_code == 405

        ret = client.delete(
            url,
            headers=header,
        )
        assert ret.status_code == 405

    for url, key, _ in urls:
        create_change_finalize_delete(auth_client, url, False, key)
    
    for url, _, _ in urls:
        # post new data/label
        ret = client.post(
            url,
            json={"key": "preset"},
            headers=header,
        )
        assert ret.status_code == 200

    # finalize
    finalize = client.put(
        f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample/{sample['sample_uuid']}",
        json={"finalized": True},
        headers=header,
    )
    assert finalize.status_code == 200

    for url, key, fails in urls:
        create_change_finalize_delete(auth_client, url, fails, key)


def test_data_label_files(auth_client: Tuple[FlaskClient, str]):
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

    # add one data and label entry
    data = client.post(
        f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample/{sample['sample_uuid']}/data",
        json={"key": "preset"},
        headers=header,
    )
    assert data.status_code == 200

    label = client.post(
        f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample/{sample['sample_uuid']}/label",
        json={"key": "preset"},
        headers=header,
    )
    assert label.status_code == 200

    data = data.get_json()
    label = label.get_json()

    urls = [
        (f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample/{sample['sample_uuid']}/data/{data['data_uuid']}/file", True),
        (f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample/{sample['sample_uuid']}/label/{label['label_uuid']}/file", False),
    ]

    for url, _ in urls:
        # head the file
        ret = client.head(
            url,
            headers=header,
        )
        assert ret.status_code == 404

        # get the file
        ret = client.get(
            url,
            headers=header,
        )
        assert ret.status_code == 404

        # post new file
        ret = client.post(
            url,
            data=b"test",
            headers=header,
        )
        assert ret.status_code == 200

        # get the file
        ret = client.get(
            url,
            headers=header,
        )
        assert ret.status_code == 200
        assert ret.data == b"test"
    
    # finalize the sample
    finalize = client.put(
        f"/api/model/{model['model_uuid']}/instance/{inst['instance_uuid']}/sample/{sample['sample_uuid']}",
        json={"finalized": True},
        headers=header,
    )
    assert finalize.status_code == 200

    for url, fails in urls:
        # post new file
        ret = client.post(
            url,
            data=b"test",
            headers=header,
        )
        if fails:
            assert ret.status_code == 400
        else:
            assert ret.status_code == 200

        # head the file 
        ret = client.head(
            url,
            headers=header,
        )
        assert ret.status_code == 200

        # get the file
        ret = client.get(
            url,
            headers=header,
        )
        assert ret.status_code == 200
        assert ret.data == b"test"

        # delet and put should be illegal
        ret = client.delete(
            url,
            headers=header,
        )
        assert ret.status_code == 405

        ret = client.put(
            url,
            data=b"test",
            headers=header,
        )
        assert ret.status_code == 405