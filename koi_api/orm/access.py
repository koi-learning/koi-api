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

from ..orm import db


class ORMAccessGeneral(db.Model):
    __tablename__ = "accessgeneral"
    __table_args__ = (db.Index("idx_accessgeneral_access_uuid", "access_uuid", mysql_length=16),)
    acess_id = db.Column(db.Integer, primary_key=True, unique=True)
    access_uuid = db.Column(db.Binary(16))

    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    user = db.relationship("ORMUser", back_populates="access_rights")

    role_id = db.Column(db.Integer, db.ForeignKey("userrolegeneral.role_id"))
    role = db.relationship("ORMUserRoleGeneral")


class ORMAccessInstance(db.Model):
    __tablename__ = "accessinstance"
    __table_args__ = (db.Index("idx_accessinstance_access_uuid", "access_uuid", mysql_length=16),)
    acess_id = db.Column(db.Integer, primary_key=True, unique=True)
    access_uuid = db.Column(db.Binary(16))
    instance_id = db.Column(db.Integer, db.ForeignKey("instance.instance_id"))
    instance = db.relationship("ORMInstance", back_populates="granted_users")

    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    user = db.relationship("ORMUser", back_populates="access_rights_instances")

    role_id = db.Column(db.Integer, db.ForeignKey("userroleinstance.role_id"))
    role = db.relationship("ORMUserRoleInstance")


class ORMAccessModel(db.Model):
    __tablename__ = "accessmodel"
    __table_args__ = (db.Index("idx_accessmodel_access_uuid", "access_uuid", mysql_length=16),)
    acess_id = db.Column(db.Integer, primary_key=True, unique=True)
    access_uuid = db.Column(db.Binary(16))
    model_id = db.Column(db.Integer, db.ForeignKey("model.model_id"))
    model = db.relationship("ORMModel", back_populates="granted_users")

    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    user = db.relationship("ORMUser", back_populates="access_rights_models")

    role_id = db.Column(db.Integer, db.ForeignKey("userrolemodel.role_id"))
    role = db.relationship("ORMUserRoleModel")
