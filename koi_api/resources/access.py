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
from sqlalchemy import select
from koi_api.orm import db
from koi_api.resources.base import (
    BaseResource,
    paged,
    user_access,
    authenticated,
    json_request,
    model_access,
    instance_access,
)
from koi_api.orm.user import ORMUser
from koi_api.orm.role import ORMUserRoleGeneral, ORMUserRoleModel, ORMUserRoleInstance
from koi_api.orm.access import ORMAccessGeneral, ORMAccessModel, ORMAccessInstance
from koi_api.common.return_codes import ERR_FORB, ERR_NOFO, ERR_BADR, SUCCESS, ERR_TAKE
from koi_api.common.string_constants import (
    BODY_USER as BU,
    BODY_ACCESS as BA,
    BODY_ROLE as BR,
)


class APIGeneralAccess(BaseResource):
    @paged
    @authenticated
    def get(self, me, page_limit, page_offset):
        """
        Get all access rights granted in general
        """
        stmt = select(ORMAccessGeneral).offset(page_offset).limit(page_limit)
        granted_users = db.session.scalars(stmt).all()

        response = [
            {
                BA.ACCESS_UUID: UUID(bytes=acc.access_uuid).hex,
                BU.USER_UUID: UUID(bytes=acc.user.user_uuid).hex,
                BR.ROLE_UUID: UUID(bytes=acc.role.role_uuid).hex,
            }
            for acc in granted_users
        ]

        return SUCCESS(response)

    @authenticated
    @user_access([BR.ROLE_EDIT_USERS])
    @json_request
    def post(self, me, json_object):
        """
        Grant a new access right to a user
        """

        # parse the granted user id
        granted_user_uuid = None
        if BU.USER_UUID in json_object:
            granted_user_uuid = json_object[BU.USER_UUID]
        else:
            return ERR_BADR("missing user uuid")

        granted_role_uuid = None
        if BR.ROLE_UUID in json_object:
            granted_role_uuid = json_object[BR.ROLE_UUID]
        else:
            return ERR_BADR("missing role uuid")

        granted_user_uuid = UUID(granted_user_uuid)
        granted_role_uuid = UUID(granted_role_uuid)

        stmt_user = select(ORMUser).where(
            ORMUser.user_uuid == granted_user_uuid.bytes
        )
        stmt_role = select(ORMUserRoleGeneral).where(
            ORMUserRoleGeneral.role_uuid == granted_role_uuid.bytes
        )

        query_user = db.session.scalars(stmt_user).one_or_none()
        query_role = db.session.scalars(stmt_role).one_or_none()

        if query_role is None:
            return ERR_NOFO("unknown role_uuid")

        if query_user is None:
            return ERR_NOFO("unknown user_uuid")

        stmt_check = select(ORMAccessGeneral).where(
            ORMAccessGeneral.user_id == query_user.user_id,
            ORMAccessGeneral.role_id == query_role.role_id,
        )
        check = db.session.scalars(stmt_check).one_or_none()

        # check if this access is already granted?
        if check is not None:
            return ERR_TAKE()

        # add the new access right
        new_uuid = uuid4()
        new_access = ORMAccessGeneral()
        new_access.user = query_user
        new_access.role = query_role
        new_access.access_uuid = new_uuid.bytes
        db.session.add(new_access)
        db.session.commit()

        response = {
            BA.ACCESS_UUID: new_uuid.hex,
            BR.ROLE_UUID: UUID(bytes=query_role.role_uuid).hex,
            BU.USER_UUID: UUID(bytes=query_user.user_uuid).hex,
        }

        return SUCCESS(response)

    @authenticated
    def put(self, me):
        return ERR_FORB()

    @authenticated
    def delete(self, me):
        return ERR_FORB()


class APIGeneralAccessCollection(BaseResource):
    @authenticated
    @user_access([])
    def get(self, access_uuid, me):
        # get the access object
        stmt = select(ORMAccessGeneral).where(
            ORMAccessGeneral.access_uuid == UUID(access_uuid).bytes
        )
        access = db.session.scalars(stmt).one_or_none()

        if access is None:
            return ERR_NOFO()

        query_user = access.user
        query_role = access.role

        response = {
            BA.ACCESS_UUID: UUID(bytes=access.access_uuid).hex,
            BU.USER_UUID: UUID(bytes=query_user.user_uuid).hex,
            BR.ROLE_UUID: UUID(bytes=query_role.role_uuid).hex,
        }

        return SUCCESS(response)

    @authenticated
    def post(self, access_uuid, me):
        return ERR_FORB()

    @authenticated
    def put(self, access_uuid, me):
        return ERR_FORB()

    @authenticated
    def delete(self, access_uuid, me):
        stmt = select(ORMAccessGeneral).where(
            ORMAccessGeneral.access_uuid == UUID(access_uuid).bytes
        )
        access = db.session.scalars(stmt).one_or_none()

        if access is None:
            return ERR_NOFO()

        db.session.delete(access)
        db.session.commit()

        return SUCCESS()


