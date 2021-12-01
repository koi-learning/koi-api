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
import koi_core as koi
from . import Dummy


def test_sample_filtering(testserver):
    try:
        koi.init()
    except koi.exceptions.KoiInitializationError:
        ...

    pool = koi.create_api_object_pool(*testserver)

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
