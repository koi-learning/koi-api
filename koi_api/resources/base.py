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

from flask_restful import Resource, request
from datetime import datetime
import functools
import re
from uuid import UUID
from ..orm.user import ORMToken, ORMUser
from ..orm.model import ORMModel
from ..common.string_constants import (
    HEADER_TOKEN,
    BODY_GENERAL as BG,
    BODY_SAMPLE as BS,
)
from ..common.string_constants import (
    BODY_USER as BU,
    BODY_MODEL as BM,
    BODY_INSTANCE as BI,
)
from ..common.return_codes import ERR_AUTH, SUCCESS, ERR_BADR, ERR_FORB, ERR_NOFO


class BaseResource(Resource):
    MAX_PAGE = 100

    def check_token(self, token_value):
        token = ORMToken.query.filter_by(token_value=token_value).one_or_none()
        if token is None:
            return False, None, False
        else:
            if token.token_invalidated or token.token_valid < datetime.now():
                return False, None, True

            return True, token.user, False

    def authenticate(self):
        token_value = None
        if HEADER_TOKEN in request.headers:
            token_value = request.headers[HEADER_TOKEN]
            token_regex = re.search("[a-fA-F0-9]{32}", token_value)

            if token_regex is None:
                return False, ERR_AUTH("token not recognized"), None

            span = token_regex.span()
            token_value = token_value[span[0]: span[1]]

        else:
            return False, ERR_AUTH("no token send"), None

        authenticated, user, expired = self.check_token(token_value)
        if not authenticated:
            if expired:
                return False, ERR_AUTH("token expired"), user
            return False, ERR_AUTH("not authenticated"), user

        return True, SUCCESS(), user


def paged(func):
    @functools.wraps(func)
    def wrapperP(self, *args, **kwargs):
        page_offset = None
        page_limit = None
        try:
            page_offset = request.args.get(BG.PAGE_OFFSET, 0, int)
            page_limit = request.args.get(BG.PAGE_LIMIT, BaseResource.MAX_PAGE, int)
        except ValueError:
            return ERR_BADR("illegal param")

        if page_limit > BaseResource.MAX_PAGE:
            return ERR_BADR("page_limit exceeds maximum")

        return func(
            self, *args, page_limit=page_limit, page_offset=page_offset, **kwargs
        )

    return wrapperP


def authenticated(func):
    @functools.wraps(func)
    def wrapperA(self, *args, **kwargs):
        auth, ret_val, me = self.authenticate()
        if not auth:
            return ret_val
        return func(self, *args, me=me, **kwargs)

    return wrapperA


def user_access(rights):
    def inner(func):
        @functools.wraps(func)
        def wrapperU(self, *args, me, **kwargs):
            if BU.USER_UUID in kwargs.keys():
                user = ORMUser.query.filter_by(
                    user_uuid=UUID(kwargs[BU.USER_UUID]).bytes
                ).one_or_none()
                if user is None:
                    return ERR_NOFO("user uuid unknown")
                if user.user_id == me.user_id:
                    return func(self, *args, me=me, user=user, **kwargs)
                else:
                    if not me.has_rights(rights):
                        return ERR_FORB()
                    return func(self, *args, me=me, user=user, **kwargs)
            else:
                if not me.has_rights(rights):
                    return ERR_FORB()
                return func(self, *args, me=me, **kwargs)

        return wrapperU

    return inner


def model_access(rights):
    """get the model specified by the model_uuid.
    If the model does not exis return an http response
    check the model and user for access rights specified by the list
    rights

    Args:
        rights ([string]): [list of access rights from common.string_constants]
    """

    def inner(func):
        @functools.wraps(func)
        def wrapperM(self, *args, me, **kwargs):
            if BM.MODEL_UUID not in kwargs:
                return ERR_BADR("missing model_uuid")
            model = ORMModel.query.filter_by(
                model_uuid=UUID(kwargs[BM.MODEL_UUID]).bytes
            ).one_or_none()

            if model is None:
                return ERR_NOFO("model unknown")

            if not me.has_rights_model(model, rights):
                return ERR_FORB()
            return func(self, *args, me=me, model=model, **kwargs)

        return wrapperM

    return inner


