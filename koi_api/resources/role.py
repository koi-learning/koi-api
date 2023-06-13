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

from uuid import uuid4, UUID
from koi_api.orm import db
from koi_api.resources.base import BaseResource, paged, authenticated, user_access, json_request
from koi_api.orm.role import ORMUserRoleGeneral, ORMUserRoleModel, ORMUserRoleInstance
from koi_api.common.return_codes import ERR_FORB, ERR_NOFO, ERR_BADR, SUCCESS
from koi_api.common.string_constants import BODY_ROLE as BR
from koi_api.common.name_generator import gen_name
from sqlalchemy import select


class APIUserRoleGeneral(BaseResource):
    @paged
    @authenticated
    @user_access([])
    def get(self, page_offset, page_limit, me):
        # get the roles
        roles_stmt = select(ORMUserRoleGeneral).offset(page_offset).limit(page_limit)
        roles = db.session.scalars(roles_stmt).all()

        # construct the response
        response = [
            {
                BR.ROLE_UUID: UUID(bytes=r.role_uuid).hex,
                BR.ROLE_NAME: r.role_name,
                BR.ROLE_DESCRIPTION: r.role_description,
                BR.ROLE_GRANT_ACCESS: int(r.grant_access),
                BR.ROLE_EDIT_USERS: int(r.edit_users),
                BR.ROLE_EDIT_MODELS: int(r.edit_models),
                BR.ROLE_EDIT_ROLES: int(r.edit_roles),
            }
            for r in roles
            if r.role_uuid is not None
        ]

        return SUCCESS(response)

    @authenticated
    @user_access([BR.ROLE_EDIT_ROLES])
    @json_request
    def post(self, me, json_object):

        new_uuid = uuid4()
        new_role = ORMUserRoleGeneral()
        new_role.role_uuid = new_uuid.bytes
        new_role.is_essential = 0

        if BR.ROLE_NAME in json_object:
            new_role.role_name = str(json_object[BR.ROLE_NAME])
        else:
            new_role.role_name = gen_name()

        if BR.ROLE_DESCRIPTION in json_object:
            new_role.role_description = str(json_object[BR.ROLE_DESCRIPTION])
        else:
            new_role.role_description = ""

        if BR.ROLE_GRANT_ACCESS in json_object:
            try:
                new_role.grant_access = min(
                    1, max(0, int(json_object[BR.ROLE_GRANT_ACCESS]))
                )
            except TypeError:
                return ERR_BADR()
        else:
            new_role.grant_access = 0

        if BR.ROLE_EDIT_USERS in json_object:
            try:
                new_role.edit_users = min(
                    1, max(0, int(json_object[BR.ROLE_EDIT_USERS]))
                )
            except TypeError:
                return ERR_BADR()
        else:
            new_role.edit_users = 0

        if BR.ROLE_EDIT_MODELS in json_object:
            try:
                new_role.edit_models = min(
                    1, max(0, int(json_object[BR.ROLE_EDIT_MODELS]))
                )
            except TypeError:
                return ERR_BADR()
        else:
            new_role.edit_models = 0

        if BR.ROLE_EDIT_ROLES in json_object:
            try:
                new_role.edit_roles = min(
                    1, max(0, int(json_object[BR.ROLE_EDIT_ROLES]))
                )
            except TypeError:
                return ERR_BADR()
        else:
            new_role.edit_roles = 0

        db.session.add(new_role)
        db.session.commit()

        return SUCCESS(
            {
                BR.ROLE_UUID: new_uuid.hex,
                BR.ROLE_NAME: new_role.role_name,
                BR.ROLE_DESCRIPTION: new_role.role_description,
                BR.ROLE_GRANT_ACCESS: int(new_role.grant_access),
                BR.ROLE_EDIT_USERS: int(new_role.edit_users),
                BR.ROLE_EDIT_MODELS: int(new_role.edit_models),
                BR.ROLE_EDIT_ROLES: int(new_role.edit_roles),
            }
        )

    @authenticated
    def put(self, me):
        return ERR_FORB()

    @authenticated
    def delete(self, me):
        return ERR_FORB()


