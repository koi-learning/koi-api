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

from koi_api.common.string_constants import BODY_ROLE as BR
from koi_api.orm import db


class ORMUserRoleGeneral(db.Model):
    __tablename__ = "userrolegeneral"
    __table_args__ = (db.Index("idx_userrolegeneral_role_uuid", "role_uuid", mysql_length=16),)
    role_id = db.Column(db.Integer, primary_key=True, unique=True)
    role_name = db.Column(db.String(500))
    role_description = db.Column(db.String(500))
    role_uuid = db.Column(db.LargeBinary(16))

    grant_access = db.Column(db.Boolean)

    edit_users = db.Column(db.Boolean)

    edit_models = db.Column(db.Boolean)

    edit_roles = db.Column(db.Boolean)

    is_essential = db.Column(db.Boolean)

    def check_right(self, right):
        mapping = {
            BR.ROLE_GRANT_ACCESS: self.grant_access,
            BR.ROLE_EDIT_USERS: self.edit_users,
            BR.ROLE_EDIT_MODELS: self.edit_models,
            BR.ROLE_EDIT_ROLES: self.edit_roles,
        }

        for key, val in mapping.items():
            if key == right and val is True:
                return True
        return False


class ORMUserRoleInstance(db.Model):
    __tablename__ = "userroleinstance"
    __table_args__ = (db.Index("idx_userroleinstance_role_uuid", "role_uuid", mysql_length=16),)
    role_id = db.Column(db.Integer, primary_key=True, unique=True)
    role_name = db.Column(db.String(500))
    role_description = db.Column(db.String(500))
    role_uuid = db.Column(db.LargeBinary(16))

    can_see = db.Column(db.Boolean)
    add_sample = db.Column(db.Boolean)

    get_training_data = db.Column(db.Boolean)
    get_inference_data = db.Column(db.Boolean)

    grant_access = db.Column(db.Boolean)

    edit = db.Column(db.Boolean)

    request_label = db.Column(db.Boolean)
    response_label = db.Column(db.Boolean)

    is_essential = db.Column(db.Boolean)

    def check_right(self, right):
        mapping = {
            BR.ROLE_SEE_INSTANCE: self.can_see,
            BR.ROLE_ADD_SAMPLE: self.add_sample,
            BR.ROLE_GET_TRAINING_DATA: self.get_training_data,
            BR.ROLE_GET_INFERENCE_DATA: self.get_inference_data,
            BR.ROLE_EDIT_INSTANCE: self.edit,
            BR.ROLE_GRANT_ACCESS_INSTANCE: self.grant_access,
            BR.ROLE_REQUEST_LABEL: self.request_label,
            BR.ROLE_RESPONSE_LABEL: self.response_label,
        }

        for key, val in mapping.items():
            if key == right and val is True:
                return True
        return False


class ORMUserRoleModel(db.Model):
    __tablename__ = "userrolemodel"
    __table_args__ = (db.Index("idx_userrolemodel_role_uuid", "role_uuid", mysql_length=16),)
    role_id = db.Column(db.Integer, primary_key=True, unique=True)
    role_name = db.Column(db.String(500))
    role_description = db.Column(db.String(500))
    role_uuid = db.Column(db.LargeBinary(16))

    can_see = db.Column(db.Boolean)
    instantiate = db.Column(db.Boolean)
    edit = db.Column(db.Boolean)
    download_code = db.Column(db.Boolean)
    grant_access = db.Column(db.Boolean)

    is_essential = db.Column(db.Boolean)

    def check_right(self, right):
        mapping = {
            BR.ROLE_SEE_MODEL: self.can_see,
            BR.ROLE_INSTANTIATE_MODEL: self.instantiate,
            BR.ROLE_EDIT_MODEL: self.edit,
            BR.ROLE_DOWNLOAD_CODE: self.download_code,
            BR.ROLE_GRANT_ACCESS_MODEL: self.grant_access,
        }

        for key, val in mapping.items():
            if key == right and val is True:
                return True
        return False
