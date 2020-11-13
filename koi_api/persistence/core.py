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
from ..orm.file import ORMFile
import gzip
from uuid import uuid1
import os


class PersistenceHandler:
    def __init__(self):
        self._base_path = None
        self._compress = None

    def init_app(self, app):
        base_path = app.config["FILEPERSISTENCE_BASE_URI"]
        compress = app.config["FILEPERSISTENCE_COMPRESS"]
        self._base_path = base_path
        self._compress = compress
        directory = os.path.dirname(self._base_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

    def get_file(self, file: ORMFile):
        path = os.path.join(self._base_path, file.file_url)

        f = gzip.open(path, mode="rb", compresslevel=9)
        data = f.read()
        f.close()

        return data

    def store_file(self, data):
        newFile = ORMFile()

        newPath = uuid1().hex + ".dat"
        newFile.file_url = newPath

        path = os.path.join(self._base_path, newPath)
        f = gzip.open(path, mode="wb", compresslevel=9)
        f.write(data)
        f.close()

        db.session.add(newFile)
        db.session.commit()

        return newFile

    def remove_file(self, file: ORMFile):
        os.remove(os.path.join(self._base_path, file.file_url))
