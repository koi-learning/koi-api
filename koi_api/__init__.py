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

    CORS(app)

    from . import orm, resources, persistence

    persistence.init_app(app)

    resources.init_app(app)

    orm.init_app(app)

    with app.app_context():
        if app.config["FORCE_RESET"] is True:
            orm.db.drop_all()

        orm.db.create_all()
        from uuid import uuid1

        num_admin_roles = orm.access.ORMAccessGeneral.query.count()
        if num_admin_roles == 0:
            admin_role = orm.role.ORMUserRoleGeneral()
            admin_role.role_name = "admin"
            admin_role.role_description = "default super-user"
            admin_role.role_uuid = uuid1().bytes
            admin_role.is_essential = True
            admin_role.enumerate_users = True
            admin_role.enumerate_models = True
            admin_role.enumerate_access = True
            admin_role.enumerate_roles = True
            admin_role.grant_access = True
            admin_role.edit_users = True
            admin_role.edit_models = True
            admin_role.edit_roles = True

            orm.db.session.add(admin_role)

        num_instance_owner_role = orm.role.ORMUserRoleInstance.query.count()
        if num_instance_owner_role == 0:
            instance_owner_role = orm.role.ORMUserRoleInstance()
            instance_owner_role.role_uuid = uuid1().bytes
            instance_owner_role.role_name = "owner"
            instance_owner_role.role_description = "instance owner"
            instance_owner_role.can_see = True
            instance_owner_role.add_sample = True
            instance_owner_role.get_training_data = True
            instance_owner_role.get_inference_data = True
            instance_owner_role.edit = True
            instance_owner_role.grant_access = True
            instance_owner_role.enumerate_access = True
            instance_owner_role.is_essential = True
            instance_owner_role.request_label = True
            instance_owner_role.response_label = True

            orm.db.session.add(instance_owner_role)

        num_model_owner_role = orm.role.ORMUserRoleModel.query.count()
        if num_model_owner_role == 0:
            model_owner_role = orm.role.ORMUserRoleModel()
            model_owner_role.role_uuid = uuid1().bytes
            model_owner_role.role_name = "owner"
            model_owner_role.role_description = "model owner"
            model_owner_role.is_essential = True

            model_owner_role.can_see = True
            model_owner_role.instantiate = True
            model_owner_role.edit = True
            model_owner_role.download_code = True
            model_owner_role.grant_access = True
            model_owner_role.enumerate_access = True
            model_owner_role.enumerate_instances = True

            orm.db.session.add(model_owner_role)

        orm.db.session.commit()

        admin = orm.user.ORMUser.query.first()
        if admin is None:
            from datetime import datetime

            admin = orm.user.ORMUser()
            admin.user_name = "admin"
            admin.user_hash = resources.user.hash_password("admin")
            admin.user_created = datetime.now()
            admin.user_uuid = uuid1().bytes
            admin.is_essential = True
            orm.db.session.add(admin)
            orm.db.session.commit()

            admin_role = orm.role.ORMUserRoleGeneral.query.first()

            new_access = orm.access.ORMAccessGeneral()
            new_access.role_id = admin_role.role_id
            new_access.user_id = admin.user_id
            new_access.access_uuid = uuid1().bytes

            orm.db.session.add(new_access)
            orm.db.session.commit()

    return app
