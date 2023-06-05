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

from sqlalchemy.orm import relationship, mapped_column
from sqlalchemy import Integer, String, DateTime, Boolean, LargeBinary, ForeignKey
from koi_api.orm import db


class ORMModel(db.Model):
    # table name and index
    __tablename__ = "model"
    #__table_args__ = (Index("idx_model_model_uuid", "model_uuid", mysql_length=16),)

    # basic fields
    model_id = mapped_column(Integer, primary_key=True, unique=True)
    model_name = mapped_column(String(500))
    model_description = mapped_column(String(500))
    model_uuid = mapped_column(LargeBinary(16), index=True)
    model_finalized = mapped_column(Boolean)
    model_last_modified = mapped_column(DateTime, nullable=False)
    model_instances_last_modified = mapped_column(DateTime, nullable=False)
    model_etag = mapped_column(String(50))
    model_instances_etag = mapped_column(String(50))

    # blob containing the model code
    code_id = mapped_column(Integer, ForeignKey("modelcode.code_id"))
    code = relationship("ORMModelCode", cascade="all, delete")

    # blob containing the visual plugin
    visual_plugin_id = mapped_column(Integer, ForeignKey("visualplugin.plugin_id"))
    visual_plugin = relationship("ORMModelVisualPlugin", cascade="all, delete")

    # blob containing the request_plugin
    request_plugin_id = mapped_column(Integer, ForeignKey("requestplugin.plugin_id"))
    request_plugin = relationship(
        "ORMModelLabelRequestPlugin", cascade="all, delete"
    )

    # the instances running this model
    instances = relationship(
        "ORMInstance", back_populates="model", lazy="dynamic", cascade="all, delete-orphan"
    )

    # model parameters
    params = relationship("ORMModelParameter", cascade="all, delete")

    # access granted to users
    granted_users = relationship(
        "ORMAccessModel", back_populates="model", lazy="dynamic", cascade="all, delete"
    )


class ORMModelCode(db.Model):
    __tablename__ = "modelcode"
    code_id = mapped_column(Integer(), primary_key=True, unique=True)

    file_id = mapped_column(Integer, ForeignKey("file.file_id"))
    file = relationship("ORMFile", cascade="all, delete")


class ORMModelVisualPlugin(db.Model):
    __tablename__ = "visualplugin"
    plugin_id = mapped_column(Integer, primary_key=True, unique=True)

    file_id = mapped_column(Integer, ForeignKey("file.file_id"))
    file = relationship("ORMFile", cascade="all, delete")


class ORMModelLabelRequestPlugin(db.Model):
    __tablename__ = "requestplugin"
    plugin_id = mapped_column(Integer, primary_key=True, unique=True)

    file_id = mapped_column(Integer, ForeignKey("file.file_id"))
    file = relationship("ORMFile", cascade="all, delete")
