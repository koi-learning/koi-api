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
from uuid import uuid1, UUID
from zipfile import ZipFile, BadZipFile
from re import compile
from datetime import datetime
from ..orm import db
from ..persistence import persistence
from ..orm.parameters import ORMModelParameter
from ..orm.model import (
    ORMModel,
    ORMModelCode,
    ORMModelVisualPlugin,
    ORMModelLabelRequestPlugin,
)
from .base import (
    BaseResource,
    authenticated,
    paged,
    user_access,
    model_access,
    json_request,
)
from ..orm.access import ORMAccessModel
from ..orm.role import ORMUserRoleModel
from ..common.return_codes import ERR_FORB, SUCCESS, ERR_NOFO, ERR_BADR
from ..common.string_constants import BODY_MODEL as BM
from ..common.string_constants import BODY_ROLE as BR
from ..common.name_generator import gen_name
from .lifetime import LT_MODEL, LT_MODEL_FINALIZED, LT_COLLECTION


class APIModel(BaseResource):
    @authenticated
    def head(self, me):
        return SUCCESS("", last_modified=datetime.utcnow())

    @paged
    @authenticated
    def get(self, me, page_offset, page_limit):

        # get the models
        query = ORMModel.query.join(ORMModel.granted_users).filter_by(
            user_id=me.user_id
        )
        query = (
            query.join(ORMAccessModel.role)
            .filter_by(can_see=1)
            .offset(page_offset)
            .limit(page_limit)
        )
        models = query.all()

        # construct the response
        response = [
            {
                BM.MODEL_UUID: UUID(bytes=model.model_uuid).hex,
                BM.MODEL_NAME: model.model_name,
                BM.MODEL_DESCRIPTION: model.model_description,
                BM.MODEL_HAS_CODE: model.code is not None,
                BM.MODEL_HAS_PLUGIN_VISUAL: model.visual_plugin is not None,
                BM.MODEL_HAS_PLUGIN_LABEL: model.request_plugin is not None,
                BM.MODEL_FINALIZED: model.model_finalized,
            }
            for model in models
        ]

        return SUCCESS(
            response, last_modified=datetime.utcnow(), valid_seconds=LT_COLLECTION
        )

    @authenticated
    @user_access([BR.ROLE_EDIT_MODELS])
    @json_request
    def post(self, me, json_object):

        # construct a new model from the fields in the request
        new_model = ORMModel()
        new_model.model_uuid = uuid1().bytes
        new_model.model_finalized = False
        new_model.model_last_modified = datetime.utcnow()
        new_model.model_etag = token_hex(16)
        new_model.model_instances_last_modified = datetime.utcnow()
        new_model.model_instances_etag = token_hex(16)

        if BM.MODEL_NAME in json_object:
            new_model.model_name = json_object[BM.MODEL_NAME]
        else:
            new_model.model_name = gen_name()

        if BM.MODEL_DESCRIPTION in json_object:
            new_model.model_description = json_object[BM.MODEL_DESCRIPTION]
        else:
            new_model.model_description = "generated by " + me.user_name

        # add the new model to the database
        db.session.add(new_model)
        db.session.commit()

        # create the access object for the owner of this model
        owner_role = ORMUserRoleModel.query.first()

        new_access = ORMAccessModel()
        new_access.model_id = new_model.model_id
        new_access.user_id = me.user_id
        new_access.role_id = owner_role.role_id
        new_access.access_uuid = uuid1().bytes

        # add the new access object
        db.session.add(new_access)
        db.session.commit()

        # return the new models id
        response = {
            BM.MODEL_UUID: UUID(bytes=new_model.model_uuid).hex,
            BM.MODEL_NAME: new_model.model_name,
            BM.MODEL_DESCRIPTION: new_model.model_description,
            BM.MODEL_HAS_CODE: False,
            BM.MODEL_HAS_PLUGIN_LABEL: False,
            BM.MODEL_HAS_PLUGIN_VISUAL: False,
        }

        return SUCCESS(
            response,
            last_modified=new_model.model_last_modified,
            valid_seconds=LT_MODEL,
            etag=new_model.model_etag,
        )

    @authenticated
    def put(self, me):
        return ERR_FORB()

    @authenticated
    def delete(self, me):
        return ERR_FORB()


