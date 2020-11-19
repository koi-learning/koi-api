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

from flask_restful import request
from flask import send_file
from flasgger import swag_from
from io import BytesIO
from uuid import uuid1, UUID
from datetime import datetime
from .base import (
    BaseResource,
    authenticated,
    paged,
    model_access,
    instance_access,
    descriptor_access,
    json_request,
)
from ..orm import db
from ..persistence import persistence
from ..orm.instance import (
    ORMInstance,
    ORMInstanceInferenceData,
    ORMInstanceTrainingData,
    ORMInstanceDescriptor,
)
from ..orm.access import ORMAccessInstance
from ..orm.role import ORMUserRoleInstance
from ..common.return_codes import ERR_FORB, ERR_NOFO, SUCCESS, ERR_BADR
from ..common.string_constants import BODY_INSTANCE as BI, BODY_ROLE as BR
from ..common.name_generator import gen_name
from .lifetime import (
    LT_INSTANCE,
    LT_INSTANCE_FINALIZED,
    LT_COLLECTION,
    LT_INFERENCE_DATA,
    LT_INSTANCE_DESCRIPTOR,
)


class APIInstanceDescriptor(BaseResource):
    @paged
    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    def get(
        self, model, model_uuid, me, instance, instance_uuid, page_offset, page_limit
    ):
        descriptors = (
            instance.instance_descriptors.offset(page_offset).limit(page_limit).all()
        )

        response = [
            {
                BI.INSTANCE_DESCRIPTOR_UUID: UUID(bytes=descriptor.descriptor_uuid).hex,
                BI.INSTANCE_DESCRIPTOR_KEY: descriptor.descriptor_key,
                BI.INSTANCE_DESCRIPTOR_KEY_HAS_FILE: descriptor.file is not None,
            }
            for descriptor in descriptors
        ]

        return SUCCESS(
            response, last_modified=datetime.utcnow(), valid_seconds=LT_COLLECTION
        )

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @json_request
    def post(self, model, model_uuid, me, instance, instance_uuid, json_object):
        new_uuid = uuid1()
        new_desc = ORMInstanceDescriptor()
        new_desc.descriptor_instance_id = instance.instance_id
        new_desc.descriptor_uuid = new_uuid.bytes

        # check if the request is complete
        if BI.INSTANCE_DESCRIPTOR_KEY in json_object:
            new_desc.descriptor_key = json_object[BI.INSTANCE_DESCRIPTOR_KEY]
        else:
            new_desc.descriptor_key = "unnamed data"

        db.session.add(new_desc)

        instance.instance_last_modified = datetime.utcnow()
        db.session.commit()

        response = {
            BI.INSTANCE_DESCRIPTOR_UUID: new_uuid.hex,
            BI.INSTANCE_DESCRIPTOR_KEY: new_desc.descriptor_key,
            BI.INSTANCE_DESCRIPTOR_KEY_HAS_FILE: new_desc.file is not None,
        }

        return SUCCESS(
            response, last_modified=datetime.utcnow(), valid_seconds=LT_INSTANCE
        )

    @authenticated
    @model_access([BR.ROLE_SEE_INSTANCE])
    def put(self, model_uuid, model, me):
        return ERR_FORB()

    @authenticated
    @model_access([BR.ROLE_SEE_INSTANCE])
    def delete(self, model_uuid, model, me):
        return ERR_FORB()


class APIInstanceDescriptorCollection(BaseResource):
    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @descriptor_access
    def head(
        self,
        model,
        model_uuid,
        me,
        instance,
        instance_uuid,
        descriptor_uuid,
        descriptor,
    ):
        return SUCCESS(
            "",
            last_modified=instance.instance_last_modified,
            valid_seconds=LT_INSTANCE_DESCRIPTOR,
        )

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @descriptor_access
    def get(
        self,
        model,
        model_uuid,
        me,
        instance,
        instance_uuid,
        descriptor_uuid,
        descriptor,
    ):
        response = {
            BI.INSTANCE_DESCRIPTOR_UUID: UUID(bytes=descriptor.descriptor_uuid).hex,
            BI.INSTANCE_DESCRIPTOR_KEY: descriptor.descriptor_key,
            BI.INSTANCE_DESCRIPTOR_KEY_HAS_FILE: descriptor.file is not None,
        }

        return SUCCESS(
            response,
            last_modified=instance.instance_last_modified,
            valid_seconds=LT_COLLECTION,
        )

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    def post(self, model, model_uuid, me, instance, instance_uuid, descriptor_uuid):
        return ERR_FORB()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @descriptor_access
    @json_request
    def put(
        self,
        model,
        model_uuid,
        me,
        instance,
        instance_uuid,
        descriptor_uuid,
        descriptor,
        json_object,
    ):
        if BI.INSTANCE_DESCRIPTOR_KEY in json_object:
            descriptor.descriptor_key = json_object[BI.INSTANCE_DESCRIPTOR_KEY]
            instance.instance_last_modified = datetime.utcnow()

        db.session.commit()

        response = {
            BI.INSTANCE_DESCRIPTOR_UUID: UUID(bytes=descriptor.descriptor_uuid).hex,
            BI.INSTANCE_DESCRIPTOR_KEY: descriptor.descriptor_key,
        }

        return SUCCESS(
            response,
            last_modified=instance.instance_last_modified,
            valid_seconds=LT_INSTANCE,
        )

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    def delete(self, model, model_uuid, me, instance, instance_uuid, descriptor_uuid):
        return ERR_FORB()


