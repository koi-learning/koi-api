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

from koi_api.orm.sample import ORMAssociationTags, ORMSampleTag
from flask.helpers import make_response
from koi_api.orm.parameters import ORMInstanceParameter
from koi_api.orm.model import ORMModel
from flask_restful import request
from flask import send_file
from io import BytesIO
from uuid import uuid4, UUID
from secrets import token_hex
from datetime import datetime
from koi_api.resources.base import (
    BaseResource,
    authenticated,
    paged,
    model_access,
    instance_access,
    descriptor_access,
    json_request,
)
from koi_api.orm import db
from koi_api.persistence import persistence
from koi_api.orm.instance import (
    ORMInstance,
    ORMInstanceInferenceData,
    ORMInstanceTrainingData,
    ORMInstanceDescriptor,
)
from koi_api.orm.access import ORMAccessInstance
from koi_api.orm.role import ORMUserRoleInstance
from koi_api.common.return_codes import ERR_FORB, ERR_NOFO, SUCCESS, ERR_BADR
from koi_api.common.string_constants import BODY_INSTANCE as BI, BODY_ROLE as BR
from koi_api.common.name_generator import gen_name
from koi_api.resources.lifetime import (
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
            response,
            last_modified=datetime.utcnow(),
            valid_seconds=LT_COLLECTION,
            etag=instance.instance_etag,
        )

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @json_request
    def post(self, model, model_uuid, me, instance, instance_uuid, json_object):
        new_uuid = uuid4()
        new_desc = ORMInstanceDescriptor()
        new_desc.instance = instance
        new_desc.descriptor_uuid = new_uuid.bytes

        # check if the request is complete
        if BI.INSTANCE_DESCRIPTOR_KEY in json_object:
            new_desc.descriptor_key = json_object[BI.INSTANCE_DESCRIPTOR_KEY]
        else:
            new_desc.descriptor_key = "unnamed data"

        db.session.add(new_desc)

        # update the timestamp and etag
        instance.instance_last_modified = datetime.utcnow()
        instance.instance_etag = token_hex(16)

        db.session.commit()

        response = {
            BI.INSTANCE_DESCRIPTOR_UUID: new_uuid.hex,
            BI.INSTANCE_DESCRIPTOR_KEY: new_desc.descriptor_key,
            BI.INSTANCE_DESCRIPTOR_KEY_HAS_FILE: new_desc.file is not None,
        }

        return SUCCESS(
            response,
            last_modified=datetime.utcnow(),
            valid_seconds=LT_COLLECTION,
            etag=instance.instance_etag,
        )

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    def put(self, model, model_uuid, me, instance, instance_uuid):
        return ERR_FORB()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    def delete(self, model, model_uuid, me, instance, instance_uuid):
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
            etag=instance.instance_etag,
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
            valid_seconds=LT_INSTANCE_DESCRIPTOR,
            etag=instance.instance_etag,
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
            instance.instance_etag = token_hex(16)

        db.session.commit()

        response = {
            BI.INSTANCE_DESCRIPTOR_UUID: UUID(bytes=descriptor.descriptor_uuid).hex,
            BI.INSTANCE_DESCRIPTOR_KEY: descriptor.descriptor_key,
        }

        return SUCCESS(
            response,
            last_modified=instance.instance_last_modified,
            valid_seconds=LT_COLLECTION,
            etag=instance.instance_etag,
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
            "",
            last_modified=instance.instance_last_modified,
            valid_seconds=LT_INSTANCE_DESCRIPTOR,
            etag=instance.instance_etag,
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

            response = make_response(
                send_file(
                    data_raw,
                    mimetype="application/octet-stream",
                    last_modified=instance.instance_last_modified,
                    max_age=LT_INSTANCE_DESCRIPTOR,
                    etag=False,
                )
            )
            response.set_etag(instance.instance_etag)

            return response

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
        # TODO: delete old descriptor file if already set
        data_raw = request.data
        file_pers = persistence.store_file(data_raw)
        descriptor.file = file_pers
        db.session.add(file_pers)

        instance.instance_last_modified = datetime.utcnow()
        instance.instance_etag = token_hex(16)

        db.session.commit()

        return SUCCESS(
            "",
            last_modified=instance.instance_last_modified,
            valid_seconds=LT_INSTANCE_DESCRIPTOR,
            etag=instance.instance_etag,
        )

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
            etag=model.model_instances_etag,
        )

    @paged
    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
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
                BI.INSTANCE_LAST_MODIFIED: instance.instance_last_modified.isoformat(),
                BI.INSTANCE_SAMPLES_LAST_MODIFIED: instance.instance_samples_last_modified.isoformat(),
                BI.INSTANCE_HAS_REQUESTS: instance.label_requests.filter_by(obsolete=False).count() > 0,
            }
            for instance in instances
        ]

        return SUCCESS(
            response,
            last_modified=model.model_instances_last_modified,
            valid_seconds=LT_COLLECTION,
            etag=model.model_instances_etag,
        )

    @authenticated
    @model_access([BR.ROLE_INSTANTIATE_MODEL, BR.ROLE_SEE_MODEL])
    @json_request
    def post(self, model_uuid, model: ORMModel, me, json_object):
        """Make a new instance for the given model.
        The model has to be finalized in order to build an instance.
        """

        if not model.model_finalized:
            return ERR_BADR("model not finalized")

        new_uuid = uuid4()
        new_inst = ORMInstance()
        new_inst.instance_uuid = new_uuid.bytes
        new_inst.model = model
        new_inst.instance_finalized = False
        new_inst.instance_last_modified = datetime.utcnow()
        new_inst.instance_etag = token_hex(16)
        new_inst.instance_samples_last_modified = datetime.utcnow()
        new_inst.instance_samples_etag = token_hex(16)

        model.model_instances_last_modified = datetime.utcnow()
        model.model_instances_etag = token_hex(16)

        # check if the request is complete
        if BI.INSTANCE_NAME in json_object:
            new_inst.instance_name = json_object[BI.INSTANCE_NAME]
        else:
            new_inst.instance_name = gen_name()

        if BI.INSTANCE_DESCRIPTION in json_object:
            new_inst.instance_description = json_object[BI.INSTANCE_DESCRIPTION]
        else:
            new_inst.instance_description = "created by " + me.user_name

        # add all model params as instance params:
        db.session.add(new_inst)

        for p in model.params:
            instance_parameter = ORMInstanceParameter()
            instance_parameter.param_uuid = uuid4().bytes
            instance_parameter.instance = new_inst
            instance_parameter.model_param = p
            instance_parameter.param_value = None
            db.session.add(instance_parameter)

        owner_role = ORMUserRoleInstance.query.first()

        # construct the access object
        access = ORMAccessInstance()
        access.role = owner_role
        access.user = me
        access.instance = new_inst
        access.access_uuid = uuid4().bytes

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
                BI.INSTANCE_LAST_MODIFIED: new_inst.instance_last_modified.isoformat(),
                BI.INSTANCE_SAMPLES_LAST_MODIFIED: new_inst.instance_samples_last_modified.isoformat(),
                BI.INSTANCE_HAS_REQUESTS: new_inst.label_requests.filter_by(obsolete=False).count() > 0,
            },
            last_modified=new_inst.instance_last_modified,
            valid_seconds=LT_INSTANCE,
            etag=new_inst.instance_etag,
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
            "",
            last_modified=instance.instance_last_modified,
            valid_seconds=valid,
            etag=instance.instance_etag,
        )

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
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
            BI.INSTANCE_LAST_MODIFIED: instance.instance_last_modified.isoformat(),
            BI.INSTANCE_SAMPLES_LAST_MODIFIED: instance.instance_samples_last_modified.isoformat(),
            BI.INSTANCE_HAS_REQUESTS: instance.label_requests.filter_by(obsolete=False).count() > 0,
        }

        valid = LT_INSTANCE
        if instance.instance_finalized:
            valid = LT_INSTANCE_FINALIZED

        return SUCCESS(
            response,
            last_modified=instance.instance_last_modified,
            valid_seconds=valid,
            etag=instance.instance_etag,
        )

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    def post(self, model_uuid, model, me, instance_uuid):
        return ERR_FORB()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_EDIT_INSTANCE, BR.ROLE_SEE_INSTANCE])
    @json_request
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
            instance.instance_etag = token_hex(16)
            model.model_instances_last_modified = datetime.utcnow()
            model.model_instances_etag = token_hex(16)

        db.session.commit()

        return SUCCESS()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE, BR.ROLE_EDIT_INSTANCE])
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
                etag=instance.inference_data.data_etag,
            )

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_GET_INFERENCE_DATA, BR.ROLE_SEE_INSTANCE])
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
                max_age=LT_INFERENCE_DATA,
            )

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_EDIT_INSTANCE, BR.ROLE_SEE_INSTANCE])
    def post(self, model_uuid, model, instance_uuid, instance, me):
        if instance.instance_finalized:

            data = request.data
            file_pers = persistence.store_file(data)

            db.session.add(file_pers)

            # TODO: prevent existing inferencedata to become orphaned
            newRequest = ORMInstanceInferenceData()
            newRequest.file = file_pers
            newRequest.data_uuid = uuid4().bytes
            newRequest.data_last_modified = datetime.utcnow()
            newRequest.data_etag = token_hex(16)

            db.session.add(newRequest)

            instance.instance_last_modified = datetime.utcnow()
            instance.instance_etag = token_hex(16)
            model.model_instances_last_modified = datetime.utcnow()
            model.model_instances_etag = token_hex(16)

            instance.inference_data = newRequest
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
                etag=instance.training_data.data_etag,
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

            db.session.add(file_pers)

            new_uuid = uuid4()

            # TODO: prevent existing inferencedata to become orphaned
            newRequest = ORMInstanceTrainingData()
            newRequest.file = file_pers
            newRequest.data_uuid = new_uuid.bytes
            newRequest.data_last_modified = datetime.utcnow()
            newRequest.data_etag = token_hex(16)
            db.session.add(newRequest)

            instance.instance_last_modified = datetime.utcnow()
            instance.instance_etag = token_hex(16)
            model.model_instances_last_modified = datetime.utcnow()
            model.model_instances_etag = token_hex(16)

            instance.training_data = newRequest
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