class APIModelAccess(BaseResource):
    @authenticated
    @paged
    @model_access([BR.ROLE_SEE_MODEL])
    def get(self, model_uuid, model, me, page_offset, page_limit):
        """
        Get all access rights granted for a particular model
        """
        stmt = select(ORMAccessModel).where(
            ORMAccessModel.model_id == model.model_id
        ).offset(page_offset).limit(page_limit)
        access_rights = db.session.scalars(stmt).all()

        response = [
            {
                BA.ACCESS_UUID: UUID(bytes=ar.access_uuid).hex,
                BU.USER_UUID: UUID(bytes=ar.user.user_uuid).hex,
                BR.ROLE_UUID: UUID(bytes=ar.role.role_uuid).hex,
            }
            for ar in access_rights
        ]

        return SUCCESS(response)

    @authenticated
    @model_access([BR.ROLE_GRANT_ACCESS_MODEL, BR.ROLE_SEE_MODEL])
    @json_request
    def post(self, model_uuid, model, me, json_object):
        """
        Grant a new access right to a user
        """
        # parse the granted user id
        granted_user_uuid = None
        if BU.USER_UUID in json_object:
            granted_user_uuid = json_object[BU.USER_UUID]
        else:
            return ERR_BADR("missing field: " + BU.USER_UUID)

        role_uuid = None
        if BR.ROLE_UUID in json_object:
            role_uuid = json_object[BR.ROLE_UUID]
        else:
            return ERR_BADR("missing field: " + BR.ROLE_UUID)

        granted_user_uuid = UUID(granted_user_uuid)
        role_uuid = UUID(role_uuid)

        stmt_user = select(ORMUser).where(
            ORMUser.user_uuid == granted_user_uuid.bytes
        )
        stmt_role = select(ORMUserRoleModel).where(
            ORMUserRoleModel.role_uuid == role_uuid.bytes
        )

        granted_user = db.session.scalars(stmt_user).one_or_none()
        role = db.session.scalars(stmt_role).one_or_none()

        if granted_user is None:
            return ERR_NOFO("unknown user_uuid")

        if role is None:
            return ERR_NOFO("unknown role_uuid")

        stmt = select(ORMAccessModel).where(
            ORMAccessModel.model_id == model.model_id,
            ORMAccessModel.user_id == granted_user.user_id,
            ORMAccessModel.role_id == role.role_id
        )
        already_granted = db.session.scalars(stmt).one_or_none()

        if already_granted is not None:
            return ERR_TAKE("access right already granted!")

        # add the new access right
        new_uuid = uuid4()

        new_access = ORMAccessModel()
        new_access.model = model
        new_access.user = granted_user
        new_access.role = role
        new_access.access_uuid = new_uuid.bytes

        db.session.add(new_access)
        db.session.commit()

        response = {
            BA.ACCESS_UUID: new_uuid.hex,
            BU.USER_UUID: UUID(bytes=granted_user.user_uuid).hex,
            BR.ROLE_UUID: UUID(bytes=role.role_uuid).hex,
        }
        return SUCCESS(response)

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    def put(self, model_uuid, model, me):
        return ERR_FORB()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    def delete(self, model_uuid, model, me):
        return ERR_FORB()


class APIModelAccessCollection(BaseResource):
    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    def get(self, model_uuid, model, me, access_uuid):
        # get the requested access object
        stmt = select(ORMAccessModel).where(
            ORMAccessModel.access_uuid == UUID(access_uuid).bytes,
            ORMAccessModel.model_id == model.model_id
        )

        access = db.session.scalars(stmt).one_or_none()

        if access is None:
            return ERR_NOFO()

        # build the response
        response = {
            BA.ACCESS_UUID: UUID(bytes=access.access_uuid).hex,
            BU.USER_UUID: UUID(bytes=access.user.user_uuid).hex,
            BR.ROLE_UUID: UUID(bytes=access.role.role_uuid).hex,
        }
        return SUCCESS(response)

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    def post(self, model_uuid, model, me, access_uuid):
        return ERR_FORB()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    def put(self, model_uuid, model, me, access_uuid):
        return ERR_FORB()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL, BR.ROLE_GRANT_ACCESS_MODEL])
    def delete(self, model_uuid, model, me, access_uuid):
        # get the requested access object
        stmt = select(ORMAccessModel).where(
            ORMAccessModel.access_uuid == UUID(access_uuid).bytes,
            ORMAccessModel.model_id == model.model_id
        )
        access = db.session.scalars(stmt).one_or_none()

        if access is None:
            return ERR_NOFO()

        db.session.delete(access)
        db.session.commit()

        return SUCCESS()