class APIInstanceDescriptorFile(BaseResource):
    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @descriptor_access
    def head(
        self,
        model_uuid,
        model,
        instance_uuid,
        instance,
        descriptor_uuid,
        descriptor,
        me,
    ):
        return SUCCESS(
            "", last_modified=instance.instance_last_modified, valid_seconds=LT_INSTANCE
        )

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @descriptor_access
    def get(
        self,
        model_uuid,
        model,
        instance_uuid,
        instance,
        descriptor_uuid,
        descriptor,
        me,
    ):
        if descriptor.file is None:
            return ERR_NOFO("no data specified")
        else:
            data_raw = persistence.get_file(descriptor.file)
            data_raw = BytesIO(data_raw)
            data_raw.seek(0)
            return send_file(
                data_raw,
                mimetype="application/octet-stream",
                last_modified=instance.instance_last_modified,
                cache_timeout=LT_INSTANCE,
            )

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @descriptor_access
    def post(
        self,
        model_uuid,
        model,
        instance_uuid,
        instance,
        descriptor_uuid,
        descriptor,
        me,
    ):
        data_raw = request.data
        file_pers = persistence.store_file(data_raw)

        descriptor.descriptor_file_id = file_pers.file_id

        db.session.add(file_pers)
        db.session.commit()

        return SUCCESS()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @descriptor_access
    def put(
        self,
        model_uuid,
        model,
        instance_uuid,
        instance,
        descriptor_uuid,
        descriptor,
        me,
    ):
        return ERR_FORB()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @descriptor_access
    def delete(
        self,
        model_uuid,
        model,
        instance_uuid,
        instance,
        descriptor_uuid,
        descriptor,
        me,
    ):
        return ERR_FORB()