def instance_access(rights):
    """get the instance specified by the instance_uuid.
    If the instance does not exis return an http response
    check the instance and user for access rights specified by the list
    rights.
    check if the instance stems from the model

    Args:
        rights ([string]): [list of access rights from common.string_constants]
    """

    def inner(func):
        @functools.wraps(func)
        def wrapperM(self, *args, me, model, **kwargs):
            if BI.INSTANCE_UUID not in kwargs:
                return ERR_BADR("missing instance_uuid")
            instance = model.instances.filter_by(
                instance_uuid=UUID(kwargs[BI.INSTANCE_UUID]).bytes
            ).one_or_none()

            if instance is None:
                return ERR_NOFO("instance unknown")

            if not me.has_rights_instance(instance, rights):
                return ERR_FORB()
            return func(self, *args, me=me, model=model, instance=instance, **kwargs)

        return wrapperM

    return inner


def sample_filter(func):
    @functools.wraps(func)
    def wrapperS(self, *args, **kwargs):
        filter_include = None
        filter_exclude = None
        try:
            filter_include = request.args.getlist(BS.SAMPLE_TAGS_INCLUDE, str)
            filter_exclude = request.args.getlist(BS.SAMPLE_TAGS_EXCLUDE, str)
        except ValueError:
            return ERR_BADR("illegal param")

        return func(
            self,
            *args,
            filter_include=filter_include,
            filter_exclude=filter_exclude,
            **kwargs
        )

    return wrapperS


def label_request_filter(func):
    @functools.wraps(func)
    def wrapperS(self, *args, **kwargs):
        filter_obsolete = None
        try:
            filter_obsolete = request.args.get(BS.SAMPLE_OBSOLETE, None, int)
        except ValueError:
            return ERR_BADR("illegal param")

        return func(self, *args, filter_obsolete=filter_obsolete, **kwargs)

    return wrapperS


def sample_access(func):
    """get the sample specified by the sample uuid
    """

    @functools.wraps(func)
    def wrapperS(self, *args, instance, **kwargs):
        if BS.SAMPLE_UUID not in kwargs:
            return ERR_BADR("missing sample_uuid")
        sample = instance.samples.filter_by(
            sample_uuid=UUID(kwargs[BS.SAMPLE_UUID]).bytes
        ).one_or_none()

        if sample is None:
            return ERR_NOFO("sample is unknown")

        return func(self, *args, instance=instance, sample=sample, **kwargs)

    return wrapperS


def sample_data_access(func):
    """get the sample data specified by the uuid
    """

    @functools.wraps(func)
    def wrapperS(self, *args, sample, **kwargs):
        if BS.SAMPLE_DATA_UUID not in kwargs:
            return ERR_BADR("missing saple_data_uuid")
        data = sample.data.filter_by(
            data_uuid=UUID(kwargs[BS.SAMPLE_DATA_UUID]).bytes
        ).one_or_none()

        if data is None:
            return ERR_NOFO("data is unknown")

        return func(self, *args, sample=sample, data=data, **kwargs)

    return wrapperS


def sample_label_access(func):
    """get the sample label specified by the uuid
    """

    @functools.wraps(func)
    def wrapperS(self, *args, sample, **kwargs):
        if BS.SAMPLE_LABEL_UUID not in kwargs:
            return ERR_BADR("missing saple_uuid")
        label = sample.label.filter_by(
            label_uuid=UUID(kwargs[BS.SAMPLE_LABEL_UUID]).bytes
        ).one_or_none()

        if label is None:
            return ERR_NOFO("label is unknown")

        return func(self, *args, sample=sample, label=label, **kwargs)

    return wrapperS


def descriptor_access(func):
    """get the descriptor specified by the uuid
    """

    @functools.wraps(func)
    def wrapperD(self, *args, instance, **kwargs):
        if BI.INSTANCE_DESCRIPTOR_UUID not in kwargs:
            return ERR_BADR("missing descriptor uuid")
        descriptor = instance.instance_descriptors.filter_by(
            descriptor_uuid=UUID(kwargs[BI.INSTANCE_DESCRIPTOR_UUID]).bytes
        ).one_or_none()

        if descriptor is None:
            return ERR_NOFO("descriptor unknown")
        return func(self, *args, instance=instance, descriptor=descriptor, **kwargs)

    return wrapperD


def json_request(func):
    @functools.wraps(func)
    def wrapperJ(self, *args, **kwargs):
        json_object = request.get_json()

        if json_object is None:
            return ERR_BADR("non-json request")

        return func(self, *args, json_object=json_object, **kwargs)

    return wrapperJ
