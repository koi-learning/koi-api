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

from zipfile import ZipFile
from io import BytesIO
from typing import Tuple
from flask.testing import FlaskClient


class Dummy:
    def __init__(self, exclude_params: bool = False):
        self.data = BytesIO()
        with ZipFile(self.data, "w") as zip:
            with open("./tests/fixtures/model/__model__.py", "rb") as f:
                zip.writestr("__model__.py", f.read())
            if not exclude_params:
                with open("./tests/fixtures/model/__param__.py", "rb") as f:
                    zip.writestr("__param__.py", f.read())

    def toBytes(self):
        return self.data.getvalue()


def make_empty_model(auth_client: Tuple[FlaskClient, str], finalized=True):
    client, header = auth_client

    # add a model without information
    ret = client.post("/api/model", headers=header, json={})
    assert ret.status_code == 200

    # parse the new model
    new_model = ret.get_json()

    # add code to the model, or else it will not be finalized
    d = Dummy()
    ret = client.post(f"/api/model/{new_model['model_uuid']}/code", headers=header, data=d.toBytes())
    assert ret.status_code == 200

    if finalized:
        # finalize the model
        new_model["finalized"] = True
        ret = client.put(f"/api/model/{new_model['model_uuid']}", headers=header, json=new_model)
        assert ret.status_code == 200

    return new_model


def make_empty_instance(auth_client: Tuple[FlaskClient, str], model_uuid: str):
    client, header = auth_client

    # create an instance
    ret = client.post(f"/api/model/{model_uuid}/instance", headers=header, json={})
    assert ret.status_code == 200

    # parse the new instance
    new_instance = ret.get_json()

    return new_instance
