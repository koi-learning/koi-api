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

from secrets import token_hex
from flask_restful import request
from flask import send_file
from io import BytesIO
from datetime import datetime
from ..orm import db
from .base import (
    BaseResource,
    authenticated,
    model_access,
    instance_access,
    sample_label_access,
)
from .base import paged, sample_access, sample_data_access, json_request, sample_filter
from uuid import UUID, uuid1
from ..orm.sample import ORMSample, ORMSampleData, ORMSampleLabel, ORMSampleTag
from ..persistence import persistence
from ..common.return_codes import ERR_FORB, ERR_NOFO, ERR_BADR, SUCCESS
from ..common.string_constants import BODY_SAMPLE as BS, BODY_ROLE as BR
from .lifetime import LT_COLLECTION, LT_SAMPLE, LT_SAMPLE_FINALIZED


class APISample(BaseResource):
    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    def head(
        self, model_uuid, model, instance_uuid, instance, me,
    ):
        return SUCCESS(
            "",
            last_modified=instance.instance_samples_last_modified,
            valid_seconds=LT_COLLECTION,
            etag=instance.instance_samples_etag,
        )

    @authenticated
    @paged
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_filter
    def get(
        self,
        model_uuid,
        model,
        instance_uuid,
        instance,
        me,
        page_offset,
        page_limit,
        filter_include,
        filter_exclude,
    ):
        """Get all samples assigned to this instance

        Args:
            model_uuid ([string]): The models uuid from the url
            model ([ORMModel]): The model object designated by the model_uuid
            instance_uuid ([string]): the instances uuid from the url
            instance ([ORMInstance]): the instance object designated by the instance uuid
            me ([ORMUser]): The authenticated user calling this function
            page_offset ([int]): offset for the set of results
            page_limit ([int]): limit for the set of results

        Returns:
            [list of object with uuid field]: list of all samples assigned to this instance
        """
        samples = instance.samples

        if len(filter_include) > 0:
            # filter includes
            samples = samples.filter(
                ORMSample.tags.any(ORMSampleTag.tag_name.in_(filter_include))
            )

        # filter excludes
        samples = samples.filter(
            ~ORMSample.tags.any(ORMSampleTag.tag_name.in_(filter_exclude))
        )

        # paging
        samples = samples.offset(page_offset).limit(page_limit).all()

        response = [
            {
                BS.SAMPLE_UUID: UUID(bytes=sample.sample_uuid).hex,
                BS.SAMPLE_FINALIZED: sample.sample_finalized,
            }
            for sample in samples
        ]

        return SUCCESS(
            response,
            last_modified=instance.instance_samples_last_modified,
            valid_seconds=LT_COLLECTION,
            etag=instance.instance_samples_etag,
        )

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE, BR.ROLE_ADD_SAMPLE])
    @json_request
    def post(self, model_uuid, model, instance_uuid, instance, me, json_object):
        """Add a new sample and assign it to this instance

        Args:
            model_uuid ([string]): The models uuid from the url
            model ([ORMModel]): The model object designated by the model_uuid
            instance_uuid ([string]): the instances uuid from the url
            instance ([ORMInstance]): the instance object designated by the instance uuid
            me ([ORMUser]): The authenticated user calling this function
            page_offset ([int]): offset for the set of results
            page_limit ([int]): limit for the set of results

        Returns:
            [string]: uuid of new sample
        """
        new_sample = ORMSample()
        new_sample.instance_id = instance.instance_id
        new_sample.sample_finalized = 0
        new_sample.sample_uuid = uuid1().bytes

        new_sample.sample_last_modified = datetime.utcnow()
        new_sample.sample_etag = token_hex(16)

        instance.instance_samples_last_modified = datetime.utcnow()
        instance.instance_samples_etag = token_hex(16)

        db.session.add(new_sample)
        db.session.commit()
        return SUCCESS(
            {
                BS.SAMPLE_UUID: UUID(bytes=new_sample.sample_uuid).hex,
                BS.SAMPLE_FINALIZED: new_sample.sample_finalized,
            },
            last_modified=new_sample.sample_last_modified,
            valid_seconds=LT_SAMPLE,
            etag=new_sample.sample_etag,
        )

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    def put(self, model_uuid, model, instance_uuid, instance, me):
        """Forbidden action"""
        return ERR_FORB()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    def delete(self, model_uuid, model, instance_uuid, instance, me):
        """Forbidden action"""
        return ERR_FORB()


