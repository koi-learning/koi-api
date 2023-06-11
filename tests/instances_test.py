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


def test_forbidden(auth_client: Tuple[FlaskClient, str]):
    client, header = auth_client
    model = make_empty_model(auth_client)
    instance = make_empty_instance(auth_client, model["model_uuid"])

    # put and delete are forbidden for instances
    ret = client.put(f"/api/model/{model['model_uuid']}/instance", headers=header, json={})
    assert ret.status_code == 405

    ret = client.delete(f"/api/model/{model['model_uuid']}/instance", headers=header)
    assert ret.status_code == 405

    # post is forbidden for single instances
    ret = client.post(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}", headers=header, json={})
    assert ret.status_code == 405

    # put and delete are forbidden for data on single instances
    for data in ["inference", "training"]:
        ret = client.put(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/{data}", headers=header, json={})
        assert ret.status_code == 405

        ret = client.delete(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/{data}", headers=header)
        assert ret.status_code == 405


def test_create_failure(auth_client: Tuple[FlaskClient, str]):
    client, header = auth_client
    model = make_empty_model(auth_client, finalized=False)

    # create an instance, but the model is not finalized
    ret = client.post(f"/api/model/{model['model_uuid']}/instance", headers=header, json={})
    assert ret.status_code == 400


def test_create(auth_client: Tuple[FlaskClient, str]):
    client, header = auth_client
    model = make_empty_model(auth_client)

    # create an instance
    ret = client.post(f"/api/model/{model['model_uuid']}/instance", headers=header, json={})
    assert ret.status_code == 200

    # create another instance, but this time with a name
    ret = client.post(f"/api/model/{model['model_uuid']}/instance", headers=header, json={"instance_name": "test", "instance_description": "test"})
    assert ret.status_code == 200
    assert ret.get_json()["instance_name"] == "test"
    assert ret.get_json()["instance_description"] == "test"

    # head request
    ret = client.head(f"/api/model/{model['model_uuid']}/instance", headers=header)
    assert ret.status_code == 200


def test_modify(auth_client: Tuple[FlaskClient, str]):
    client, header = auth_client
    model = make_empty_model(auth_client)
    instance = make_empty_instance(auth_client, model["model_uuid"])

    ret = client.get(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}", headers=header)
    assert ret.status_code == 200
    new_instance = ret.get_json()

    assert new_instance["instance_name"] != "test"
    assert new_instance["instance_description"] != "test"

    # wrongfully finalize the instance
    new_instance["finalized"] = "true"
    ret = client.put(f"/api/model/{model['model_uuid']}/instance/{new_instance['instance_uuid']}", headers=header, json=new_instance)
    assert ret.status_code == 400

    # modify the instance and read back the changes
    new_instance["instance_name"] = "test"
    new_instance["instance_description"] = "test"
    new_instance["finalized"] = True

    ret = client.put(f"/api/model/{model['model_uuid']}/instance/{new_instance['instance_uuid']}", headers=header, json=new_instance)
    assert ret.status_code == 200

    # read back the changes
    ret = client.get(f"/api/model/{model['model_uuid']}/instance/{new_instance['instance_uuid']}", headers=header)
    assert ret.status_code == 200
    read_instance = ret.get_json()

    for key in ["instance_name", "instance_description", "finalized"]:
        assert new_instance[key] == read_instance[key]

    # modifying a finalized instance is forbidden
    new_instance["finalized"] = False
    ret = client.put(f"/api/model/{model['model_uuid']}/instance/{new_instance['instance_uuid']}", headers=header, json=new_instance)
    assert ret.status_code == 400

    # head request on single instance should always work
    ret = client.head(f"/api/model/{model['model_uuid']}/instance/{new_instance['instance_uuid']}", headers=header)
    assert ret.status_code == 200


def test_delete(auth_client: Tuple[FlaskClient, str]):
    client, header = auth_client
    model = make_empty_model(auth_client)

    # create an instance
    ret = client.post(f"/api/model/{model['model_uuid']}/instance", headers=header, json={})
    assert ret.status_code == 200

    # parse the new instance
    new_instance = ret.get_json()

    # check that we can see the instance
    ret = client.get(f"/api/model/{model['model_uuid']}/instance", headers=header)
    assert ret.status_code == 200
    assert len(ret.get_json()) == 1

    # delete the instance
    ret = client.delete(f"/api/model/{model['model_uuid']}/instance/{new_instance['instance_uuid']}", headers=header)
    assert ret.status_code == 200

    # check that we can't see the instance
    ret = client.get(f"/api/model/{model['model_uuid']}/instance", headers=header)
    assert ret.status_code == 200
    assert len(ret.get_json()) == 0

    ret = client.get(f"/api/model/{model['model_uuid']}/instance/{new_instance['instance_uuid']}", headers=header)
    assert ret.status_code == 404
    

def test_data(auth_client: Tuple[FlaskClient, str]):
    client, header = auth_client
    model = make_empty_model(auth_client)
    instance = make_empty_instance(auth_client, model["model_uuid"])

    # inference and trainings data is handled the same so we can iterate over it
    datas = ["inference", "training"]
    for data_type in datas:
        # head and get should fail if there is no data
        ret = client.head(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/{data_type}", headers=header)
        assert ret.status_code == 404

        ret = client.get(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/{data_type}", headers=header)
        assert ret.status_code == 404

        # post should fail if the instance is not finalized
        ret = client.post(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/{data_type}", headers=header, json={})
        assert ret.status_code == 400

    # finalize the instance
    instance["finalized"] = True
    ret = client.put(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}", headers=header, json=instance)
    assert ret.status_code == 200

    # now we should be able to post data
    for data_type in datas:
        ret = client.post(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/{data_type}", headers=header, data=b"test")
        assert ret.status_code == 200

        # head and get should work
        ret = client.head(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/{data_type}", headers=header)
        assert ret.status_code == 200

        ret = client.get(f"/api/model/{model['model_uuid']}/instance/{instance['instance_uuid']}/{data_type}", headers=header)
        assert ret.status_code == 200


def not_instance_merging(testserver):
    try:
        koi.init()
    except koi.exceptions.KoiInitializationError:
        ...

    pool = koi.create_api_object_pool(*testserver)

    # create an empty model
    model = pool.new_model()
    model.code = Dummy()
    model.finalized = True

    # create two instances and finalize
    inst1 = model.new_instance()
    inst2 = model.new_instance()
    inst1.finalized = True
    inst2.finalized = True

    # give them some descriptors
    inst1.descriptors["c"].append("1")
    inst1.descriptors["c"].append("2")
    inst2.descriptors["c"].append("2")
    inst2.descriptors["c"].append("3")

    inst1.descriptors["a"].append("1")
    inst2.descriptors["b"].append("2")

    # create samples for these instances
    sample1 = inst1.new_sample()
    sample2 = inst2.new_sample()

    # give them some tags and labels
    sample1.tags.add("keep this")
    sample2.tags.add("keep this")

    sample1.labels["class1"].append(b"keep this label")
    sample2.labels["class1"].append(b"keep this label")
    sample2.labels["class2"].append(b"keep this label")

    # finalize the samples and add some non mergeable content
    sample1.finalized = True
    sample2.finalized = True

    sample1.tags.add("do not keep this")
    sample2.tags.add("do not keep this")

    sample1.labels["class1"].append(b"do not keep this")
    sample2.labels["class3"].append(b"do not keep this")

    # build a mergeable instance
    inst3 = model.new_instance()
    inst3.finalized = True

    # merge and get the samples
    inst3.merge([inst1, inst2])
    samples = list(inst3.get_samples())

    # get the descriptors after merging
    desc_a = [x.raw.decode() for x in inst3.descriptors["a"]]
    desc_b = [x.raw.decode() for x in inst3.descriptors["b"]]
    desc_c = [x.raw.decode() for x in inst3.descriptors["c"]]

    # check if we merged the descriptor correctly
    assert desc_a == ["1"]
    assert desc_b == ["2"]
    assert desc_c == ["1", "2", "3"]

    # the merged instance schould have two samples
    assert len(samples) == 2

    # check if we merged the tags correctly
    for sample in samples:
        assert "keep this" in sample.tags
        assert "do not keep this" not in sample.tags

        labels = [x.raw for x in sample.labels["class1"]]
        assert b"do not keep this" not in labels
        assert b"keep this label" in labels

        labels = [x.raw for x in sample.labels["class2"]]
        assert b"do not keep this" not in labels

        labels = [x.raw for x in sample.labels["class3"]]
        assert b"do not keep this" not in labels
