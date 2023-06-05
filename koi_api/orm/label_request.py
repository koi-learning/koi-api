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
from sqlalchemy import Integer, LargeBinary, Boolean, ForeignKey
from koi_api.orm import db


class ORMLabelRequest(db.Model):
    __tablename__ = "labelrequest"
    # __table_args__ = (Index("idx_labelrequest_label_request_uuid", "label_request_uuid", mysql_length=16),)
    label_request_id = mapped_column(Integer, primary_key=True, unique=True)
    label_request_uuid = mapped_column(LargeBinary(16))

    obsolete = mapped_column(Boolean)

    label_request_sample_id = mapped_column(Integer, ForeignKey("sample.sample_id"))

    sample = relationship("ORMSample", back_populates="label_requests")

    label_request_instance_id = mapped_column(
        Integer, ForeignKey("instance.instance_id")
    )

    instance = relationship("ORMInstance", back_populates="label_requests")
