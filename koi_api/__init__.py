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

from flask import Flask
from flask_cors import CORS


def create_app():
    app = Flask(__name__)

    app.config.from_pyfile("config/base.py")
    app.config.from_envvar("KOI_CONFIG", silent=True)
    app.config.from_prefixed_env(prefix="KOI")

    CORS(app)

    from . import orm, resources, persistence
    from datetime import datetime

    persistence.init_app(app)

    resources.init_app(app)

    orm.init_app(app)

    with app.app_context():
        if app.config["FORCE_RESET"] is True:
            orm.db.drop_all()

        orm.db.create_all()
        from uuid import uuid1

        # pair the config keys with their appropriate ORM-constructors
        roles = [
            ("INITIAL_INSTANCE_ROLES", orm.role.ORMUserRoleInstance),
            ("INITIAL_MODEL_ROLES", orm.role.ORMUserRoleModel),
            ("INITIAL_GENERAL_ROLES", orm.role.ORMUserRoleGeneral),
            ("ADDITIONAL_GENERAL_ROLES", orm.role.ORMUserRoleGeneral),
        ]

        # add all initial roles if not present
        for role_type, role_object in roles:
            if role_type in app.config:
                for role in app.config[role_type]:
                    db_role = role_object.query.filter_by(role_name=role["name"]).one_or_none()
                    if db_role is None:
                        # create a new role
                        db_role = role_object()
                        db_role.role_uuid = uuid1().bytes
                        db_role.role_name = role["name"]
                        db_role.role_description = role["description"]
                        db_role.is_essential = role["is_essential"]
                        for priv, value in role["priviledges"].items():
                            setattr(db_role, priv, value)
                        orm.db.session.add(db_role)
                    else:
                        # update if we already know this role
                        # do not update the uuid and the name
                        db_role.role_description = role["description"]
                        db_role.is_essential = role["is_essential"]
                        for priv, value in role["priviledges"].items():
                            setattr(db_role, priv, value)
        orm.db.session.commit()

        for user_type in ["INITIAL_USERS", "ADDITIONAL_USERS"]:
            if user_type in app.config:
                for user in app.config[user_type]:
                    db_user = orm.user.ORMUser.query.filter_by(user_name=user["name"]).one_or_none()
                    if db_user is None:
                        # create a new user but do not edit existing users
                        db_user = orm.user.ORMUser()
                        db_user.user_name = user["name"]
                        db_user.user_uuid = uuid1().bytes
                        db_user.user_hash = resources.user.hash_password(user["password"])
                        db_user.user_created = datetime.utcnow()
                        db_user.is_essential = user["is_essential"]
                        orm.db.session.add(db_user)
                        orm.db.session.commit()

                    # for each role assigned to this user, add it if not present
                    for role_name in user["general_roles"]:
                        db_role = orm.role.ORMUserRoleGeneral.query.filter_by(role_name=role_name).one_or_none()
                        if db_role is None:
                            # something is very wrong -> we do not know this role
                            continue

                        user_role_assoc = orm.access.ORMAccessGeneral.query.filter_by(
                            user_id=db_user.user_id, role_id=db_role.role_id
                        ).one_or_none()
                        if user_role_assoc is None:
                            # create a new association
                            user_role_assoc = orm.access.ORMAccessGeneral()
                            user_role_assoc.user_id = db_user.user_id
                            user_role_assoc.role_id = db_role.role_id
                            user_role_assoc.access_uuid = uuid1().bytes
                            orm.db.session.add(user_role_assoc)
        orm.db.session.commit()

    return app
