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

from datetime import datetime
from ..orm import db
from .base import (
    BaseResource,
    authenticated,
    model_access,
    instance_access,
)
from .base import sample_access, json_request
from ..orm.sample import ORMSampleTag
from ..common.return_codes import ERR_FORB, SUCCESS
from ..common.string_constants import BODY_ROLE as BR, BODY_TAG as BT
from .lifetime import LT_COLLECTION


class APISampleTag(BaseResource):
    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
    def head(self, model_uuid, model, instance_uuid, instance, sample_uuid, sample, me):
        return SUCCESS(
            "",
            last_modified=instance.instance_samples_last_modified,
            valid_seconds=LT_COLLECTION,
        )

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
    def get(
        self, model_uuid, model, instance_uuid, instance, sample_uuid, sample, me,
    ):
        """
        """
        tags = sample.tags.query.all()

        response = [{BT.TAG_NAME: tag.tag_name} for tag in tags]

        return SUCCESS(
            response,
            last_modified=instance.instance_samples_last_modified,
            valid_seconds=LT_COLLECTION,
        )

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
        """
        """
        changed = False
        # go through all tags in the json_list
        for tag in json_object:

            # get all tags currently registered
            all_tags = {tag.name: tag for tag in ORMSampleTag.query.all()}

            # is the current tag known?
            if tag in all_tags.keys():

                # check that the current tag is not already asigned
                if tag not in sample.tags:
                    sample.tags.append(tag)
                    changed = True
            else:

                # create a new tag and associate it
                new_tag = ORMSampleTag()
                new_tag.tag_name = tag[BT.TAG_NAME]
                db.session.add(new_tag)
                sample.tags.append(new_tag)
                changed = True

            # commit changes made in this run
            db.session.commit()

        if changed:
            instance.instance_samples_last_modified = datetime.utcnow()
            sample.sample_last_modified = datetime.utcnow()
            db.session.commit()

        return SUCCESS()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
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

        return ERR_FORB()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
    def delete(
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
        # drop all tags
        sample.tags = []
        instance.instance_samples_last_modified = datetime.utcnow()
        sample.sample_last_modified = datetime.utcnow()
        db.session.commit()
        return SUCCESS()


class APISampleTagCollection(BaseResource):
    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
    def delete(
        self, model_uuid, model, instance_uuid, instance, sample_uuid, sample, me, tag
    ):
        """
        """
        local_tag = sample.tags.query.filter(tag_name=tag).one_or_none()

        if local_tag is not None:
            sample.tags.remove(local_tag)
            db.session.commit()

        return SUCCESS()

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
        return ERR_FORB()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    @sample_access
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
        return ERR_FORB()

    @authenticated
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
        json_object,
    ):
        return ERR_FORB()