class APIInstanceAccess(BaseResource):
    @paged
    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    def get(
        self, model_uuid, model, instance_uuid, instance, me, page_limit, page_offset
    ):
        """
        Get all access rights granted for a particular instance
        """
        # get all granted users

        stmt = select(ORMAccessInstance).where(
            ORMAccessInstance.instance_id == instance.instance_id
        ).offset(page_offset).limit(page_limit)
        granted_users = db.session.scalars(stmt).all()

        response = [
            {
                BA.ACCESS_UUID: UUID(bytes=acc.access_uuid).hex,
                BU.USER_UUID: UUID(bytes=acc.user.user_uuid).hex,
                BR.ROLE_UUID: UUID(bytes=acc.role.role_uuid).hex,
            }
            for acc in granted_users
        ]

        return SUCCESS(response)

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE, BR.ROLE_GRANT_ACCESS_INSTANCE])
    @json_request
    def post(self, model_uuid, model, instance_uuid, instance, me, json_object):
        """
        Grant a new access right to a user
        """
        # parse the granted user id
        granted_user_uuid = None
        if BU.USER_UUID in json_object:
            granted_user_uuid = UUID(json_object[BU.USER_UUID])
        else:
            return ERR_BADR("missing field: " + BU.USER_UUID)

        # parse the granted user id
        granted_role_uuid = None
        if BR.ROLE_UUID in json_object:
            granted_role_uuid = UUID(json_object[BR.ROLE_UUID])
        else:
            return ERR_BADR("missing field: " + BR.ROLE_UUID)

        stmt_user = select(ORMUser).where(
            ORMUser.user_uuid == granted_user_uuid.bytes
        )
        stmt_role = select(ORMUserRoleInstance).where(
            ORMUserRoleInstance.role_uuid == granted_role_uuid.bytes
        )

        granted_user = db.session.scalars(stmt_user).one_or_none()
        granted_role = db.session.scalars(stmt_role).one_or_none()

        if granted_user is None:
            return ERR_NOFO("unknown user_uuid")

        if granted_role is None:
            return ERR_NOFO("unknown role_uuid")

        stmt = select(ORMAccessInstance).where(
            ORMAccessInstance.instance_id == instance.instance_id,
            ORMAccessInstance.user_id == granted_user.user_id,
            ORMAccessInstance.role_id == granted_role.role_id
        )
        check = db.session.scalars(stmt).one_or_none()

        if check is not None:
            return ERR_TAKE()

        # add the new access right
        new_uuid = uuid4()
        new_access = ORMAccessInstance()
        new_access.instance = instance
        new_access.user = granted_user
        new_access.role = granted_role
        new_access.access_uuid = new_uuid.bytes
        db.session.add(new_access)
        db.session.commit()

        response = {
            BA.ACCESS_UUID: new_uuid.hex,
            BU.USER_UUID: granted_user_uuid.hex,
            BR.ROLE_UUID: granted_role_uuid.hex,
        }
        return SUCCESS(response)

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


class APIInstanceAccessCollection(BaseResource):
    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    def get(self, model_uuid, model, instance_uuid, instance, me, access_uuid):

        # get the access object
        stmt = select(ORMAccessInstance).where(
            ORMAccessInstance.access_uuid == UUID(access_uuid).bytes,
            ORMAccessInstance.instance_id == instance.instance_id
        )
        access = db.session.scalars(stmt).one_or_none()

        if access is None:
            return ERR_NOFO()

        # construct the response
        response = {
            BA.ACCESS_UUID: UUID(bytes=access.access_uuid).hex,
            BU.USER_UUID: UUID(bytes=access.user.user_uuid).hex,
            BR.ROLE_UUID: UUID(bytes=access.role.role_uuid).hex,
        }

        return SUCCESS(response)

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    def post(self, model_uuid, model, instance_uuid, instance, access_uuid, me):
        return ERR_FORB()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE])
    def put(self, model_uuid, model, instance_uuid, instance, access_uuid, me):
        return ERR_FORB()

    @authenticated
    @model_access([BR.ROLE_SEE_MODEL])
    @instance_access([BR.ROLE_SEE_INSTANCE, BR.ROLE_GRANT_ACCESS_INSTANCE])
    def delete(self, model_uuid, model, instance_uuid, instance, me, access_uuid):
        # get the access object
        
        stmt = select(ORMAccessInstance).where(
            ORMAccessInstance.access_uuid == UUID(access_uuid).bytes,
            ORMAccessInstance.instance_id == instance.instance_id
        )
        
        access = db.session.scalars(stmt).one_or_none()

        if access is None:
            return ERR_NOFO()

        db.session.delete(access)
        db.session.commit()

        return SUCCESS()
