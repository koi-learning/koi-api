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
from secrets import token_hex
from ..orm import db
from .base import (
    BaseResource,
    authenticated,
    model_access,
    instance_access,
)
from .base import sample_access, json_request
from ..orm.sample import ORMAssociationTags, ORMSampleTag
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
            last_modified=sample.sample_last_modified,
            valid_seconds=LT_COLLECTION,
            etag=sample.sample_etag,
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
        tags = sample.tags

        response = [{BT.TAG_NAME: tag.tag.tag_name} for tag in tags]

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
            all_tags = {t.tag_name: t for t in instance.tags}

            # is the current tag known?
            if tag[BT.TAG_NAME] in all_tags.keys():
                current_tag = all_tags[tag[BT.TAG_NAME]]

                # check that the current tag is not already asigned
                sample_tags = [t.tag for t in sample.tags]
                if current_tag not in sample_tags:
                    # generate new association between sample and tag
                    new_assoc = ORMAssociationTags()
                    new_assoc.sample_id = sample.sample_id
                    new_assoc.tag_id = current_tag.tag_id

                    # check if this association is to be kept when merging?
                    if sample.sample_finalized:
                        new_assoc.mergeable = False
                    else:
                        new_assoc.mergeable = True

                    db.session.add(new_assoc)
                    changed = True
            else:

                # create a new tag and associate it
                new_tag = ORMSampleTag()
                new_tag.tag_name = tag[BT.TAG_NAME]
                new_tag.instance_id = instance.instance_id
                db.session.add(new_tag)
                db.session.commit()

                # generate new association between sample and tag
                new_assoc = ORMAssociationTags()
                new_assoc.sample_id = sample.sample_id
                new_assoc.tag_id = new_tag.tag_id

                # check if this association is to be kept when merging?
                if sample.sample_finalized:
                    new_assoc.mergeable = False
                else:
                    new_assoc.mergeable = True

                db.session.add(new_assoc)

                changed = True

            # commit changes made in this run
            db.session.commit()

        if changed:
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
    ):
        # drop all tags
        tags = sample.tags
        for tag_assoc in tags:
            db.session.delete(tag_assoc)
        for tag in instance.tags:
            if tag.samples is None:
                db.session.delete(tag)

        instance.instance_samples_last_modified = datetime.utcnow()
        instance.instance_samples_etag = token_hex(16)
        sample.sample_last_modified = datetime.utcnow()
        sample.sample_etag = token_hex(16)
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
        tags = sample.tags

        for t in tags:
            if t.tag.tag_name == tag:
                db.session.delete(t)

        for tag in instance.tags:
            if tag.samples is None:
                db.session.delete(tag)

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
