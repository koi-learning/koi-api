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
from uuid import UUID, uuid4
from koi_api.orm import db
from koi_api.resources.base import (
    BaseResource,
    authenticated,
    model_access,
    instance_access,
    json_request,
)
from koi_api.common.string_constants import BODY_ROLE as BR, BODY_PARAM as BP
from koi_api.common.return_codes import SUCCESS, ERR_FORB, ERR_NOFO, ERR_BADR, ERR_FATL
from koi_api.orm.parameters import ORMInstanceParameter, ORMModelParameter


class APIModelParameter(BaseResource):
    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    def get(self, model_uuid, model, me):
        params = ORMModelParameter.query.filter_by(model_id=model.model_id).all()

        response = [
            {
                BP.PARAM_UUID: UUID(bytes=param.param_uuid).hex,
                BP.PARAM_NAME: param.param_name,
                BP.PARAM_DESCRIPTION: param.param_description,
                BP.PARAM_CONSTRAINT: param.param_constraint,
                BP.PARAM_TYPE: param.param_type,
            }
            for param in params
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
        try:
            param_uuid = UUID(param_uuid)
        except ValueError:
            return ERR_BADR("misformed parameter uuid")

        param = ORMModelParameter.query.filter_by(
            model_id=model.model_id,
            param_uuid=param_uuid.bytes
        ).one_or_none()
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
    def post(self, model_uuid, model, me, param_uuid):
        return ERR_FORB()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    def put(self, model_uuid, model, me, param_uuid):
        return ERR_FORB()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    def delete(self, model_uuid, model, me, param_uuid):
        return ERR_FORB()


class APIInstanceParameter(BaseResource):
    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    def get(
        self, model_uuid, model: ORMModel, instance_uuid, instance: ORMInstance, me
    ):
        params = ORMInstanceParameter.query.filter_by(
            instance_id=instance.instance_id
        ).all()
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
            for param in params
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

        model_param = ORMModelParameter.query.filter_by(
            param_uuid=model_param_uuid.bytes
        ).one_or_none()

        if model_param is None:
            return ERR_NOFO("model parameter is unknown")

        instance_param_value = ""
        if BP.PARAM_VALUE in json_object:
            instance_param_value = json_object[BP.PARAM_VALUE]
            if not any([isinstance(instance_param_value, t) for t in [str, int, float]]):
                return ERR_BADR("wrong field type: " + BP.PARAM_VALUE)
            
        instance_param = ORMInstanceParameter.query.filter_by(
            model_param_id=model_param.param_id
        ).one_or_none()

        if instance_param is None:
            instance_param = ORMInstanceParameter()
            instance_param.param_uuid = uuid4().bytes
            instance_param.param_value = instance_param_value
            instance_param.model_param = model_param
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
        
        try:
            param_uuid = UUID(param_uuid)
        except ValueError:
            return ERR_BADR("misformed parameter uuid")

        param = ORMInstanceParameter.query.filter_by(
            instance_id=instance.instance_id,
            param_uuid=param_uuid.bytes
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
        try:
            param_uuid = UUID(param_uuid)
        except ValueError:
            return ERR_BADR("misformed parameter uuid")

        param = ORMInstanceParameter.query.filter_by(
            instance_id=instance.instance_id,
            param_uuid=param_uuid.bytes
        ).one_or_none()

        if param is None:
            return ERR_NOFO("parameter is unknown")

        if BP.PARAM_VALUE in json_object:
            param.param_value = json_object[BP.PARAM_VALUE]
            if not any([isinstance(param.param_value, t) for t in [str, int, float]]):
                return ERR_BADR("wrong field type: " + BP.PARAM_VALUE)

        db.session.commit()
        return SUCCESS()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    def delete(self, model_uuid, model, instance_uuid, instance, me, param_uuid):
        try:
            param_uuid = UUID(param_uuid)
        except ValueError:
            return ERR_BADR("misformed parameter uuid")

        param = ORMInstanceParameter.query.filter_by(
            instance_id=instance.instance_id,
            param_uuid=param_uuid.bytes
        ).one_or_none()

        if param is None:
            return ERR_NOFO("parameter is unknown")

        db.session.delete(param)
        db.session.commit()
        return SUCCESS()