class APIUserRoleGeneralCollection(BaseResource):
    @authenticated
    @user_access([])
    def get(self, me, role_uuid):
        # get the role
        role_stmt = select(ORMUserRoleGeneral).where(
            ORMUserRoleGeneral.role_uuid == UUID(role_uuid).bytes
        )
        r = db.session.scalars(role_stmt).one_or_none()

        if r is None:
            return ERR_NOFO()

        response = {
            BR.ROLE_UUID: UUID(bytes=r.role_uuid).hex,
            BR.ROLE_NAME: r.role_name,
            BR.ROLE_DESCRIPTION: r.role_description,
            BR.ROLE_GRANT_ACCESS: int(r.grant_access),
            BR.ROLE_EDIT_USERS: int(r.edit_users),
            BR.ROLE_EDIT_MODELS: int(r.edit_models),
            BR.ROLE_EDIT_ROLES: int(r.edit_roles),
            BR.ROLE_ESSENTIAL: int(r.is_essential),
        }

        return SUCCESS(response)

    @authenticated
    def post(self, me, role_uuid):
        return ERR_FORB()

    @authenticated
    @user_access([BR.ROLE_EDIT_ROLES])
    @json_request
    def put(self, me, role_uuid, json_object):
        # get the role
        role_stmt = select(ORMUserRoleGeneral).where(
            ORMUserRoleGeneral.role_uuid == UUID(role_uuid).bytes
        )
        r = db.session.scalars(role_stmt).one_or_none()

        if r is None:
            return ERR_NOFO()

        if BR.ROLE_NAME in json_object:
            r.role_name = str(json_object[BR.ROLE_NAME])

        if BR.ROLE_DESCRIPTION in json_object:
            r.role_description = str(json_object[BR.ROLE_DESCRIPTION])

        if BR.ROLE_GRANT_ACCESS in json_object:
            try:
                r.grant_access = min(1, max(0, int(json_object[BR.ROLE_GRANT_ACCESS])))
            except TypeError:
                return ERR_BADR()

        if BR.ROLE_EDIT_USERS in json_object:
            try:
                r.edit_users = min(1, max(0, int(json_object[BR.ROLE_EDIT_USERS])))
            except TypeError:
                return ERR_BADR()

        if BR.ROLE_EDIT_MODELS in json_object:
            try:
                r.edit_models = min(1, max(0, int(json_object[BR.ROLE_EDIT_MODELS])))
            except TypeError:
                return ERR_BADR()

        if BR.ROLE_EDIT_ROLES in json_object:
            try:
                r.edit_roles = min(1, max(0, int(json_object[BR.ROLE_EDIT_ROLES])))
            except TypeError:
                return ERR_BADR()

        db.session.commit()

        return SUCCESS()

    @authenticated
    @user_access([BR.ROLE_EDIT_ROLES])
    def delete(self, me, role_uuid):
        # get the role
        role_stmt = select(ORMUserRoleGeneral).where(
            ORMUserRoleGeneral.role_uuid == UUID(role_uuid).bytes
        )
        r = db.session.scalars(role_stmt).one_or_none()

        if r is None:
            return ERR_NOFO()

        if r.is_essential:
            return ERR_BADR("role is essential")

        db.session.delete(r)
        db.session.commit()

        return SUCCESS()


