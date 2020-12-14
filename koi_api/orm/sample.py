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


association_table = db.Table(
    "association_tags",
    db.Model.metadata,
    db.Column("sample_id", db.Integer, db.ForeignKey("sample.sample_id")),
    db.Column("tag_id", db.Integer, db.ForeignKey("sample_tag.tag_id")),
)


class ORMSample(db.Model):
    __tablename__ = "sample"
    __table_args__ = (
        db.Index("idx_sample_sample_uuid", "sample_uuid", mysql_length=16),
    )
    sample_id = db.Column(db.Integer, primary_key=True, unique=True)
    sample_uuid = db.Column(db.Binary(16))
    sample_finalized = db.Column(db.Boolean)

    sample_last_modified = db.Column(db.DateTime, nullable=False)

    data = db.relationship(
        "ORMSampleData",
        back_populates="sample",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    label = db.relationship(
        "ORMSampleLabel",
        back_populates="sample",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    instance_id = db.Column(db.Integer, db.ForeignKey("instance.instance_id"))
    instance = db.relationship("ORMInstance", back_populates="samples")

    label_requests = db.relationship(
        "ORMLabelRequest", back_populates="sample", lazy="dynamic"
    )

    tags = db.relationship("ORMSampleTag", secondary=association_table)


class ORMSampleData(db.Model):
    __tablename__ = "sampledata"
    __table_args__ = (
        db.Index("idx_sampledata_data_uuid", "data_uuid", mysql_length=16),
    )
    data_id = db.Column(db.Integer, primary_key=True, unique=True)
    data_uuid = db.Column(db.Binary(16))

    data_last_modified = db.Column(db.DateTime, nullable=False)

    data_key = db.Column(db.String(500))

    sample_id = db.Column(db.Integer, db.ForeignKey("sample.sample_id"))
    sample = db.relationship("ORMSample", back_populates="data")

    file_id = db.Column(db.Integer, db.ForeignKey("file.file_id"))
    file = db.relationship("ORMFile", cascade="all, delete")


class ORMSampleLabel(db.Model):
    __tablename__ = "label"
    __table_args__ = (db.Index("idx_label_label_uuid", "label_uuid", mysql_length=16),)
    label_id = db.Column(db.Integer, primary_key=True, unique=True)
    label_uuid = db.Column(db.Binary(16))

    label_last_modified = db.Column(db.DateTime, nullable=False)

    label_key = db.Column(db.String(500))

    sample_id = db.Column(db.Integer, db.ForeignKey("sample.sample_id"))
    sample = db.relationship("ORMSample", back_populates="label")

    file_id = db.Column(db.Integer, db.ForeignKey("file.file_id"))
    file = db.relationship("ORMFile", cascade="all, delete")


class ORMSampleTag(db.Model):
    __tablename__ = "sample_tag"

    tag_id = db.Column(db.Integer, primary_key=True, unique=True)
    tag_name = db.Column(db.String(500), unique=True)

    instance_id = db.Column(db.Integer, db.ForeignKey("instance.instance_id"))
    instance = db.relationship("ORMInstance", back_populates="tags")