class APIInstance(BaseResource):
    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    def head(self, model, model_uuid, me):
        return SUCCESS(
            "",
            last_modified=model.model_instances_last_modified,
            valid_seconds=LT_COLLECTION,
        )

    @paged
    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @swag_from("../apidef/instance/get.yml")
    def get(self, model, model_uuid, me, page_offset, page_limit):
        # get the instances
        query = model.instances.join(ORMInstance.granted_users).filter_by(
            user_id=me.user_id
        )
        query = (
            query.join(ORMAccessInstance.role)
            .filter_by(can_see=1)
            .offset(page_offset)
            .limit(page_limit)
        )
        instances = query.all()

        response = [
            {
                BI.INSTANCE_UUID: UUID(bytes=instance.instance_uuid).hex,
                BI.INSTANCE_NAME: instance.instance_name,
                BI.INSTANCE_DESCRIPTION: instance.instance_description,
                BI.INSTANCE_HAS_INFERENCE: instance.inference_data is not None,
                BI.INSTANCE_HAS_TRAINING: instance.training_data is not None,
                BI.INSTANCE_FINALIZED: instance.instance_finalized,
                BI.INSTANCE_COULD_TRAIN: instance.instance_finalized
                and (
                    instance.instance_last_modified
                    < instance.instance_samples_last_modified
                ),
            }
            for instance in instances
        ]

        return SUCCESS(
            response,
            last_modified=model.model_instances_last_modified,
            valid_seconds=LT_COLLECTION,
        )

    @authenticated
    @model_access([BR.ROLE_INSTANTIATE_MODEL, BR.ROLE_SEE_MODEL])
    @json_request
    @swag_from("../apidef/instance/post.yml")
    def post(self, model_uuid, model, me, json_object):
        """Make a new instance for the given model.
        The model has to be finalized in order to build an instance.
        """

        if not model.model_finalized:
            return ERR_BADR("model not finalized")

        new_uuid = uuid1()
        new_inst = ORMInstance()
        new_inst.instance_uuid = new_uuid.bytes
        new_inst.model_id = model.model_id
        new_inst.instance_finalized = False
        new_inst.instance_last_modified = datetime.utcnow()
        new_inst.instance_samples_last_modified = datetime.utcnow()

        model.model_instances_last_modified = datetime.utcnow()

        # check if the request is complete
        if BI.INSTANCE_NAME in json_object:
            new_inst.instance_name = json_object[BI.INSTANCE_NAME]
        else:
            new_inst.instance_name = gen_name()

        if BI.INSTANCE_DESCRIPTION in json_object:
            new_inst.instance_description = json_object[BI.INSTANCE_DESCRIPTION]
        else:
            new_inst.instance_description = "created by " + me.user_name

        # add the new instance
        db.session.add(new_inst)
        db.session.commit()

        owner_role = ORMUserRoleInstance.query.first()

        # construct the access object
        access = ORMAccessInstance()
        access.role_id = owner_role.role_id
        access.user_id = me.user_id
        access.instance_id = new_inst.instance_id
        access.access_uuid = uuid1().bytes

        db.session.add(access)
        db.session.commit()

        return SUCCESS(
            {
                BI.INSTANCE_UUID: UUID(bytes=new_inst.instance_uuid).hex,
                BI.INSTANCE_NAME: new_inst.instance_name,
                BI.INSTANCE_DESCRIPTION: new_inst.instance_description,
                BI.INSTANCE_HAS_INFERENCE: False,
                BI.INSTANCE_HAS_TRAINING: False,
                BI.INSTANCE_FINALIZED: new_inst.instance_finalized,
                BI.INSTANCE_COULD_TRAIN: new_inst.instance_finalized
                and (
                    new_inst.instance_last_modified
                    < new_inst.instance_samples_last_modified
                ),
            },
            last_modified=new_inst.instance_last_modified,
            valid_seconds=LT_INSTANCE,
        )

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    def put(self, model_uuid, model, me):
        return ERR_FORB()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    def delete(self, model_uuid, model, me):
        return ERR_FORB()


class APIInstanceCollection(BaseResource):
    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    def head(self, model_uuid, model, instance_uuid, instance, me):
        valid = LT_INSTANCE
        if instance.instance_finalized:
            valid = LT_INSTANCE_FINALIZED
        return SUCCESS(
            "", last_modified=instance.instance_last_modified, valid_seconds=valid
        )

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @swag_from("../apidef/instance_collection/get.yml")
    def get(self, model_uuid, model, instance_uuid, instance, me):

        # build the response
        response = {
            BI.INSTANCE_UUID: UUID(bytes=instance.instance_uuid).hex,
            BI.INSTANCE_NAME: instance.instance_name,
            BI.INSTANCE_DESCRIPTION: instance.instance_description,
            BI.INSTANCE_HAS_INFERENCE: instance.inference_data is not None,
            BI.INSTANCE_HAS_TRAINING: instance.training_data is not None,
            BI.INSTANCE_FINALIZED: instance.instance_finalized,
            BI.INSTANCE_COULD_TRAIN: instance.instance_finalized
            and (
                instance.instance_last_modified
                < instance.instance_samples_last_modified
            ),
        }

        valid = LT_INSTANCE
        if instance.instance_finalized:
            valid = LT_INSTANCE_FINALIZED

        return SUCCESS(
            response, last_modified=instance.instance_last_modified, valid_seconds=valid
        )

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    def post(self, model_uuid, model, me, instance_uuid):
        return ERR_FORB()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_EDIT_INSTANCE, BR.ROLE_SEE_INSTANCE])
    @json_request
    @swag_from("../apidef/instance_collection/put.yml")
    def put(self, model_uuid, model, me, instance_uuid, instance, json_object):
        if instance.instance_finalized:
            return ERR_BADR("instance is finalized")

        modified = False
        if BI.INSTANCE_NAME in json_object:
            if instance.instance_name != json_object[BI.INSTANCE_NAME]:
                instance.instance_name = json_object[BI.INSTANCE_NAME]
                modified = True

        if BI.INSTANCE_DESCRIPTION in json_object:
            if instance.instance_description != json_object[BI.INSTANCE_DESCRIPTION]:
                instance.instance_description = json_object[BI.INSTANCE_DESCRIPTION]
                modified = True

        if BI.INSTANCE_FINALIZED in json_object:
            try:
                _finalized = min(1, max(0, int(json_object[BI.INSTANCE_FINALIZED])))
                if instance.instance_finalized != _finalized:
                    instance.instance_finalized = _finalized
                    modified = True
            except ValueError:
                return ERR_BADR("finalized is illegal")

        if modified:
            instance.instance_last_modified = datetime.utcnow()
            model.model_instances_last_modified = datetime.utcnow()

        db.session.commit()

        return SUCCESS()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE, BR.ROLE_EDIT_INSTANCE])
    @swag_from("../apidef/instance_collection/delete.yml")
    def delete(self, model_uuid, model, me, instance_uuid, instance):
        # delete the instance
        db.session.delete(instance)
        db.session.commit()

        return SUCCESS()


