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

from koi_api.resources.base import (
    BaseResource,
    authenticated,
    model_access,
    instance_access,
)
from koi_api.common.return_codes import ERR_FORB, SUCCESS
from koi_api.common.string_constants import BODY_ROLE as BR, BODY_TAG as BT
from koi_api.resources.lifetime import LT_COLLECTION


class APIInstanceTag(BaseResource):
    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    def head(self, model_uuid, model, instance_uuid, instance, sample_uuid, sample, me):
        return SUCCESS(
            "",
            last_modified=instance.instance_samples_last_modified,
            valid_seconds=LT_COLLECTION,
            etag=instance.instance_etag,
        )

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    def get(
        self, model_uuid, model, instance_uuid, instance, me,
    ):
        """
        """
        tags = instance.tags.all()

        response = [{BT.TAG_NAME: tag.tag_name} for tag in tags]

        return SUCCESS(
            response,
            last_modified=instance.instance_samples_last_modified,
            valid_seconds=LT_COLLECTION,
            etag=instance.instance_samples_etag,
        )

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    def put(
        self,
        model_uuid,
        model,
        instance_uuid,
        instance,
        me,
        json_object,
    ):
        """
        """
        return ERR_FORB()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    def post(
        self,
        model_uuid,
        model,
        instance_uuid,
        instance,
        me,
        json_object,
    ):
        return ERR_FORB()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    def delete(
        self,
        model_uuid,
        model,
        instance_uuid,
        instance,
        me,
        json_object,
    ):
        return ERR_FORB()