class APIUserRoleModel(BaseResource):
    @paged
    @authenticated
    @user_access([])
    def get(self, me, page_offset, page_limit):
        # get the roles
        roles_stmt = select(ORMUserRoleModel).offset(page_offset).limit(page_limit)
        roles = db.session.scalars(roles_stmt).all()

        # construct the response
        response = [
            {
                BR.ROLE_UUID: UUID(bytes=r.role_uuid).hex,
                BR.ROLE_NAME: r.role_name,
                BR.ROLE_DESCRIPTION: r.role_description,
                BR.ROLE_SEE_MODEL: int(r.can_see),
                BR.ROLE_INSTANTIATE_MODEL: int(r.instantiate),
                BR.ROLE_EDIT_MODEL: int(r.edit),
                BR.ROLE_DOWNLOAD_CODE: int(r.download_code),
                BR.ROLE_GRANT_ACCESS_MODEL: int(r.grant_access),
            }
            for r in roles
        ]

        return SUCCESS(response)

    @authenticated
    @user_access([BR.ROLE_EDIT_ROLES])
    @json_request
    def post(self, me, json_object):

        new_uuid = uuid4()
        new_role = ORMUserRoleModel()
        new_role.role_uuid = new_uuid.bytes

        new_role.is_essential = 0

        if BR.ROLE_NAME in json_object:
            new_role.role_name = str(json_object[BR.ROLE_NAME])
        else:
            new_role.role_name = gen_name()

        if BR.ROLE_DESCRIPTION in json_object:
            new_role.role_description = str(json_object[BR.ROLE_DESCRIPTION])
        else:
            new_role.role_description = ""

        if BR.ROLE_SEE_MODEL in json_object:
            try:
                new_role.can_see = min(1, max(0, int(json_object[BR.ROLE_SEE_MODEL])))
            except TypeError:
                return ERR_BADR()
        else:
            new_role.can_see = 0

        if BR.ROLE_INSTANTIATE_MODEL in json_object:
            try:
                new_role.instantiate = min(
                    1, max(0, int(json_object[BR.ROLE_INSTANTIATE_MODEL]))
                )
            except TypeError:
                return ERR_BADR()
        else:
            new_role.instantiate = 0

        if BR.ROLE_EDIT_MODEL in json_object:
            try:
                new_role.edit = min(1, max(0, int(json_object[BR.ROLE_EDIT_MODEL])))
            except TypeError:
                return ERR_BADR()
        else:
            new_role.edit = 0

        if BR.ROLE_DOWNLOAD_CODE in json_object:
            try:
                new_role.download_code = min(
                    1, max(0, int(json_object[BR.ROLE_DOWNLOAD_CODE]))
                )
            except TypeError:
                return ERR_BADR()
        else:
            new_role.download_code = 0

        if BR.ROLE_GRANT_ACCESS_MODEL in json_object:
            try:
                new_role.grant_access = min(
                    1, max(0, int(json_object[BR.ROLE_GRANT_ACCESS_MODEL]))
                )
            except TypeError:
                return ERR_BADR()
        else:
            new_role.grant_access = 0

        db.session.add(new_role)
        db.session.commit()

        return SUCCESS(
            {
                BR.ROLE_UUID: new_uuid.hex,
                BR.ROLE_NAME: new_role.role_name,
                BR.ROLE_DESCRIPTION: new_role.role_description,
                BR.ROLE_SEE_MODEL: int(new_role.can_see),
                BR.ROLE_INSTANTIATE_MODEL: int(new_role.instantiate),
                BR.ROLE_EDIT_MODEL: int(new_role.edit),
                BR.ROLE_DOWNLOAD_CODE: int(new_role.download_code),
                BR.ROLE_GRANT_ACCESS_MODEL: int(new_role.grant_access),
            }
        )

    @authenticated
    def put(self, me):
        return ERR_FORB()

    @authenticated
    def delete(self, me):
        return ERR_FORB()


