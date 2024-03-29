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
import secrets
from sqlalchemy import select
from uuid import uuid4, UUID
from hashlib import sha256
from datetime import datetime, timedelta
from koi_api.common.return_codes import (
    ERR_BADR,
    ERR_TAKE,
    SUCCESS,
    ERR_FORB,
    ERR_NOFO,
    ERR_AUTH,
)
from koi_api.orm.user import ORMUser, ORMToken
from koi_api.orm import db
from koi_api.resources.base import BaseResource, authenticated, paged, user_access, json_request
from koi_api.common.string_constants import (
    BODY_USER as BU,
    BODY_GENERAL as BG,
    BODY_ROLE as BR,
)
from koi_api.resources.lifetime import LT_SESSION_TOKEN
from koi_api.common.name_generator import gen_name


def hash_password(password):
    return sha256(password.encode("utf8")).digest()


class APIUser(BaseResource):
    @paged
    @authenticated
    @user_access([])
    def get(self, me, page_offset, page_limit):
        """
        Get a list of all users
        """
        stmt_users = select(ORMUser).offset(page_offset).limit(page_limit)
        users = db.session.scalars(stmt_users).all()

        return SUCCESS([{BU.USER_UUID: UUID(bytes=u.user_uuid).hex, BU.USER_NAME: u.user_name} for u in users])

    @authenticated
    @user_access([BR.ROLE_EDIT_USERS])
    def post(self, me):

        new_user = ORMUser()
        user_name = None
        password = None

        json_data = request.get_json()

        if BU.USER_NAME in json_data:
            user_name = json_data[BU.USER_NAME]
        else:
            user_name = gen_name()

        if BU.PASSWORD in json_data:
            password = json_data[BU.PASSWORD]
        else:
            password = secrets.token_hex(16)

        user_stmt = select(ORMUser).where(ORMUser.user_name == user_name)
        user = db.session.scalars(user_stmt).one_or_none()

        while user is not None:
            user_name = user_name + secrets.token_hex(2)
            user_stmt = select(ORMUser).where(ORMUser.user_name == user_name)
            user = db.session.scalars(user_stmt).one_or_none()

        new_uuid = uuid4()

        new_user.user_name = user_name
        new_user.user_hash = hash_password(password)
        new_user.user_created = datetime.utcnow()
        new_user.user_uuid = new_uuid.bytes
        new_user.is_essential = 0

        db.session.add(new_user)
        db.session.commit()
        return SUCCESS({BU.USER_UUID: new_uuid.hex, BU.USER_NAME: new_user.user_name})

    @authenticated
    def put(self, me):
        return ERR_FORB()

    @authenticated
    def delete(self, me):
        return ERR_FORB()


class APIUserCollection(BaseResource):
    """
    DOCSTRING
    """
    @authenticated
    @user_access([])
    def get(self, user_uuid, me, user):

        return SUCCESS(
            {
                BU.USER_UUID: UUID(bytes=user.user_uuid).hex,
                BU.USER_NAME: user.user_name,
                BU.USER_ESSENTIAL: user.is_essential,
                BU.USER_CREATED: user.user_created.isoformat(),
            }
        )

    @authenticated
    def post(self, me, user_uuid):
        return ERR_FORB()

    @authenticated
    @user_access([BR.ROLE_EDIT_USERS])
    @json_request
    def put(self, user_uuid, user, me, json_object):
        """
        Update some user information.
        """

        # update the user fields if transmitted
        if BU.USER_NAME in json_object:
            user_probe_stmt = select(ORMUser).where(ORMUser.user_name == json_object[BU.USER_NAME])
            user_probe = db.session.scalars(user_probe_stmt).one_or_none()
            if user_probe is None:
                user.user_name = json_object[BU.USER_NAME]
            else:
                return ERR_TAKE("user name is taken")

        if BU.PASSWORD in json_object:
            user.user_hash = hash_password(json_object[BU.PASSWORD])

        db.session.commit()

        return SUCCESS()

    @authenticated
    @user_access([BR.ROLE_EDIT_USERS])
    def delete(self, user_uuid, user, me):
        """
        Delete a user profile.
        """

        if user.is_essential:
            return ERR_FORB("user is essential")

        # we need to invalidate all user tokens
        for token in user.tokens.all():
            token.token_invalidated = True
            token.token_value = "x"

        # delete the user entry
        db.session.delete(user)
        db.session.commit()

        return SUCCESS()


class APILogout(BaseResource):
    """
    This resource manages the logout from the service.
    """

    def get(self):
        return ERR_FORB()

    @authenticated
    def post(self, me):

        token_stmt = select(ORMToken).where(
            ORMToken.user == me,
        )
        my_tokens = db.session.scalars(token_stmt).all()

        for token in my_tokens:
            token.token_invalidated = True
            token.token_value = "x"

        db.session.commit()

        return SUCCESS("token invalidated")

    def put(self):
        return ERR_FORB()

    def delete(self):
        return ERR_FORB()


class APILogin(BaseResource):
    """
    This Resource manages the login to the service.
    """

    def get(self):
        return ERR_FORB()

    @json_request
    def post(self, json_object):
        """
        login with user name and password. The password is hashed and checked against
        the users hash in the database. If the login is successful, a new connection token
        is returned along the users id.
        """
        user_name = None
        password = None

        if BU.USER_NAME in json_object:
            user_name = str(json_object[BU.USER_NAME])
        else:
            return ERR_BADR()

        if BU.PASSWORD in json_object:
            password = str(json_object[BU.PASSWORD])
        else:
            return ERR_BADR()

        # lookup the user in the database
        user_stmt = select(ORMUser).where(ORMUser.user_name == user_name)
        user = db.session.scalars(user_stmt).one_or_none()

        # do we know the user trying to login?
        if user is None:
            return ERR_NOFO()  # This enables user enumeration! could be problematic

        # calculate the hash for the supplied password
        password = hash_password(password)

        # do these hashes match?
        if password != user.user_hash:
            return ERR_AUTH()

        token_value = None
        token_created = datetime.utcnow()
        token_valid = token_created + timedelta(seconds=LT_SESSION_TOKEN)

        token = 1
        retries_left = 20
        while token is not None:
            if retries_left > 0:
                retries_left -= 1
            else:
                return "token space exhausted", 500
            # make a new token!
            token_value = secrets.token_hex(16)

            # check if token exists
            token_stmt = select(ORMToken).where(ORMToken.token_value == token_value)
            token = db.session.scalars(token_stmt).one_or_none()

        # register token
        token = ORMToken()
        token.token_value = token_value
        token.user = user
        token.token_created = token_created
        token.token_valid = token_valid
        token.token_invalidated = False
        db.session.add(token)
        db.session.commit()

        # respond
        return SUCCESS(
            {BU.USER_UUID: UUID(bytes=user.user_uuid).hex, BG.TOKEN: token_value, BG.EXPIRES: token_valid.isoformat()}
        )

    def put(self):
        return ERR_FORB()

    def delete(self):
        return ERR_FORB()