class APIInstanceInferenceData(BaseResource):
    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_GET_INFERENCE_DATA, BR.ROLE_SEE_INSTANCE])
    def head(self, model_uuid, model, instance_uuid, instance, me):
        if instance.inference_data is None or instance.inference_data.file is None:
            return ERR_NOFO()
        else:
            return SUCCESS(
                "",
                last_modified=instance.inference_data.data_last_modified,
                valid_seconds=LT_INFERENCE_DATA,
            )

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_GET_INFERENCE_DATA, BR.ROLE_SEE_INSTANCE])
    @swag_from("../apidef/instance_inference/get.yml")
    def get(self, model_uuid, model, instance_uuid, instance, me):
        if instance.inference_data is None or instance.inference_data.file is None:
            return ERR_NOFO()

        else:
            data = persistence.get_file(instance.inference_data.file)
            data = BytesIO(data)
            data.seek(0)
            return send_file(
                data,
                mimetype="application/octet-stream",
                last_modified=instance.inference_data.data_last_modified,
                cache_timeout=LT_INFERENCE_DATA,
            )

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_EDIT_INSTANCE, BR.ROLE_SEE_INSTANCE])
    def post(self, model_uuid, model, instance_uuid, instance, me):
        if instance.instance_finalized:

            data = request.data
            file_pers = persistence.store_file(data)

            # TODO: prevent existing inferencedata to become orphaned
            newRequest = ORMInstanceInferenceData()
            newRequest.data_file_id = file_pers.file_id
            newRequest.data_uuid = uuid1().bytes
            newRequest.data_last_modified = datetime.utcnow()
            db.session.add(newRequest)
            db.session.commit()

            instance.instance_last_modified = datetime.utcnow()
            model.model_instances_last_modified = datetime.utcnow()

            instance.inference_data_id = newRequest.data_id
            db.session.commit()

        else:
            return ERR_BADR("instance is not finalized")
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


class APIInstanceTrainingData(BaseResource):
    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_GET_INFERENCE_DATA, BR.ROLE_SEE_INSTANCE])
    def head(self, model_uuid, model, instance_uuid, instance, me):
        if instance.training_data is None or instance.training_data.file is None:
            return ERR_NOFO()
        else:
            return SUCCESS(
                "",
                last_modified=instance.training_data.data_last_modified,
                valid_seconds=LT_INFERENCE_DATA,
            )

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_GET_TRAINING_DATA, BR.ROLE_SEE_INSTANCE])
    def get(self, model_uuid, model, instance_uuid, instance, me):
        if instance.training_data is None or instance.training_data.file is None:
            return ERR_NOFO()

        else:
            data = persistence.get_file(instance.training_data.file)
            data = BytesIO(data)
            data.seek(0)
            return send_file(data, mimetype="application/octet-stream")

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_EDIT_INSTANCE, BR.ROLE_SEE_INSTANCE])
    def post(self, model_uuid, model, instance_uuid, instance, me):
        if instance.instance_finalized:

            data = request.data
            file_pers = persistence.store_file(data)
            new_uuid = uuid1()

            # TODO: prevent existing inferencedata to become orphaned
            newRequest = ORMInstanceTrainingData()
            newRequest.data_file_id = file_pers.file_id
            newRequest.data_uuid = new_uuid.bytes
            newRequest.data_last_modified = datetime.utcnow()
            db.session.add(newRequest)
            db.session.commit()

            instance.instance_last_modified = datetime.utcnow()
            model.model_instances_last_modified = datetime.utcnow()

            instance.training_data_id = newRequest.data_id
            db.session.commit()

        else:
            return ERR_BADR("instance is not finalized")
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