class APIUserRoleModelCollection(BaseResource):
    @authenticated
    @user_access([])
    def get(self, me, role_uuid):
        # get the role
        role_stmt = select(ORMUserRoleModel).where(
            ORMUserRoleModel.role_uuid == UUID(role_uuid).bytes
        )
        r = db.session.scalars(role_stmt).one_or_none()

        if r is None:
            return ERR_NOFO()

        response = {
            BR.ROLE_UUID: UUID(bytes=r.role_uuid).hex,
            BR.ROLE_NAME: r.role_name,
            BR.ROLE_DESCRIPTION: r.role_description,
            BR.ROLE_SEE_MODEL: r.can_see,
            BR.ROLE_INSTANTIATE_MODEL: r.instantiate,
            BR.ROLE_EDIT_MODEL: r.edit,
            BR.ROLE_DOWNLOAD_CODE: r.download_code,
            BR.ROLE_GRANT_ACCESS_MODEL: r.grant_access,
        }

        return SUCCESS(response)

    @authenticated
    def post(self, me, role_uuid):
        return ERR_FORB()

    @authenticated
    @user_access([BR.ROLE_EDIT_ROLES])
    @json_request
    def put(self, me, role_uuid, json_object):
        role_stmt = select(ORMUserRoleModel).where(
            ORMUserRoleModel.role_uuid == UUID(role_uuid).bytes
        )
        r = db.session.scalars(role_stmt).one_or_none()

        if r is None:
            return ERR_NOFO()

        if BR.ROLE_NAME in json_object:
            r.role_name = str(json_object[BR.ROLE_NAME])

        if BR.ROLE_DESCRIPTION in json_object:
            r.role_description = str(json_object[BR.ROLE_DESCRIPTION])

        if BR.ROLE_SEE_MODEL in json_object:
            try:
                r.can_see = min(1, max(0, int(json_object[BR.ROLE_SEE_MODEL])))
            except TypeError:
                return ERR_BADR()

        if BR.ROLE_INSTANTIATE_MODEL in json_object:
            try:
                r.instantiate = min(
                    1, max(0, int(json_object[BR.ROLE_INSTANTIATE_MODEL]))
                )
            except TypeError:
                return ERR_BADR()

        if BR.ROLE_EDIT_MODEL in json_object:
            try:
                r.edit = min(1, max(0, int(json_object[BR.ROLE_EDIT_MODEL])))
            except TypeError:
                return ERR_BADR()

        if BR.ROLE_DOWNLOAD_CODE in json_object:
            try:
                r.download_code = min(
                    1, max(0, int(json_object[BR.ROLE_DOWNLOAD_CODE]))
                )
            except TypeError:
                return ERR_BADR()

        if BR.ROLE_GRANT_ACCESS_MODEL in json_object:
            try:
                r.grant_access = min(
                    1, max(0, int(json_object[BR.ROLE_GRANT_ACCESS_MODEL]))
                )
            except TypeError:
                return ERR_BADR()

        db.session.commit()

        return SUCCESS()

    @authenticated
    @user_access([BR.ROLE_EDIT_ROLES])
    def delete(self, me, role_uuid):
        # get the role
        role_stmt = select(ORMUserRoleModel).where(
            ORMUserRoleModel.role_uuid == UUID(role_uuid).bytes
        )
        r = db.session.scalars(role_stmt).one_or_none()

        if r is None:
            return ERR_NOFO()

        if r.is_essential:
            return ERR_BADR("role is essential")

        db.session.delete(r)
        db.session.commit()

        return SUCCESS()


