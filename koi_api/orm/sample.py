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
from sqlalchemy import Integer, String, LargeBinary, ForeignKey, DateTime, Boolean
from koi_api.orm import db


class ORMAssociationTags(db.Model):
    __tablename__ = "tags_association"
    assoc_id = mapped_column(Integer, primary_key=True)
    tag_id = mapped_column(Integer, ForeignKey("sample_tag.tag_id"))
    sample_id = mapped_column(Integer, ForeignKey("sample.sample_id"))
    mergeable = mapped_column(Boolean)

    sample = relationship("ORMSample", back_populates="tags")
    tag = relationship("ORMSampleTag", back_populates="samples")


class ORMSample(db.Model):
    __tablename__ = "sample"
    #__table_args__ = (Index("idx_sample_sample_uuid", "sample_uuid", mysql_length=16))

    sample_id = mapped_column(Integer, primary_key=True, unique=True)
    sample_uuid = mapped_column(LargeBinary(16))
    sample_finalized = mapped_column(Boolean)

    sample_last_modified = mapped_column(DateTime, nullable=False)
    sample_etag = mapped_column(String(50))

    data = relationship(
        "ORMSampleData",
        back_populates="sample",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    label = relationship(
        "ORMSampleLabel",
        back_populates="sample",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    instance_id = mapped_column(Integer, ForeignKey("instance.instance_id"))
    instance = relationship("ORMInstance", back_populates="samples")

    label_requests = relationship(
        "ORMLabelRequest", back_populates="sample", lazy="dynamic"
    )

    tags = relationship("ORMAssociationTags", back_populates="sample", lazy="dynamic")

    def purge_for_merge(self):
        # collect all labels that will be lost ofter merging
        labels_to_pruge = self.label.filter_by(mergeable=False).all()
        for label in labels_to_pruge:
            db.session.delete(label)

        # collect all associations that will be lost after merging
        tags_assoc_to_prune = self.tags.filter_by(mergeable=False).all()
        for tag in tags_assoc_to_prune:
            db.session.delete(tag)
        db.session.commit()

        # drop all samples that have lost all associations
        for tag in self.instance.tags:
            if tag.samples is None:
                db.session.delete(tag)
        db.session.commit()


class ORMSampleData(db.Model):
    __tablename__ = "sampledata"
    #__table_args__ = (Index("idx_sampledata_data_uuid", "data_uuid", mysql_length=16))

    data_id = mapped_column(Integer, primary_key=True, unique=True)
    data_uuid = mapped_column(LargeBinary(16))

    data_last_modified = mapped_column(DateTime, nullable=False)
    data_etag = mapped_column(String(50))

    data_key = mapped_column(String(500))

    sample_id = mapped_column(Integer, ForeignKey("sample.sample_id"))
    sample = relationship("ORMSample", back_populates="data")

    file_id = mapped_column(Integer, ForeignKey("file.file_id"))
    file = relationship("ORMFile", cascade="all, delete")


class ORMSampleLabel(db.Model):
    __tablename__ = "label"
    #__table_args__ = (Index("idx_label_label_uuid", "label_uuid", mysql_length=16),)
    label_id = mapped_column(Integer, primary_key=True, unique=True)
    label_uuid = mapped_column(LargeBinary(16))

    label_last_modified = mapped_column(DateTime, nullable=False)
    label_etag = mapped_column(String(50))

    label_key = mapped_column(String(500))

    sample_id = mapped_column(Integer, ForeignKey("sample.sample_id"))
    sample = relationship("ORMSample", back_populates="label")

    file_id = mapped_column(Integer, ForeignKey("file.file_id"))
    file = relationship("ORMFile", cascade="all, delete")

    mergeable = mapped_column(Boolean)


class ORMSampleTag(db.Model):
    __tablename__ = "sample_tag"

    tag_id = mapped_column(Integer, primary_key=True, unique=True)
    tag_name = mapped_column(String(500))

    instance_id = mapped_column(Integer, ForeignKey("instance.instance_id"))
    instance = relationship("ORMInstance", back_populates="tags")

    samples = relationship("ORMAssociationTags", back_populates="tag")