class APIModelCollection(BaseResource):
    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    def head(self, model, model_uuid, me):
        valid = LT_MODEL
        if model.model_finalized:
            valid = LT_MODEL_FINALIZED
        return SUCCESS(
            "",
            last_modified=model.model_last_modified,
            valid_seconds=valid,
            etag=model.model_etag,
        )

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    def get(self, model, me, model_uuid):

        # construct the response
        response = {
            BM.MODEL_UUID: UUID(bytes=model.model_uuid).hex,
            BM.MODEL_NAME: model.model_name,
            BM.MODEL_DESCRIPTION: model.model_description,
            BM.MODEL_HAS_CODE: model.code is not None,
            BM.MODEL_HAS_PLUGIN_VISUAL: model.visual_plugin is not None,
            BM.MODEL_HAS_PLUGIN_LABEL: model.request_plugin is not None,
            BM.MODEL_FINALIZED: model.model_finalized,
        }

        valid = LT_MODEL
        if model.model_finalized:
            valid = LT_MODEL_FINALIZED

        return SUCCESS(
            response,
            last_modified=model.model_last_modified,
            valid_seconds=valid,
            etag=model.model_etag,
        )

    @authenticated
    def post(self, me, model_uuid):
        return ERR_FORB()

    @authenticated
    @model_access([BR.ROLE_EDIT_MODEL])
    @json_request
    def put(self, model, model_uuid, me, json_object):
        modified = False
        if not model.model_finalized:
            # update this models fields according to the reqest
            if BM.MODEL_NAME in json_object:
                if model.model_name != json_object[BM.MODEL_NAME]:
                    model.model_name = json_object[BM.MODEL_NAME]
                    modified = True

            if BM.MODEL_DESCRIPTION in json_object:
                if model.model_description != json_object[BM.MODEL_DESCRIPTION]:
                    model.model_description = json_object[BM.MODEL_DESCRIPTION]
                    modified = True

            if BM.MODEL_FINALIZED in json_object:
                has_code = model.code is not None
                try:
                    _finalized = min(1, max(0, int(json_object[BM.MODEL_FINALIZED])))
                except ValueError:
                    return ERR_BADR("illegal field: finalized")

                if _finalized:
                    if has_code:
                        if model.model_finalized != _finalized:
                            model.model_finalized = _finalized
                            modified = True
                    else:
                        return ERR_BADR("cannot finalize without code")

            if modified:
                model.model_last_modified = datetime.utcnow()
                model.model_etag = token_hex(16)

        else:
            return ERR_BADR("model is finalized")

        db.session.commit()

        return SUCCESS()

    @authenticated
    @model_access([BR.ROLE_EDIT_MODEL])
    def delete(self, model, me, model_uuid):
        db.session.delete(model)
        db.session.commit()

        return SUCCESS()