class APISampleCollection(BaseResource):
    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
    def head(self, model_uuid, model, instance_uuid, instance, sample_uuid, sample, me):
        valid = LT_SAMPLE
        if sample.sample_finalized:
            valid = LT_SAMPLE_FINALIZED
        return SUCCESS(
            "",
            last_modified=sample.sample_last_modified,
            valid_seconds=valid,
            etag=sample.sample_etag,
        )

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
    def get(self, model_uuid, model, instance_uuid, instance, sample_uuid, sample, me):
        response = {
            BS.SAMPLE_UUID: UUID(bytes=sample.sample_uuid).hex,
            BS.SAMPLE_FINALIZED: sample.sample_finalized,
        }

        valid = LT_SAMPLE
        if sample.sample_finalized:
            valid = LT_SAMPLE_FINALIZED

        return SUCCESS(
            response,
            last_modified=sample.sample_last_modified,
            valid_seconds=valid,
            etag=sample.sample_etag,
        )

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
    def post(self, model_uuid, model, instance_uuid, instance, sample_uuid, sample, me):
        """Forbidden action"""
        return ERR_FORB()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
    @json_request
    def put(
        self,
        model_uuid,
        model,
        instance_uuid,
        instance,
        sample_uuid,
        sample,
        me,
        json_object,
    ):
        modified = False

        if BS.SAMPLE_FINALIZED in json_object:
            try:
                _finalized = min(1, max(0, int(json_object[BS.SAMPLE_FINALIZED])))
                if sample.sample_finalized != _finalized:
                    sample.sample_finalized = _finalized
                    modified = True

            except ValueError:
                return ERR_BADR("illegal param: " + BS.SAMPLE_FINALIZED)

        if modified:
            instance.instance_samples_last_modified = datetime.utcnow()
            instance.instance_samples_etag = token_hex(16)
            sample.sample_last_modified = datetime.utcnow()
            sample.sample_etag = token_hex(16)

        db.session.commit()

        return SUCCESS()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
    def delete(
        self, model_uuid, model, instance_uuid, instance, sample_uuid, sample, me
    ):
        """Delete the requested sample.

        Args:
            model_uuid (string): model uuid from the url
            model (ORMModel): model object
            instance_uuid (string): instance uuid from the url
            instance (ORMInstance): instance object
            sample_uuid (string): sample uuid from the url
            sample (ORMSample): sample object
            me (ORMUser): authenticated user calling this function

        Returns:
            http-status: success
        """
        instance.instance_samples_last_modified = datetime.utcnow()
        instance.instance_etag = token_hex(16)
        db.session.delete(sample)
        db.session.commit()
        return SUCCESS()


class APISampleData(BaseResource):
    @authenticated
    @paged
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
    def head(
        self,
        model_uuid,
        model,
        instance_uuid,
        instance,
        sample_uuid,
        sample,
        me,
        page_limit,
        page_offset,
    ):
        return SUCCESS(
            "",
            last_modified=sample.sample_last_modified,
            valid_seconds=LT_COLLECTION,
            etag=sample.sample_etag,
        )

    @authenticated
    @paged
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
    def get(
        self,
        model_uuid,
        model,
        instance_uuid,
        instance,
        sample_uuid,
        sample,
        me,
        page_limit,
        page_offset,
    ):

        data = sample.data.offset(page_offset).limit(page_limit).all()

        response = [
            {
                BS.SAMPLE_DATA_UUID: UUID(bytes=d.data_uuid).hex,
                BS.SAMPLE_HAS_FILE: d.file is not None,
                BS.SAMPLE_KEY: d.data_key,
            }
            for d in data
        ]
        return SUCCESS(
            response,
            last_modified=sample.sample_last_modified,
            valid_seconds=LT_COLLECTION,
            etag=sample.sample_etag,
        )

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
    @json_request
    def post(
        self,
        model_uuid,
        model,
        instance_uuid,
        instance,
        sample_uuid,
        sample,
        me,
        json_object,
    ):
        if sample.sample_finalized:
            return ERR_BADR("sample is finalized")

        new_uuid = uuid1()

        new_data = ORMSampleData()
        new_data.file_id = None
        new_data.sample_id = sample.sample_id
        new_data.data_uuid = new_uuid.bytes

        if BS.SAMPLE_KEY in json_object:
            new_data.data_key = json_object[BS.SAMPLE_KEY]
        else:
            new_data.data_key = "unnamed data"

        sample.sample_last_modified = datetime.utcnow()
        sample.sample_etag = token_hex(16)
        new_data.data_last_modified = datetime.utcnow()
        new_data.date_etag = token_hex(16)
        instance.instance_samples_last_modified = datetime.utcnow()
        instance.instance_samples_etag = token_hex(16)

        db.session.add(new_data)
        db.session.commit()

        return SUCCESS(
            {
                BS.SAMPLE_DATA_UUID: new_uuid.hex,
                BS.SAMPLE_KEY: new_data.data_key,
                BS.SAMPLE_HAS_FILE: new_data.file is not None,
            }
        )

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
    def put(self, model_uuid, model, instance_uuid, instance, sample_uuid, sample, me):
        """Forbidden action"""
        return ERR_FORB()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
    def delete(
        self, model_uuid, model, instance_uuid, instance, sample_uuid, sample, me
    ):
        """Forbidden action"""
        return ERR_FORB()


