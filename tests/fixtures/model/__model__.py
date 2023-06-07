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

from typing import Any, List
import pickle
from koi_core.resources.instance import Instance


asset_dir = None
model = None


def set_asset_dir(dir: str):
    """get the asset directory and hold it for further access
    Args:
        dir (str): temporary directory with all model assets
    """
    global asset_dir
    asset_dir = dir


def batch_generator(instance: Instance):
    yield instance.get_samples(filter_include=["consumed"], filter_exclude=["obsolete"])


def initialize_training() -> None:
    global model
    model = "fresh model"


def train(batch: List[Any]) -> None:
    global model
    model = "trained model"


def infer(batch: List[Any], result: List[Any]) -> None:
    global model

    result["class_prob"] = [0.5, 0.3, 0.2]

    result["model_used"] = model


def should_create_training_data() -> bool:
    # we do not create training data, as the model is so small and we do not have enough data
    return False


def save_training_data() -> bytes:
    # we do not create training data, as the model is so small and we do not have enough data
    return None


def load_training_data(data: bytes) -> None:
    pass


def should_create_inference_data() -> bool:
    return True


def save_inference_data() -> bytes:
    global model

    return pickle.dumps(model)


def load_inference_data(data: bytes) -> None:
    global model
    model = pickle.loads(data)
