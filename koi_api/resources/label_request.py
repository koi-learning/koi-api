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
from uuid import uuid4, UUID
from koi_api.resources.base import BaseResource, authenticated, paged
from koi_api.resources.base import instance_access, json_request, model_access, label_request_filter
from koi_api.orm import db
from koi_api.persistence import persistence
from koi_api.orm.sample import ORMSample, ORMSampleLabel
from koi_api.orm.label_request import ORMLabelRequest
from koi_api.common.return_codes import ERR_FORB, ERR_NOFO, SUCCESS, ERR_BADR
from koi_api.common.string_constants import BODY_SAMPLE as BS, BODY_ROLE as BR, BODY_INSTANCE as BI


class APILabelRequest(BaseResource):
    @authenticated
    @paged
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @label_request_filter
    def get(
        self,
        model_uuid,
        model,
        instance_uuid,
        instance,
        me,
        page_offset,
        page_limit,
        filter_obsolete,
    ):
        label_requests = instance.label_requests
        if filter_obsolete is not None:
            label_requests = label_requests.filter_by(
                obsolete=min(1, max(0, filter_obsolete))
            )
        label_requests.offset(page_offset).limit(
            page_limit
        )
        label_requests = label_requests.all()

        response = [
            {
                BS.SAMPLE_LABEL_REQUEST_UUID: UUID(bytes=fr.label_request_uuid).hex,
                BS.SAMPLE_UUID: UUID(bytes=fr.sample.sample_uuid).hex,
                BI.INSTANCE_UUID: UUID(bytes=fr.instance.instance_uuid).hex,
                BS.SAMPLE_OBSOLETE: fr.obsolete,
            }
            for fr in label_requests
        ]

        return SUCCESS(response)

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @json_request
    def post(self, model_uuid, model, instance_uuid, instance, me, json_object):
        new_uuid = uuid4()

        new_request = ORMLabelRequest()
        new_request.label_request_uuid = new_uuid.bytes
        new_request.obsolete = 0
        new_request.label_request_instance = instance

        if BS.SAMPLE_UUID in json_object:
            sample = instance.samples.filter_by(
                sample_uuid=UUID(json_object[BS.SAMPLE_UUID]).bytes
            ).one_or_none()
            if sample is None:
                ERR_NOFO("unknown sample")
            else:
                new_request.label_request_sample = sample
        else:
            return ERR_BADR("missing field: " + BS.SAMPLE_UUID)

        db.session.add(new_request)
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


class APILabelRequestCollection(BaseResource):
    @authenticated
    @paged
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    def get(
        self,
        model_uuid,
        model,
        instance_uuid,
        instance,
        me,
        page_offset,
        page_limit,
        request_uuid,
    ):

        label_request = instance.label_requests.filter_by(
            label_request_uuid=UUID(request_uuid).bytes
        )
        label_request = label_request.one_or_none()

        if label_request is None:
            return ERR_NOFO("unknown label request")

        response = {
            BS.SAMPLE_LABEL_REQUEST_UUID: UUID(bytes=label_request.label_request_uuid).hex,
            BS.SAMPLE_UUID: UUID(bytes=label_request.sample.sample_uuid).hex,
            BI.INSTANCE_UUID: UUID(bytes=label_request.instance.instance_uuid).hex,
            BS.SAMPLE_OBSOLETE: label_request.obsolete,
        }

        return SUCCESS(response)

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE, BR.ROLE_RESPONSE_LABEL])
    def post(self, model_uuid, model, instance_uuid, instance, me, request_uuid):
        label_request = instance.label_requests.filter_by(
            label_request_uuid=UUID(request_uuid).bytes
        )
        label_request = label_request.join(ORMSample).one_or_none()

        if label_request is None:
            return ERR_NOFO("unknown feature request")

        label = request.data
        file_pers = persistence.store_file(label)

        new_uuid = uuid4()

        new_data = ORMSampleLabel()
        new_data.file = file_pers
        new_data.sample = label_request
        new_data.label_uuid = new_uuid.bytes

        db.session.add(new_data)

        label_request.obsolete = 1

        db.session.commit()

        return SUCCESS()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @json_request
    def put(self, model_uuid, model, instance_uuid, instance, me, request_uuid, json_object):
        label_request = instance.label_requests.filter_by(
            label_request_uuid=UUID(request_uuid).bytes
        )
        label_request = label_request.one_or_none()

        if label_request is None:
            return ERR_NOFO("unknown feature request")
        if BS.SAMPLE_OBSOLETE in json_object:
            try:
                label_request.obsolete = min(1, max(0, int(json_object[BS.SAMPLE_OBSOLETE])))
                label_request.sample.consumed = False
            except ValueError:
                return ERR_BADR("malformed field")

        db.session.commit()
        return SUCCESS()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    def delete(self, model_uuid, model, instance_uuid, instance, me, request_uuid):
        label_request = instance.label_requests.filter_by(
            label_request_uuid=UUID(request_uuid).bytes
        ).one_or_none()

        if label_request is None:
            return ERR_NOFO("unknown feature request")

        db.session.delete(label_request)

        return SUCCESS()
