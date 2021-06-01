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
import pytest
from xprocess import ProcessStarter
import os


@pytest.fixture
def testserver(xprocess):
    class Starter(ProcessStarter):
        pattern = "Running on http://127.0.0.1:5000/"

        cwd = os.getcwd()

        my_env = os.environ.copy()
        my_env["FLASK_APP"] = os.path.join(cwd, "koi_api")
        my_env["KOI_CONFIG"] = "config/debug.py"
        my_env["FLASK_ENV"] = "development"
        my_env["FLASK_DEBUG"] = "1"

        args = ["python", "-m", "flask", "run", "--no-reload"]

        env = my_env

        timeout = 15

    # ensure process is running and return its logfile
    logs = xprocess.ensure("testserver", Starter)

    print(logs)

    conn = ("http://127.0.0.1:5000", "admin", "admin")
    yield conn

    # clean up whole process tree afterwards
    xprocess.getinfo("testserver").terminate()
