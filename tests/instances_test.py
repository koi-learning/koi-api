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
from . import Dummy


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
