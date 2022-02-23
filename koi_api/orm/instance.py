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


class ORMInstance(db.Model):
    # table name and index for improved access speeds
    __tablename__ = "instance"
    __table_args__ = (
        db.Index("idx_instance_instance_uuid", "instance_uuid", mysql_length=16),
    )

    # the basic fields
    instance_id = db.Column(db.Integer, primary_key=True, unique=True)
    instance_name = db.Column(db.String(500))
    instance_description = db.Column(db.String(500))
    instance_uuid = db.Column(db.LargeBinary(16))
    instance_finalized = db.Column(db.Boolean)
    instance_last_modified = db.Column(db.DateTime, nullable=False)
    instance_samples_last_modified = db.Column(db.DateTime, nullable=False)
    instance_etag = db.Column(db.String(50))
    instance_samples_etag = db.Column(db.String(50))

    instance_merged_id = db.Column(db.Integer, db.ForeignKey("instance.instance_id"))
    instance_merged = db.relationship("ORMInstance")

    # the associated model
    model_id = db.Column(db.Integer, db.ForeignKey("model.model_id"))
    model = db.relationship("ORMModel", back_populates="instances")

    # all parameters available to this instance
    params = db.relationship(
        "ORMInstanceParameter",
        back_populates="instance",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    # all samples available to this instance
    samples = db.relationship(
        "ORMSample",
        back_populates="instance",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    # granted user access
    granted_users = db.relationship(
        "ORMAccessInstance",
        back_populates="instance",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    # requests pending for this instance
    label_requests = db.relationship(
        "ORMLabelRequest",
        back_populates="instance",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    # blob containing the inference data
    inference_data_id = db.Column(db.Integer, db.ForeignKey("inferencedata.data_id"))
    inference_data = db.relationship("ORMInstanceInferenceData", cascade="all, delete")

    # blob containing the training data
    training_data_id = db.Column(db.Integer, db.ForeignKey("trainingdata.data_id"))
    training_data = db.relationship("ORMInstanceTrainingData", cascade="all, delete")

    # descriptors assigned to this instance
    instance_descriptors = db.relationship(
        "ORMInstanceDescriptor",
        back_populates="instance",
        lazy="dynamic",
        cascade="all, delete",
    )

    tags = db.relationship("ORMSampleTag", lazy="dynamic")


class ORMInstanceInferenceData(db.Model):
    __tablename__ = "inferencedata"
    __table_args__ = (
        db.Index("idx_inferencedata_data_uuid", "data_uuid", mysql_length=16),
    )
    data_id = db.Column(db.Integer, primary_key=True, unique=True)
    data_uuid = db.Column(db.LargeBinary(16))

    data_last_modified = db.Column(db.DateTime)
    data_etag = db.Column(db.String(50))

    data_file_id = db.Column(db.Integer, db.ForeignKey("file.file_id"))
    file = db.relationship("ORMFile", cascade="all, delete")

    # data_date_registered = db.Column(db.DateTime)
    # data_version = db.Column(db.Integer)


class ORMInstanceTrainingData(db.Model):
    __tablename__ = "trainingdata"
    __table_args__ = (
        db.Index("idx_trainingdata_data_uuid", "data_uuid", mysql_length=16),
    )
    data_id = db.Column(db.Integer, primary_key=True, unique=True)
    data_uuid = db.Column(db.LargeBinary(16))

    data_last_modified = db.Column(db.DateTime)
    data_etag = db.Column(db.String(50))

    data_file_id = db.Column(db.Integer, db.ForeignKey("file.file_id"))
    file = db.relationship("ORMFile", cascade="all, delete")

    # data_date_registered = db.Column(db.DateTime)
    # data_version = db.Column(db.Integer)


class ORMInstanceDescriptor(db.Model):
    __tablename__ = "instancedescriptor"
    __table_args__ = (
        db.Index(
            "idx_intancedescriptor_descriptor_uuid", "descriptor_uuid", mysql_length=16
        ),
    )
    descriptor_id = db.Column(db.Integer, primary_key=True, unique=True)
    descriptor_uuid = db.Column(db.LargeBinary(16))

    descriptor_key = db.Column(db.String(500))

    descriptor_file_id = db.Column(db.Integer, db.ForeignKey("file.file_id"))
    file = db.relationship("ORMFile", cascade="all, delete")

    descriptor_instance_id = db.Column(
        db.Integer, db.ForeignKey("instance.instance_id")
    )
    instance = db.relationship("ORMInstance")
