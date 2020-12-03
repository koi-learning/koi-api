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


class ORMModelParameter(db.Model):
    __tablename__ = "modelparam"
    __table_args__ = (db.Index("idx_modelparam_param_uuid", "param_uuid", mysql_length=16),)

    param_id = db.Column(db.Integer, primary_key=True, unique=True)
    param_uuid = db.Column(db.Binary(16))

    param_name = db.Column(db.String(500))
    param_description = db.Column(db.String(500))
    param_type = db.Column(db.String(500))
    param_constraint = db.Column(db.String(500))

    model_id = db.Column(db.Integer, db.ForeignKey("model.model_id"))
    model = db.relationship("ORMModel", back_populates="params")


class ORMInstanceParameter(db.Model):
    __tablename__ = "instanceparam"
    __table_args__ = (db.Index("idx_instanceparam_param_uuid", "param_uuid", mysql_length=16),)
    param_id = db.Column(db.Integer, primary_key=True, unique=True)
    param_uuid = db.Column(db.Binary(16))

    param_value = db.Column(db.String(500))

    model_param_id = db.Column(db.Integer, db.ForeignKey("modelparam.param_id"))
    model_param: ORMModelParameter = db.relationship("ORMModelParameter")

    instance_id = db.Column(db.Integer, db.ForeignKey("instance.instance_id"))
    instance = db.relationship("ORMInstance", back_populates="params")
