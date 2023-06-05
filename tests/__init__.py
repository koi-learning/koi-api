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
    def toBytes(self):
        data = BytesIO()
        f = ZipFile(data, "w")
        model_file = f.open("__model__.py", "w")
        model_file.write(b"")
        model_file.close()
        f.close()

        return data.getvalue()


def make_empty_model(auth_client: Tuple[FlaskClient, str]):
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
