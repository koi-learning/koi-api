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

SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False

FILEPERSISTENCE_COMPRESS = True
FILEPERSISTENCE_BASE_URI = "./temp/"

FORCE_RESET = False

INITIAL_GENERAL_ROLES = [
    {
        "name": "admin",
        "description": "KOI-Administrator",
        "is_essential": True,
        "priviledges": {
            "grant_access": True,
            "edit_users": True,
            "edit_models": True,
            "edit_roles": True,
        },
    },
    {
        "name": "guest",
        "description": "Guest",
        "is_essential": False,
        "priviledges": {
            "grant_access": False,
            "edit_users": False,
            "edit_models": False,
            "edit_roles": False,
        },
    },
    {
        "name": "worker",
        "description": "Worker",
        "is_essential": False,
        "priviledges": {
            "grant_access": False,
            "edit_users": False,
            "edit_models": False,
            "edit_roles": False,
        },
    },
]
ADDITIONAL_GENERAL_ROLES = []

INITIAL_MODEL_ROLES = [
    {
        "name": "owner",
        "description": "Model owner",
        "is_essential": True,
        "priviledges": {
            "can_see": True,
            "instantiate": True,
            "edit": True,
            "download_code": True,
            "grant_access": True,
        },
    },
    {
        "name": "guest",
        "description": "Model guest",
        "is_essential": False,
        "priviledges": {
            "can_see": True,
            "instantiate": False,
            "edit": False,
            "download_code": False,
            "grant_access": False,
        },
    },
    {
        "name": "worker",
        "description": "Model access for workers",
        "is_essential": False,
        "priviledges": {
            "can_see": True,
            "instantiate": True,
            "edit": False,
            "download_code": True,
            "grant_access": False,
        },
    },
    {
        "name": "user",
        "description": "Model access for users",
        "is_essential": False,
        "priviledges": {
            "can_see": True,
            "instantiate": True,
            "edit": False,
            "download_code": False,
            "grant_access": False,
        },
    },
]

INITIAL_INSTANCE_ROLES = [
    {
        "name": "owner",
        "description": "Instance owner",
        "is_essential": True,
        "priviledges": {
            "can_see": True,
            "add_sample": True,
            "get_training_data": True,
            "get_inference_data": True,
            "edit": True,
            "grant_access": True,
            "request_label": True,
            "response_label": True,
        },
    },
    {
        "name": "guest",
        "description": "Instance guest",
        "is_essential": False,
        "priviledges": {
            "can_see": True,
            "add_sample": False,
            "get_training_data": False,
            "get_inference_data": False,
            "edit": False,
            "grant_access": False,
            "request_label": False,
            "response_label": False,
        },
    },
    {
        "name": "worker",
        "description": "Instance access for workers",
        "is_essential": False,
        "priviledges": {
            "can_see": True,
            "add_sample": True,
            "get_training_data": True,
            "get_inference_data": True,
            "edit": True,
            "grant_access": False,
            "request_label": True,
            "response_label": False,
        },
    },
    {
        "name": "user",
        "description": "Instance access for users",
        "is_essential": False,
        "priviledges": {
            "can_see": True,
            "add_sample": False,
            "get_training_data": False,
            "get_inference_data": True,
            "edit": True,
            "grant_access": False,
            "request_label": False,
            "response_label": True,
        },
    },

]

INITIAL_USERS = [
    {"name": "admin", "password": "admin", "is_essential": True, "general_roles": ["admin"]},
    {"name": "guest", "password": "guest", "is_essential": False, "general_roles": ["guest"]},
    {"name": "worker", "password": "worker", "is_essential": False, "general_roles": ["worker"]},
]
ADDITIONAL_USERS = []
