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

from sqlalchemy.orm import mapped_column
from sqlalchemy import Integer, String
from koi_api.orm import db


class ORMFile(db.Model):
    __tablename__ = "file"
    file_id = mapped_column(Integer, primary_key=True, unique=True)
    file_url = mapped_column(String(500))
