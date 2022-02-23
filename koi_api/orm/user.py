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


class ORMUser(db.Model):
    __tablename__ = "user"
    __table_args__ = (db.Index("idx_user_user_uuid", "user_uuid", mysql_length=16),)

    user_id = db.Column(db.Integer, primary_key=True, unique=True)
    user_name = db.Column(db.String(500), unique=True)
    user_hash = db.Column(db.LargeBinary(32))
    user_created = db.Column(db.DateTime)
    user_uuid = db.Column(db.LargeBinary(16))
    is_essential = db.Column(db.Boolean)

    tokens = db.relationship(
        "ORMToken", back_populates="user", lazy="dynamic", cascade="all, delete"
    )

    access_rights = db.relationship(
        "ORMAccessGeneral", back_populates="user", lazy="dynamic", cascade="all, delete"
    )

    access_rights_instances = db.relationship(
        "ORMAccessInstance",
        back_populates="user",
        lazy="dynamic",
        cascade="all, delete",
    )
    access_rights_models = db.relationship(
        "ORMAccessModel", back_populates="user", lazy="dynamic", cascade="all, delete"
    )

    def has_rights(self, rights):
        roles = [ar.role for ar in self.access_rights.all()]

        for right in rights:
            has_right = False
            for role in roles:
                if role.check_right(right):
                    has_right = True
                    break
            if not has_right:
                return False
        return True

    def has_rights_model(self, model, rights):
        roles = [
            ar.role
            for ar in self.access_rights_models.filter_by(model_id=model.model_id).all()
        ]
        for right in rights:
            has_right = False
            for role in roles:
                if role.check_right(right):
                    has_right = True
                    break
            if not has_right:
                return False
        return True

    def has_rights_instance(self, instance, rights):
        roles = [
            ar.role
            for ar in self.access_rights_instances.filter_by(
                instance_id=instance.instance_id
            ).all()
        ]
        for right in rights:
            has_right = False
            for role in roles:
                if role.check_right(right):
                    has_right = True
                    break
            if not has_right:
                return False
        return True


class ORMToken(db.Model):
    __tablename__ = "token"
    __table_args__ = (
        db.Index("idx_token_token_value", "token_value", mysql_length=500),
    )
    token_id = db.Column(db.Integer, primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    user = db.relationship("ORMUser", back_populates="tokens")

    token_value = db.Column(db.String(500), unique=True)
    token_created = db.Column(db.DateTime)
    token_valid = db.Column(db.DateTime)
    token_invalidated = db.Column(db.Boolean, nullable=False)