class APIInstanceMerge(BaseResource):
    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_EDIT_INSTANCE, BR.ROLE_SEE_INSTANCE])
    @json_request
    def post(self, model_uuid, model, instance_uuid, instance, me, json_object):
        # only finalized instances can be used for merging
        if not instance.instance_finalized:
            return ERR_FORB("instance has to be finalized!")

        # collect all known descriptors
        known_descriptors = dict()

        descriptors = instance.instance_descriptors.all()

        for desc in descriptors:
            key = desc.descriptor_key
            data_raw = persistence.get_file(desc.file)
            if key not in known_descriptors.keys():
                known_descriptors[key] = [
                    data_raw,
                ]
            else:
                known_descriptors[key].append(data_raw)

        new_descriptors = dict()

        # check the instances for merging
        for inst_uuid in json_object[BI.INSTANCE_UUID]:
            inst = ORMInstance.query.filter_by(
                instance_uuid=UUID(inst_uuid).bytes
            ).one_or_none()

            # check if the instance uuid is valid
            if inst is None:
                continue

            # check if the instance is not already merged
            if inst.instance_merged_id is not None:
                continue

            # collect the descriptor of this instance and check if we already have them
            descriptors = inst.instance_descriptors.all()

            for desc in descriptors:
                if desc.file is None:
                    continue

                key = desc.descriptor_key
                data_raw = persistence.get_file(desc.file)

                if key in known_descriptors.keys():
                    if data_raw in known_descriptors[key]:
                        continue

                if key not in new_descriptors.keys():
                    new_descriptors[key] = [
                        data_raw,
                    ]
                else:
                    if data_raw not in new_descriptors[key]:
                        new_descriptors[key].append(data_raw)

            # transfer all samples to the new merged instance
            samples = inst.samples.all()

            for sample in samples:
                # throw away unmergeable labels!
                sample.purge_for_merge()

                # transfer ownership of the sample
                sample.instance = instance

                # generate a new uuid as this is needed in our hirachical layout
                sample.sample_uuid = uuid4().bytes

            # move all tags to the new instance that are not already there
            tags_to_move = inst.tags.all()
            for tag in tags_to_move:
                existing_tags = instance.tags.all()
                matched = False
                for ext_tag in existing_tags:
                    if ext_tag.tag_name == tag.tag_name:
                        matched = True
                        break

                if not matched:
                    new_tag = ORMSampleTag()
                    new_tag.instance = instance
                    new_tag.tag_name = tag.tag_name
                    db.session.add(new_tag)

            # get all associations from the merging instance that are mergeable
            associations = (
                ORMAssociationTags.query.filter_by(mergeable=True)
                .join(ORMAssociationTags.tag)
                .filter_by(instance_id=inst.instance_id)
                .all()
            )

            # get the list of all known tags from the target instance
            existing_tags = instance.tags.all()

            for assoc in associations:
                for ext_tag in existing_tags:
                    if assoc.tag.tag_name == ext_tag.tag_name:
                        assoc.tag = ext_tag
                        break
            db.session.commit()

            # mark the current instance as merged
            inst.instance_merged = instance

        # add the new descriptors to the merged instance
        for key, values in new_descriptors.items():
            for value in values:
                new_desc = ORMInstanceDescriptor()
                new_desc.descriptor_key = key
                new_desc.descriptor_instance = instance
                new_desc.descriptor_uuid = uuid4().bytes

                file_pers = persistence.store_file(value)

                db.session.add(file_pers)

                new_desc.descriptor_file = file_pers
                db.session.add(new_desc)

        db.session.commit()
        return SUCCESS()
