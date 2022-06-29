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

from koi_api.persistence.core import PersistenceHandler
from sqlalchemy import event
from koi_api.orm.file import ORMFile


class PersistenceSingleton:
    instance = None

    def __init__(self, *arg, **kwargs):
        if not PersistenceSingleton.instance:
            PersistenceSingleton.instance = PersistenceHandler(*arg, **kwargs)

    def __getattr__(self, name):
        return getattr(self.instance, name)


persistence = PersistenceSingleton()


@event.listens_for(ORMFile, "after_delete")
def cascaded_file_remove(mapper, connection, target):
    persistence.remove_file(target)


def init_app(app):
    persistence.init_app(app)