class APIModelCode(BaseResource):
    @authenticated
    @model_access([BR.ROLE_EDIT_MODEL])
    def head(self, model_uuid, model, me):
        valid = LT_MODEL
        if model.model_finalized:
            valid = LT_MODEL_FINALIZED
        return SUCCESS(
            "",
            last_modified=model.model_last_modified,
            valid_seconds=valid,
            etag=model.model_etag,
        )

    @authenticated
    @model_access([BR.ROLE_EDIT_MODEL])
    def get(self, model_uuid, model, me):
        if model.code is None or model.code.file is None:
            return ERR_NOFO("no code specified")
        else:
            data = persistence.get_file(model.code.file)
            data = BytesIO(data)
            data.seek(0)

            valid = LT_MODEL
            if model.model_finalized:
                valid = LT_MODEL_FINALIZED

            return send_file(
                data,
                mimetype="application/octet-stream",
                last_modified=model.model_last_modified,
                cache_timeout=valid,
            )

    @authenticated
    @model_access([BR.ROLE_EDIT_MODEL])
    def post(self, model_uuid, model, me):
        if not model.model_finalized:
            data = request.data
            file_pers = persistence.store_file(data)

            model.params = []

            ziph = None
            try:
                ziph = ZipFile(BytesIO(data), "r")
            except BadZipFile:
                return ERR_BADR("invalid zip-file")
            lines = list()

            if "__param__.py" in ziph.namelist():
                params_file = ziph.open("__param__.py")
                lines = params_file.readlines()

            pattern = compile(
                r"""\s*(?P<param>.*)\s*:\s*(?P<type>str|int|float)\s*(#\s*(\[(?P<constraint>.*)\])?\s*(?P<comment>.*))?\s*"""
            )

            for line in lines:
                utf8 = line.decode("utf8")
                match = pattern.match(utf8)
                if match is not None:

                    new_param = ORMModelParameter()
                    new_param.param_uuid = uuid1().bytes
                    new_param.model_id = model.model_id
                    new_param.param_name = match.group("param")
                    new_param.param_type = match.group("type")
                    if match.group("comment") is not None:
                        new_param.param_description = match.group("comment")
                    else:
                        new_param.param_description = ""

                    if match.group("constraint") is not None:
                        new_param.param_constraint = match.group("constraint")
                    else:
                        new_param.param_constraint = ""
                    db.session.add(new_param)

            # TODO: prevent existing code to become orphaned
            newCode = ORMModelCode()
            newCode.file_id = file_pers.file_id

            db.session.add(newCode)
            db.session.commit()

            model.model_last_modified = datetime.utcnow()
            model.model_etag = token_hex(16)

            model.code_id = newCode.code_id
            db.session.commit()

        else:
            return ERR_BADR("model is finalized")
        return SUCCESS()

    @authenticated
    def put(self, model_uuid, me):
        return ERR_FORB()

    @authenticated
    def delete(self, model_uuid, me):
        return ERR_FORB()


class APIModelVisualPlugin(BaseResource):
    @authenticated
    @model_access([BR.ROLE_EDIT_MODEL])
    def get(self, model_uuid, model, me):
        if model.visual_plugin is None or model.visual_plugin.file is None:
            return ERR_NOFO("no visual plugin specified")
        else:
            data = persistence.get_file(model.visual_plugin.file)
            data = BytesIO(data)
            data.seek(0)

            valid = LT_MODEL
            if model.model_finalized:
                valid = LT_MODEL_FINALIZED
            return send_file(
                data, mimetype="application/octet-stream", cache_timeout=valid
            )

    @authenticated
    @model_access([BR.ROLE_EDIT_MODEL])
    def post(self, model_uuid, model, me):
        data = request.data
        file_pers = persistence.store_file(data)

        # TODO: prevent existing plugin to become orphaned
        newVisual = ORMModelVisualPlugin()
        newVisual.file_id = file_pers.file_id
        db.session.add(newVisual)
        db.session.commit()

        model.visual_plugin_id = newVisual.plugin_id
        model.model_last_modified = datetime.utcnow()
        model.model_etag = token_hex(16)
        db.session.commit()
        return SUCCESS()

    @authenticated
    def put(self, model_uuid, me):
        return ERR_FORB()

    @authenticated
    def delete(self, model_uuid, me):
        return ERR_FORB()


class APIModelRequestPlugin(BaseResource):
    @authenticated
    @model_access([BR.ROLE_EDIT_MODEL])
    def get(self, model_uuid, model, me):
        if model.request_plugin is None or model.request_plugin.file is None:
            return ERR_NOFO("no request plugin specified")
        else:
            data = persistence.get_file(model.request_plugin.file)
            data = BytesIO(data)
            data.seek(0)

            valid = LT_MODEL
            if model.model_finalized:
                valid = LT_MODEL_FINALIZED

            return send_file(
                data, mimetype="application/octet-stream", cache_timeout=valid
            )

    @authenticated
    @model_access([BR.ROLE_EDIT_MODEL])
    def post(self, model_uuid, model, me):

        data = request.data
        file_pers = persistence.store_file(data)

        # TODO: prevent existing plugin to become orphaned
        newRequest = ORMModelLabelRequestPlugin()
        newRequest.file_id = file_pers.file_id
        db.session.add(newRequest)
        db.session.commit()

        model.request_plugin_id = newRequest.plugin_id
        model.model_last_modified = datetime.utcnow()
        model.model_etag = token_hex(16)
        db.session.commit()
        return SUCCESS()

    @authenticated
    def put(self, model_uuid, me):
        return ERR_FORB()

    @authenticated
    def delete(self, model_uuid, me):
        return ERR_FORB()
