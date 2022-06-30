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

from koi_api.resources.base import BaseResource
from koi_api.common.return_codes import ERR_FORB, SUCCESS


class APIHealth(BaseResource):
    def get(self):
        return SUCCESS()

    def put(self):
        """
        This function is not allowed.
        """
        return ERR_FORB()

    def post(self):
        """
        This function is not allowed.
        """
        return ERR_FORB()

    def delete(self):
        """
        This function is not allowed.
        """
        return ERR_FORB()
