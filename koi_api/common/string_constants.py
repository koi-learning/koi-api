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

HEADER_TOKEN = "Authorization"


class BODY_GENERAL:
    PAGE_LIMIT = "page_limit"
    PAGE_OFFSET = "page_offset"
    TOKEN = "token"
    EXPIRES = "expires"


class BODY_SAMPLE:
    SAMPLE_UUID = "sample_uuid"
    SAMPLE_FINALIZED = "finalized"
    FILE_PAYLOAD = "payload"
    SAMPLE_DATA = "data"
    SAMPLE_LABEL = "label"
    SAMPLE_DATA_UUID = "data_uuid"
    SAMPLE_LABEL_UUID = "label_uuid"
    SAMPLE_OBSOLETE = "obsolete"
    SAMPLE_CONSUMED = "consumed"
    SAMPLE_LABEL_REQUEST_UUID = "label_request_uuid"
    SAMPLE_KEY = "key"
    SAMPLE_HAS_FILE = "has_file"

    SAMPLE_TAGS_INCLUDE = "inc_tags"
    SAMPLE_TAGS_EXCLUDE = "exc_tags"


class BODY_TAG:
    TAG_NAME = "name"


class BODY_USER:
    USER_NAME = "user_name"
    USER_UUID = "user_uuid"
    USER_ESSENTIAL = "user_essential"
    USER_CREATED = "user_created"
    PASSWORD = "password"


class BODY_INSTANCE:
    INSTANCE_NAME = "instance_name"
    INSTANCE_UUID = "instance_uuid"
    INSTANCE_DESCRIPTION = "instance_description"
    INSTANCE_FINALIZED = "finalized"
    INSTANCE_HAS_TRAINING = "has_training"
    INSTANCE_HAS_INFERENCE = "has_inference"

    INSTANCE_DESCRIPTOR_UUID = "descriptor_uuid"
    INSTANCE_DESCRIPTOR_KEY = "key"
    INSTANCE_DESCRIPTOR_KEY_HAS_FILE = "has_file"
    INSTANCE_COULD_TRAIN = "could_train"
    INSTANCE_LAST_MODIFIED = "last_modified"
    INSTANCE_HAS_REQUESTS = "has_requests"


class BODY_MODEL:
    MODEL_NAME = "model_name"
    MODEL_UUID = "model_uuid"
    MODEL_DESCRIPTION = "model_description"
    MODEL_FINALIZED = "finalized"
    MODEL_INSTANCES = "model_instances"
    MODEL_HAS_CODE = "has_code"
    MODEL_HAS_PLUGIN_VISUAL = "has_visual_plugin"
    MODEL_HAS_PLUGIN_LABEL = "has_label_plugin"
    MODEL_LAST_MODIFIED = "last_modified"


class BODY_ROLE:
    ROLE_UUID = "role_uuid"
    ROLE_NAME = "role_name"
    ROLE_DESCRIPTION = "role_description"

    # rights from general roles
    # obsolete
    # ROLE_ENUM_USERS = "enumerate_users"
    # ROLE_ENUM_MODELS = "enumerate_models"
    # ROLE_ENUM_ACCESS = "enumerate_access"
    # ROLE_ENUM_ROLES = "enumerate_roles"

    ROLE_GRANT_ACCESS = "grant_access"
    ROLE_EDIT_USERS = "edit_users"
    ROLE_EDIT_MODELS = "edit_models"
    ROLE_EDIT_ROLES = "edit_roles"
    ROLE_ESSENTIAL = "is_essential"

    # rights from model roles
    ROLE_SEE_MODEL = "can_see_model"
    ROLE_INSTANTIATE_MODEL = "instantiate_model"
    ROLE_EDIT_MODEL = "edit_model"
    ROLE_DOWNLOAD_CODE = "download_model"
    ROLE_GRANT_ACCESS_MODEL = "grant_access_model"
    # obsolete
    # ROLE_ENUM_ACCESS_MODEL = "enumerate_access_model"
    # ROLE_ENUM_INSTANCES = "enumerate_instances"

    # rights from instance roles
    ROLE_SEE_INSTANCE = "can_see_instance"
    ROLE_ADD_SAMPLE = "add_sample"
    ROLE_GET_TRAINING_DATA = "get_training_data"
    ROLE_GET_INFERENCE_DATA = "get_inference_data"
    ROLE_EDIT_INSTANCE = "edit_instance"
    ROLE_GRANT_ACCESS_INSTANCE = "grant_access_instance"
    # obsolete
    # ROLE_ENUM_ACCESS_INSTANCE = "enumerate_access_instance"
    ROLE_REQUEST_LABEL = "request_labels"
    ROLE_RESPONSE_LABEL = "response_labels"


class BODY_ACCESS:
    ACCESS_UUID = "access_uuid"


class BODY_PARAM:
    PARAM_UUID = "param_uuid"
    PARAM_UUID_VALUE = "value_uuid"
    PARAM_NAME = "name"
    PARAM_DESCRIPTION = "description"
    PARAM_CONSTRAINT = "constraint"
    PARAM_TYPE = "type"
    PARAM_VALUE = "value"
