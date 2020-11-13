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

from flask import Response, json
from datetime import datetime, timedelta


class ReturnCode:
    def __init__(self, message="", code=200):
        self.m = message
        self.c = code

    def __call__(self, body=None, header=None, last_modified=None, valid_seconds=15):
        rsp = None
        if body is None:
            rsp = Response(json.dumps(self.m), self.c, header, mimetype="application/json")
        else:
            rsp = Response(json.dumps(body), self.c, header, mimetype="application/json")

        if last_modified is not None:
            then = datetime.utcnow() + timedelta(seconds=valid_seconds)
            rsp.expires = then
            rsp.last_modified = last_modified
        return rsp


SUCCESS = ReturnCode("")
ERR_BADR = ReturnCode("", 400)
ERR_AUTH = ReturnCode("not authenticated", 401)
ERR_NOFO = ReturnCode("resource not found", 404)
ERR_FORB = ReturnCode("action is forbidden", 405)
ERR_TAKE = ReturnCode("resource is taken", 409)