class APIUserRoleInstance(BaseResource):
    @paged
    @authenticated
    @user_access([])
    def get(self, page_offset, page_limit, me):
        # get the roles
        roles_stmt = select(ORMUserRoleInstance).offset(page_offset).limit(page_limit)
        roles = db.session.scalars(roles_stmt).all()

        # construct the response
        response = [
            {
                BR.ROLE_UUID: UUID(bytes=r.role_uuid).hex,
                BR.ROLE_NAME: r.role_name,
                BR.ROLE_DESCRIPTION: r.role_description,
                BR.ROLE_SEE_INSTANCE: int(r.can_see),
                BR.ROLE_ADD_SAMPLE: int(r.add_sample),
                BR.ROLE_GET_TRAINING_DATA: int(r.get_training_data),
                BR.ROLE_GET_INFERENCE_DATA: int(r.get_inference_data),
                BR.ROLE_EDIT_INSTANCE: int(r.edit),
                BR.ROLE_GRANT_ACCESS_INSTANCE: int(r.grant_access),
                BR.ROLE_REQUEST_LABEL: int(r.request_label),
                BR.ROLE_RESPONSE_LABEL: int(r.response_label),
            }
            for r in roles
        ]

        return SUCCESS(response)

    @authenticated
    @user_access([BR.ROLE_EDIT_ROLES])
    @json_request
    def post(self, me, json_object):

        new_uuid = uuid4()
        new_role = ORMUserRoleInstance()
        new_role.role_uuid = new_uuid.bytes

        new_role.is_essential = 0

        if BR.ROLE_NAME in json_object:
            new_role.role_name = str(json_object[BR.ROLE_NAME])
        else:
            new_role.role_name = gen_name()

        if BR.ROLE_DESCRIPTION in json_object:
            new_role.role_description = str(json_object[BR.ROLE_DESCRIPTION])
        else:
            new_role.role_description = ""

        if BR.ROLE_SEE_INSTANCE in json_object:
            try:
                new_role.can_see = min(
                    1, max(0, int(json_object[BR.ROLE_SEE_INSTANCE]))
                )
            except TypeError:
                return ERR_BADR()
        else:
            new_role.can_see = 0

        if BR.ROLE_ADD_SAMPLE in json_object:
            try:
                new_role.add_sample = min(
                    1, max(0, int(json_object[BR.ROLE_ADD_SAMPLE]))
                )
            except TypeError:
                return ERR_BADR()
        else:
            new_role.add_sample = 0

        if BR.ROLE_GET_TRAINING_DATA in json_object:
            try:
                new_role.get_training_data = min(
                    1, max(0, int(json_object[BR.ROLE_GET_TRAINING_DATA]))
                )
            except TypeError:
                return ERR_BADR()
        else:
            new_role.get_training_data = 0

        if BR.ROLE_GET_INFERENCE_DATA in json_object:
            try:
                new_role.get_inference_data = min(
                    1, max(0, int(json_object[BR.ROLE_GET_INFERENCE_DATA]))
                )
            except TypeError:
                return ERR_BADR()
        else:
            new_role.get_inference_data = 0

        if BR.ROLE_EDIT_INSTANCE in json_object:
            try:
                new_role.edit = min(1, max(0, int(json_object[BR.ROLE_EDIT_INSTANCE])))
            except TypeError:
                return ERR_BADR()
        else:
            new_role.edit = 0

        if BR.ROLE_GRANT_ACCESS_INSTANCE in json_object:
            try:
                new_role.grant_access = min(
                    1, max(0, int(json_object[BR.ROLE_GRANT_ACCESS_INSTANCE]))
                )
            except TypeError:
                return ERR_BADR()
        else:
            new_role.grant_access = 0

        if BR.ROLE_REQUEST_LABEL in json_object:
            try:
                new_role.request_label = min(
                    1, max(0, int(json_object[BR.ROLE_REQUEST_LABEL]))
                )
            except TypeError:
                return ERR_BADR()
        else:
            new_role.request_label = 0

        if BR.ROLE_RESPONSE_LABEL in json_object:
            try:
                new_role.response_label = min(
                    1, max(0, int(json_object[BR.ROLE_RESPONSE_LABEL]))
                )
            except TypeError:
                return ERR_BADR()
        else:
            new_role.response_label = 0

        db.session.add(new_role)
        db.session.commit()

        return SUCCESS(
            {
                BR.ROLE_UUID: new_uuid.hex,
                BR.ROLE_NAME: new_role.role_name,
                BR.ROLE_DESCRIPTION: new_role.role_description,
                BR.ROLE_SEE_INSTANCE: int(new_role.can_see),
                BR.ROLE_ADD_SAMPLE: int(new_role.add_sample),
                BR.ROLE_GET_TRAINING_DATA: int(new_role.get_training_data),
                BR.ROLE_GET_INFERENCE_DATA: int(new_role.get_inference_data),
                BR.ROLE_EDIT_INSTANCE: int(new_role.edit),
                BR.ROLE_GRANT_ACCESS_INSTANCE: int(new_role.grant_access),
                BR.ROLE_REQUEST_LABEL: int(new_role.request_label),
                BR.ROLE_RESPONSE_LABEL: int(new_role.response_label),
            }
        )

    @authenticated
    def put(self, me):
        return ERR_FORB()

    @authenticated
    def delete(self, me):
        return ERR_FORB()


