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
    
def sample_filtering(client):
    

    model = pool.new_model()
    model.code = Dummy()
    model.finalized = True

    # create two instances and finalize
    inst = model.new_instance()
    inst.finalized = True

    for _ in range(1):
        new_sample = inst.new_sample()
        new_sample.tags.add("A")
        new_sample.finalized = True

    for _ in range(3):
        new_sample = inst.new_sample()
        new_sample.tags.add("A")
        new_sample.tags.add("B")
        new_sample.finalized = True

    for _ in range(5):
        new_sample = inst.new_sample()
        new_sample.tags.add("B")
        new_sample.finalized = True

    all_a = inst.get_samples(filter_include=["A", ])
    assert len(all_a) == 1+3

    all_b = inst.get_samples(filter_include=["B", ])
    assert len(all_b) == 3+5

    only_a = inst.get_samples(filter_include=["A", ], filter_exclude=["B", ])
    assert len(only_a) == 1

    only_b = inst.get_samples(filter_include=["B", ], filter_exclude=["A", ])
    assert len(only_b) == 5
