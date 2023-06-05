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
from sqlalchemy import Integer, String, LargeBinary, ForeignKey
from koi_api.orm import db


class ORMModelParameter(db.Model):
    __tablename__ = "modelparam"
    # __table_args__ = (Index("idx_modelparam_param_uuid", "param_uuid", mysql_length=16),)

    param_id = mapped_column(Integer, primary_key=True, unique=True)
    param_uuid = mapped_column(LargeBinary(16))

    param_name = mapped_column(String(500))
    param_description = mapped_column(String(500))
    param_type = mapped_column(String(500))
    param_constraint = mapped_column(String(500))

    model_id = mapped_column(Integer, ForeignKey("model.model_id"))
    model = relationship("ORMModel", back_populates="params")


class ORMInstanceParameter(db.Model):
    __tablename__ = "instanceparam"
    # __table_args__ = (Index("idx_instanceparam_param_uuid", "param_uuid", mysql_length=16),)
    param_id = mapped_column(Integer, primary_key=True, unique=True)
    param_uuid = mapped_column(LargeBinary(16))

    param_value = mapped_column(String(500))

    model_param_id = mapped_column(Integer, ForeignKey("modelparam.param_id"))
    model_param = relationship("ORMModelParameter")

    instance_id = mapped_column(Integer, ForeignKey("instance.instance_id"))
    instance = relationship("ORMInstance", back_populates="params")