class APISampleDataCollection(BaseResource):
    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
    @sample_data_access
    def head(
        self,
        model_uuid,
        model,
        instance_uuid,
        instance,
        sample_uuid,
        sample,
        data_uuid,
        data,
        me,
    ):
        valid = LT_SAMPLE
        if sample.sample_finalized:
            valid = LT_SAMPLE_FINALIZED
        return SUCCESS(
            "",
            last_modified=data.data_last_modified,
            valid_seconds=valid,
            etag=data.data_etag,
        )

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
    @sample_data_access
    def get(
        self,
        model_uuid,
        model,
        instance_uuid,
        instance,
        sample_uuid,
        sample,
        data_uuid,
        data,
        me,
    ):
        response = {
            BS.SAMPLE_DATA_UUID: UUID(bytes=data.data_uuid).hex,
            BS.SAMPLE_HAS_FILE: data.file is not None,
            BS.SAMPLE_KEY: data.data_key,
        }
        valid = LT_SAMPLE
        if sample.sample_finalized:
            valid = LT_SAMPLE_FINALIZED
        return SUCCESS(
            response,
            last_modified=data.data_last_modified,
            valid_seconds=valid,
            etag=data.data_etag,
        )

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
    @sample_data_access
    def post(
        self,
        model_uuid,
        model,
        instance_uuid,
        instance,
        sample_uuid,
        sample,
        data_uuid,
        data,
        me,
    ):
        return ERR_FORB()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
    @sample_data_access
    @json_request
    def put(
        self,
        model_uuid,
        model,
        instance_uuid,
        instance,
        sample_uuid,
        sample,
        data_uuid,
        data,
        me,
        json_object,
    ):
        if BS.SAMPLE_KEY in json_object:
            if data.data_key != json_object[BS.SAMPLE_KEY]:
                data.data_key = json_object[BS.SAMPLE_KEY]
                sample.sample_last_modified = datetime.utcnow()
                sample.sample_etag = token_hex(16)
                data.data_last_modified = datetime.utcnow()
                data.data_etag = token_hex(16)
                instance.instance_samples_last_modified = datetime.utcnow()
                instance.instance_samples_etag = token_hex(16)

        db.session.commit()
        return SUCCESS()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
    @sample_data_access
    def delete(
        self,
        model_uuid,
        model,
        instance_uuid,
        instance,
        sample_uuid,
        sample,
        data_uuid,
        data,
        me,
    ):
        if sample.sample_finalized:
            return ERR_BADR("sample is finalized")

        sample.sample_last_modified = datetime.utcnow()
        sample.sample_etag = token_hex(16)
        instance.instance_samples_last_modified = datetime.utcnow()
        instance.instance_samples_etag = token_hex(16)

        db.session.delete(data)
        db.session.commit()
        return SUCCESS()


