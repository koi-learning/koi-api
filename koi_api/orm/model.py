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

from koi_api.orm.parameters import ORMModelParameter
from typing import Iterable
from ..orm import db


class ORMModel(db.Model):
    # table name and index
    __tablename__ = "model"
    __table_args__ = (db.Index("idx_model_model_uuid", "model_uuid", mysql_length=16),)

    # basic fields
    model_id = db.Column(db.Integer, primary_key=True, unique=True)
    model_name = db.Column(db.String(500))
    model_description = db.Column(db.String(500))
    model_uuid = db.Column(db.Binary(16))
    model_finalized = db.Column(db.Boolean)
    model_last_modified = db.Column(db.DateTime, nullable=False)
    model_instances_last_modified = db.Column(db.DateTime, nullable=False)

    # blob containing the model code
    code_id = db.Column(db.Integer, db.ForeignKey("modelcode.code_id"))
    code = db.relationship("ORMModelCode", cascade="all, delete")

    # blob containing the visual plugin
    visual_plugin_id = db.Column(db.Integer, db.ForeignKey("visualplugin.plugin_id"))
    visual_plugin = db.relationship("ORMModelVisualPlugin", cascade="all, delete")

    # blob containing the request_plugin
    request_plugin_id = db.Column(db.Integer, db.ForeignKey("requestplugin.plugin_id"))
    request_plugin = db.relationship(
        "ORMModelLabelRequestPlugin", cascade="all, delete"
    )

    # the instances running this model
    instances = db.relationship(
        "ORMInstance", back_populates="model", lazy="dynamic", cascade="all, delete-orphan"
    )

    # model parameters
    params: Iterable[ORMModelParameter] = db.relationship("ORMModelParameter", lazy="dynamic", cascade="all, delete")

    # access granted to users
    granted_users = db.relationship(
        "ORMAccessModel", back_populates="model", lazy="dynamic", cascade="all, delete"
    )


class ORMModelCode(db.Model):
    __tablename__ = "modelcode"
    code_id = db.Column(db.Integer(), primary_key=True, unique=True)

    file_id = db.Column(db.Integer, db.ForeignKey("file.file_id"))
    file = db.relationship("ORMFile", cascade="all, delete")


class ORMModelVisualPlugin(db.Model):
    __tablename__ = "visualplugin"
    plugin_id = db.Column(db.Integer, primary_key=True, unique=True)

    file_id = db.Column(db.Integer, db.ForeignKey("file.file_id"))
    file = db.relationship("ORMFile", cascade="all, delete")


class ORMModelLabelRequestPlugin(db.Model):
    __tablename__ = "requestplugin"
    plugin_id = db.Column(db.Integer, primary_key=True, unique=True)

    file_id = db.Column(db.Integer, db.ForeignKey("file.file_id"))
    file = db.relationship("ORMFile", cascade="all, delete")