class APIUserRoleInstanceCollection(BaseResource):
    @authenticated
    @user_access([])
    def get(self, role_uuid, me):
        # get the role
        role_stmt = select(ORMUserRoleInstance).where(
            ORMUserRoleInstance.role_uuid == UUID(role_uuid).bytes
        )
        r = db.session.scalars(role_stmt).one_or_none()

        if r is None:
            return ERR_NOFO()

        response = {
            BR.ROLE_UUID: UUID(bytes=r.role_uuid).hex,
            BR.ROLE_NAME: r.role_name,
            BR.ROLE_DESCRIPTION: r.role_description,
            BR.ROLE_SEE_INSTANCE: int(r.can_see),
            BR.ROLE_ADD_SAMPLE: int(r.add_sample),
            BR.ROLE_GET_TRAINING_DATA: int(r.get_training_data),
            BR.ROLE_GET_INFERENCE_DATA: int(r.get_inference_data),
            BR.ROLE_EDIT_INSTANCE: int(r.edit),
            BR.ROLE_GRANT_ACCESS_INSTANCE: int(r.grant_access),
            BR.ROLE_REQUEST_LABEL: int(r.request_label),
            BR.ROLE_RESPONSE_LABEL: int(r.response_label),
        }

        return SUCCESS(response)

    @authenticated
    def post(self, role_uuid, me):
        return ERR_FORB()

    @authenticated
    @user_access([BR.ROLE_EDIT_ROLES])
    @json_request
    def put(self, role_uuid, me, json_object):
        role_stmt = select(ORMUserRoleInstance).where(
            ORMUserRoleInstance.role_uuid == UUID(role_uuid).bytes
        )
        r = db.session.scalars(role_stmt).one_or_none()

        if r is None:
            return ERR_NOFO()

        if BR.ROLE_NAME in json_object:
            r.role_name = str(json_object[BR.ROLE_NAME])

        if BR.ROLE_DESCRIPTION in json_object:
            r.role_description = str(json_object[BR.ROLE_DESCRIPTION])

        if BR.ROLE_SEE_INSTANCE in json_object:
            try:
                r.can_see = min(1, max(0, int(json_object[BR.ROLE_SEE_INSTANCE])))
            except TypeError:
                return ERR_BADR()

        if BR.ROLE_ADD_SAMPLE in json_object:
            try:
                r.add_sample = min(1, max(0, int(json_object[BR.ROLE_ADD_SAMPLE])))
            except TypeError:
                return ERR_BADR()

        if BR.ROLE_GET_TRAINING_DATA in json_object:
            try:
                r.get_training_data = min(
                    1, max(0, int(json_object[BR.ROLE_GET_TRAINING_DATA]))
                )
            except TypeError:
                return ERR_BADR()

        if BR.ROLE_GET_INFERENCE_DATA in json_object:
            try:
                r.get_inference_data = min(
                    1, max(0, int(json_object[BR.ROLE_GET_INFERENCE_DATA]))
                )
            except TypeError:
                return ERR_BADR()

        if BR.ROLE_EDIT_INSTANCE in json_object:
            try:
                r.edit = min(1, max(0, int(json_object[BR.ROLE_EDIT_INSTANCE])))
            except TypeError:
                return ERR_BADR()

        if BR.ROLE_GRANT_ACCESS_INSTANCE in json_object:
            try:
                r.grant_access = min(
                    1, max(0, int(json_object[BR.ROLE_GRANT_ACCESS_INSTANCE]))
                )
            except TypeError:
                return ERR_BADR()

        if BR.ROLE_REQUEST_LABEL in json_object:
            try:
                r.request_label = min(
                    1, max(0, int(json_object[BR.ROLE_REQUEST_LABEL]))
                )
            except TypeError:
                return ERR_BADR()

        if BR.ROLE_RESPONSE_LABEL in json_object:
            try:
                r.response_label = min(
                    1, max(0, int(json_object[BR.ROLE_RESPONSE_LABEL]))
                )
            except TypeError:
                return ERR_BADR()

        db.session.commit()

        return SUCCESS()

    @authenticated
    @user_access([BR.ROLE_EDIT_ROLES])
    def delete(self, role_uuid, me):
        # get the role
        role_stmt = select(ORMUserRoleInstance).where(
            ORMUserRoleInstance.role_uuid == UUID(role_uuid).bytes
        )
        r = db.session.scalars(role_stmt).one_or_none()

        if r is None:
            return ERR_NOFO()

        if r.is_essential:
            return ERR_BADR("role is essential")

        db.session.delete(r)
        db.session.commit()

        return SUCCESS()