class APISampleLabel(BaseResource):
    @authenticated
    @paged
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
    def head(
        self,
        model_uuid,
        model,
        instance_uuid,
        instance,
        sample_uuid,
        sample,
        me,
        page_limit,
        page_offset,
    ):
        valid = LT_SAMPLE
        if sample.sample_finalized:
            valid = LT_SAMPLE_FINALIZED
        return SUCCESS(
            "",
            last_modified=sample.sample_last_modified,
            valid_seconds=valid,
            etag=sample.sample_etag,
        )

    @authenticated
    @paged
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
    def get(
        self,
        model_uuid,
        model,
        instance_uuid,
        instance,
        sample_uuid,
        sample,
        me,
        page_limit,
        page_offset,
    ):

        data = sample.label.offset(page_offset).limit(page_limit).all()
        response = [
            {
                BS.SAMPLE_LABEL_UUID: UUID(bytes=d.label_uuid).hex,
                BS.SAMPLE_HAS_FILE: d.file is not None,
                BS.SAMPLE_KEY: d.label_key,
            }
            for d in data
        ]
        valid = LT_SAMPLE
        if sample.sample_finalized:
            valid = LT_SAMPLE_FINALIZED
        return SUCCESS(
            response,
            last_modified=sample.sample_last_modified,
            valid_seconds=valid,
            etag=sample.sample_etag,
        )

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
    @json_request
    def post(
        self,
        model_uuid,
        model,
        instance_uuid,
        instance,
        sample_uuid,
        sample,
        me,
        json_object,
    ):

        new_uuid = uuid1()

        new_label = ORMSampleLabel()
        new_label.file_id = None
        new_label.sample_id = sample.sample_id
        new_label.label_uuid = new_uuid.bytes

        if BS.SAMPLE_KEY in json_object:
            new_label.label_key = json_object[BS.SAMPLE_KEY]
        else:
            new_label.label_key = "unnamed label"

        sample.sample_last_modified = datetime.utcnow()
        sample.sample_etag = token_hex()
        new_label.label_last_modified = datetime.utcnow()
        new_label.label_etag = token_hex(16)
        instance.instance_samples_last_modified = datetime.utcnow()
        instance.instance_samples_etag = token_hex(16)
        db.session.add(new_label)
        db.session.commit()

        return SUCCESS(
            {
                BS.SAMPLE_LABEL_UUID: new_uuid.hex,
                BS.SAMPLE_KEY: new_label.label_key,
                BS.SAMPLE_HAS_FILE: new_label.file is not None,
            }
        )

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
    def put(self, model_uuid, model, instance_uuid, instance, sample_uuid, sample, me):
        """Forbidden action"""
        return ERR_FORB()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
    def delete(
        self, model_uuid, model, instance_uuid, instance, sample_uuid, sample, me
    ):
        """Forbidden action"""
        return ERR_FORB()


class APISampleLabelCollection(BaseResource):
    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
    @sample_label_access
    def head(
        self,
        model_uuid,
        model,
        instance_uuid,
        instance,
        sample_uuid,
        sample,
        me,
        label_uuid,
        label,
    ):
        valid = LT_SAMPLE
        if sample.sample_finalized:
            valid = LT_SAMPLE_FINALIZED
        return SUCCESS(
            "",
            last_modified=label.label_last_modified,
            valid_seconds=valid,
            etag=label.label_etag,
        )

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
    @sample_label_access
    def get(
        self,
        model_uuid,
        model,
        instance_uuid,
        instance,
        sample_uuid,
        sample,
        me,
        label_uuid,
        label,
    ):
        response = {
            BS.SAMPLE_LABEL_UUID: UUID(bytes=label.label_uuid).hex,
            BS.SAMPLE_HAS_FILE: label.file is not None,
            BS.SAMPLE_KEY: label.label_key,
        }
        valid = LT_SAMPLE
        if sample.sample_finalized:
            valid = LT_SAMPLE_FINALIZED
        return SUCCESS(
            response,
            last_modified=label.label_last_modified,
            valid_seconds=valid,
            etag=label.label_etag,
        )

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
    @sample_label_access
    def post(
        self,
        model_uuid,
        model,
        instance_uuid,
        instance,
        sample_uuid,
        sample,
        me,
        label_uuid,
        label,
    ):
        return ERR_FORB()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
    @sample_label_access
    @json_request
    def put(
        self,
        model_uuid,
        model,
        instance_uuid,
        instance,
        sample_uuid,
        sample,
        me,
        label_uuid,
        label,
        json_object,
    ):
        if BS.SAMPLE_KEY in json_object:
            if label.label_key != json_object[BS.SAMPLE_KEY]:
                label.label_key = json_object[BS.SAMPLE_KEY]
                instance.instance_samples_last_modified = datetime.utcnow()
                instance.instance_samples_etag = token_hex(16)
                sample.sample_last_modified = datetime.utcnow()
                sample.sample_etag = token_hex(16)
                label.label_last_modified = datetime.utcnow()
                label.label_etag = token_hex(16)

        db.session.commit()
        return SUCCESS()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
    @sample_label_access
    def delete(
        self,
        model_uuid,
        model,
        instance_uuid,
        instance,
        sample_uuid,
        sample,
        me,
        label_uuid,
        label,
    ):
        db.session.delete(label)
        sample.sample_last_modified = datetime.utcnow()
        sample.sample_etag = token_hex(16)
        instance.instance_samples_last_modified = datetime.utcnow()
        instance.instance_samples_etag = token_hex(16)
        db.session.commit()
        return SUCCESS()


