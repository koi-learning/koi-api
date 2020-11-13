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

import random

first = [
    "fast",
    "slow",
    "pink",
    "red",
    "yellow",
    "blue",
    "green",
    "loud",
    "silent",
    "flimsy",
    "dirty",
    "clean",
    "funny",
    "boring",
]

second = [
    "standing",
    "running",
    "sitting",
    "driving",
    "walking",
    "learning",
    "studying",
    "seeing",
    "smelling",
    "hearing",
    "tasting",
    "brewing",
]

third = [
    "hannes",
    "morty",
    "rick",
    "john",
    "kurt",
    "gandalf",
    "phillip",
    "jerry",
    "erik",
]


def gen_name():
    random.seed()

    ret = ""
    ret += random.choice(first)
    ret += "-"
    ret += random.choice(second)
    ret += "-"
    ret += random.choice(third)

    return ret
