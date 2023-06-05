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

from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy import Integer, String, LargeBinary, Boolean, DateTime, ForeignKey
from koi_api.orm import db


class ORMInstance(db.Model):
    # table name and index for improved access speeds
    __tablename__ = "instance"
    #__table_args__ = (Index("idx_instance_instance_uuid", "instance_uuid", mysql_length=16))

    # the basic fields
    instance_id = mapped_column(Integer, primary_key=True, unique=True)
    instance_name = mapped_column(String(500))
    instance_description = mapped_column(String(500))
    instance_uuid = mapped_column(LargeBinary(16))
    instance_finalized = mapped_column(Boolean)
    instance_last_modified = mapped_column(DateTime, nullable=False)
    instance_samples_last_modified = mapped_column(DateTime, nullable=False)
    instance_etag = mapped_column(String(50))
    instance_samples_etag = mapped_column(String(50))

    instance_merged_id = mapped_column(Integer, ForeignKey("instance.instance_id"))
    instance_merged = relationship("ORMInstance")

    # the associated model
    model_id = mapped_column(Integer, ForeignKey("model.model_id"))
    model = relationship("ORMModel", back_populates="instances")

    # all parameters available to this instance
    params = relationship(
        "ORMInstanceParameter",
        back_populates="instance",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    # all samples available to this instance
    samples = relationship(
        "ORMSample",
        back_populates="instance",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    # granted user access
    granted_users = relationship(
        "ORMAccessInstance",
        back_populates="instance",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    # requests pending for this instance
    label_requests = relationship(
        "ORMLabelRequest",
        back_populates="instance",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    # blob containing the inference data
    inference_data_id = mapped_column(Integer, ForeignKey("inferencedata.data_id"))
    inference_data = relationship("ORMInstanceInferenceData", cascade="all, delete")

    # blob containing the training data
    training_data_id = mapped_column(Integer, ForeignKey("trainingdata.data_id"))
    training_data = relationship("ORMInstanceTrainingData", cascade="all, delete")

    # descriptors assigned to this instance
    instance_descriptors = relationship(
        "ORMInstanceDescriptor",
        back_populates="instance",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    tags = relationship("ORMSampleTag", lazy="dynamic")


class ORMInstanceInferenceData(db.Model):
    __tablename__ = "inferencedata"
    #__table_args__ = (Index("idx_inferencedata_data_uuid", "data_uuid", mysql_length=16))

    data_id = mapped_column(Integer, primary_key=True, unique=True)
    data_uuid = mapped_column(LargeBinary(16))

    data_last_modified = mapped_column(DateTime)
    data_etag = mapped_column(String(50))

    data_file_id = mapped_column(Integer, ForeignKey("file.file_id"))
    file = relationship("ORMFile", cascade="all, delete")

    # data_date_registered = mapped_column(DateTime)
    # data_version = mapped_column(Integer)


class ORMInstanceTrainingData(db.Model):
    __tablename__ = "trainingdata"
    #__table_args__ = (Index("idx_trainingdata_data_uuid", "data_uuid", mysql_length=16))

    data_id = mapped_column(Integer, primary_key=True, unique=True)
    data_uuid = mapped_column(LargeBinary(16))

    data_last_modified = mapped_column(DateTime)
    data_etag = mapped_column(String(50))

    data_file_id = mapped_column(Integer, ForeignKey("file.file_id"))
    file = relationship("ORMFile", cascade="all, delete")

    # data_date_registered = mapped_column(DateTime)
    # data_version = mapped_column(Integer)


class ORMInstanceDescriptor(db.Model):
    __tablename__ = "instancedescriptor"
    #__table_args__ = (Index("idx_intancedescriptor_descriptor_uuid", "descriptor_uuid", mysql_length=16))

    descriptor_id = mapped_column(Integer, primary_key=True, unique=True)
    descriptor_uuid = mapped_column(LargeBinary(16))

    descriptor_key = mapped_column(String(500))

    descriptor_file_id = mapped_column(Integer, ForeignKey("file.file_id"))
    file = relationship("ORMFile", cascade="all, delete")

    descriptor_instance_id = mapped_column(
        Integer, ForeignKey("instance.instance_id")
    )
    instance = relationship("ORMInstance", back_populates="instance_descriptors")