class APISampleDataFile(BaseResource):
    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
    @sample_data_access
    def head(
        self,
        model_uuid,
        model,
        instance_uuid,
        instance,
        sample_uuid,
        sample,
        data_uuid,
        data,
        me,
    ):
        valid = LT_SAMPLE
        if sample.sample_finalized:
            valid = LT_SAMPLE_FINALIZED
        return SUCCESS(
            "",
            last_modified=data.data_last_modified,
            valid_seconds=valid,
            etag=data.data_etag,
        )

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
    @sample_data_access
    def get(
        self,
        model_uuid,
        model,
        instance_uuid,
        instance,
        sample_uuid,
        sample,
        data_uuid,
        data,
        me,
    ):
        if data.file is None:
            return ERR_NOFO("no data specified")
        else:
            data_raw = persistence.get_file(data.file)
            data_raw = BytesIO(data_raw)
            data_raw.seek(0)
            valid = LT_SAMPLE
            if sample.sample_finalized:
                valid = LT_SAMPLE_FINALIZED
            return send_file(
                data_raw,
                mimetype="application/octet-stream",
                last_modified=data.data_last_modified,
                cache_timeout=valid,
            )

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
    @sample_data_access
    def post(
        self,
        model_uuid,
        model,
        instance_uuid,
        instance,
        sample_uuid,
        sample,
        data_uuid,
        data,
        me,
    ):
        if sample.sample_finalized:
            return ERR_BADR("sample is finalized")

        data_raw = request.data
        file_pers = persistence.store_file(data_raw)

        sample.sample_last_modified = datetime.utcnow()
        sample.sample_etag = token_hex(16)
        data.data_last_modified = datetime.utcnow()
        data.data_etag = token_hex(16)
        instance.instance_samples_last_modified = datetime.utcnow()
        instance.instance_samples_etag = token_hex(16)

        data.file_id = file_pers.file_id
        db.session.add(file_pers)
        db.session.commit()

        return SUCCESS()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
    @sample_data_access
    def put(
        self,
        model_uuid,
        model,
        instance_uuid,
        instance,
        sample_uuid,
        sample,
        data_uuid,
        data,
        me,
    ):
        return ERR_FORB()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
    @sample_data_access
    def delete(
        self,
        model_uuid,
        model,
        instance_uuid,
        instance,
        sample_uuid,
        sample,
        data_uuid,
        data,
        me,
    ):
        return ERR_FORB()


class APISampleLabelFile(BaseResource):
    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
    @sample_label_access
    def head(
        self,
        model_uuid,
        model,
        instance_uuid,
        instance,
        sample_uuid,
        sample,
        label_uuid,
        label,
        me,
    ):
        return SUCCESS(
            "",
            last_modified=label.label_last_modified,
            valid_seconds=LT_SAMPLE,
            etag=label.label_etag,
        )

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
    @sample_label_access
    def get(
        self,
        model_uuid,
        model,
        instance_uuid,
        instance,
        sample_uuid,
        sample,
        label_uuid,
        label,
        me,
    ):
        if label.file is None:
            return ERR_NOFO("no data specified")
        else:
            data_raw = persistence.get_file(label.file)
            data_raw = BytesIO(data_raw)
            data_raw.seek(0)
            return send_file(
                data_raw,
                mimetype="application/octet-stream",
                last_modified=label.label_last_modified,
                cache_timeout=LT_SAMPLE,
            )

        return SUCCESS()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
    @sample_label_access
    def post(
        self,
        model_uuid,
        model,
        instance_uuid,
        instance,
        sample_uuid,
        sample,
        label_uuid,
        label,
        me,
    ):
        data_raw = request.data
        file_pers = persistence.store_file(data_raw)

        label.file_id = file_pers.file_id

        sample.sample_last_modified = datetime.utcnow()
        sample.sample_etag = token_hex(16)
        label.label_last_modified = datetime.utcnow()
        label.label_etag = token_hex(16)
        instance.instance_samples_last_modified = datetime.utcnow()
        instance.instance_samples_etag = token_hex(16)

        db.session.add(file_pers)
        db.session.commit()

        return SUCCESS()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
    @sample_label_access
    def put(
        self,
        model_uuid,
        model,
        instance_uuid,
        instance,
        sample_uuid,
        sample,
        label_uuid,
        label,
        me,
    ):
        return ERR_FORB()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
    @sample_label_access
    def delete(
        self,
        model_uuid,
        model,
        instance_uuid,
        instance,
        sample_uuid,
        sample,
        label_uuid,
        label,
        me,
    ):
        return ERR_FORB()
