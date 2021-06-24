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

from koi_api.orm.model import ORMModel
from koi_api.orm.instance import ORMInstance
from uuid import UUID, uuid1
from ..orm import db
from ..resources.base import (
    BaseResource,
    authenticated,
    model_access,
    instance_access,
    json_request,
)
from ..common.string_constants import BODY_ROLE as BR, BODY_PARAM as BP
from ..common.return_codes import SUCCESS, ERR_FORB, ERR_NOFO, ERR_BADR
from ..orm.parameters import ORMInstanceParameter


class APIModelParameter(BaseResource):
    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    def get(self, model_uuid, model, me):
        response = [
            {
                BP.PARAM_UUID: UUID(bytes=param.param_uuid).hex,
                BP.PARAM_NAME: param.param_name,
                BP.PARAM_DESCRIPTION: param.param_description,
                BP.PARAM_CONSTRAINT: param.param_constraint,
                BP.PARAM_TYPE: param.param_type,
            }
            for param in model.params.all()
        ]
        return SUCCESS(response)

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    def post(self, model_uuid, model, me):
        return ERR_FORB()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    def put(self, model_uuid, model, me):
        return ERR_FORB()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    def delete(self, model_uuid, model, me):
        return ERR_FORB()


class APIModelParameterCollection(BaseResource):
    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    def get(self, model_uuid, model, me, param_uuid):
        param = model.params.filter_by(param_uuid=UUID(param_uuid).bytes).one_or_none()
        if param is None:
            return ERR_NOFO()

        response = {
            BP.PARAM_UUID: UUID(bytes=param.param_uuid).hex,
            BP.PARAM_NAME: param.param_name,
            BP.PARAM_DESCRIPTION: param.param_description,
            BP.PARAM_CONSTRAINT: param.param_constraint,
            BP.PARAM_TYPE: param.param_type,
        }
        return SUCCESS(response)

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    def post(self, model_uuid, model, me):
        return ERR_FORB()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    def put(self, model_uuid, model, me):
        return ERR_FORB()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    def delete(self, model_uuid, model, me):
        return ERR_FORB()


class APIInstanceParameter(BaseResource):
    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    def get(
        self, model_uuid, model: ORMModel, instance_uuid, instance: ORMInstance, me
    ):
        response = [
            {
                BP.PARAM_UUID_VALUE: UUID(bytes=param.param_uuid).hex,
                BP.PARAM_UUID: UUID(bytes=param.model_param.param_uuid),
                BP.PARAM_VALUE: param.param_value,
                BP.PARAM_NAME: param.model_param.param_name,
                BP.PARAM_DESCRIPTION: param.model_param.param_description,
                BP.PARAM_CONSTRAINT: param.model_param.param_constraint,
                BP.PARAM_TYPE: param.model_param.param_type,
            }
            for param in instance.params.all()
        ]
        return SUCCESS(response)

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @json_request
    def post(self, model_uuid, model, instance_uuid, instance, me, json_object):
        model_param_uuid = None

        if BP.PARAM_UUID in json_object:
            try:
                model_param_uuid = UUID(json_object[BP.PARAM_UUID])
            except ValueError:
                return ERR_BADR("misformed field:" + BP.PARAM_UUID)
        else:
            return ERR_BADR("missing field: " + BP.PARAM_UUID)

        model_param = model.params.filter_by(
            param_uuid=model_param_uuid.bytes
        ).one_or_none()

        if model_param is None:
            return ERR_NOFO("model parameter is unknown")

        instance_param_value = ""
        if BP.PARAM_VALUE in json_object:
            try:
                instance_param_value = json_object[BP.PARAM_VALUE]
            except ValueError:
                return ERR_BADR()

        instance_param = instance.params.filter_by(
            model_param_id=model_param.param_id
        ).one_or_none()

        if instance_param is None:
            instance_param = ORMInstanceParameter()
            instance_param.param_uuid = uuid1().bytes
            instance_param.param_value = instance_param_value
            instance_param.model_param_id = model_param.param_id
            db.session.add(instance_param)
        else:
            instance_param.param_value = instance_param_value
        db.session.commit()
        return SUCCESS()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    def put(self, model_uuid, model, instance_uuid, instance, me):
        return ERR_FORB()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    def delete(self, model_uuid, model, instance_uuid, instance, me):
        return ERR_FORB()


class APIInstanceParameterCollection(BaseResource):
    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    def get(self, model_uuid, model, instance_uuid, instance, me, param_uuid):
        param = instance.params.filter_by(
            param_uuid=UUID(param_uuid).bytes
        ).one_or_none()

        if param is None:
            return ERR_NOFO("parameter is unknown")

        response = {
            BP.PARAM_UUID: UUID(bytes=param.model_param.param_uuid).hex,
            BP.PARAM_UUID_VALUE: UUID(bytes=param.param_uuid).hex,
            BP.PARAM_VALUE: param.param_value,
        }
        return SUCCESS(response)

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    def post(self, model_uuid, model, instance_uuid, instance, me, param_uuid):
        return ERR_FORB()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @json_request
    def put(
        self, model_uuid, model, instance_uuid, instance, me, param_uuid, json_object
    ):
        param = instance.params.filter_by(
            param_uuid=UUID(param_uuid).bytes
        ).one_or_none()

        if param is None:
            return ERR_NOFO("parameter is unknown")

        if BP.PARAM_VALUE in json_object:
            try:
                param.param_value = json_object[BP.PARAM_VALUE]
            except ValueError:
                return ERR_BADR()

        db.session.commit()
        return SUCCESS()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    def delete(self, model_uuid, model, instance_uuid, instance, me, param_uuid):
        param = instance.params.filter_by(
            param_uuid=UUID(param_uuid).bytes
        ).one_or_none()

        if param is None:
            return ERR_NOFO("parameter is unknown")

        db.session.delete(param)
        return SUCCESS()
