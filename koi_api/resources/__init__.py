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

from flask_restful import Api

from .user import APIUserCollection, APIUser, APILogin, APILogout
from .model import (
    APIModel,
    APIModelCollection,
    APIModelCode,
    APIModelVisualPlugin,
    APIModelRequestPlugin,
)
from .instance import (
    APIInstance,
    APIInstanceCollection,
    APIInstanceInferenceData,
    APIInstanceTrainingData,
    APIInstanceDescriptor,
    APIInstanceDescriptorCollection,
    APIInstanceDescriptorFile,
)
from .sample import (
    APISample,
    APISampleCollection,
    APISampleData,
    APISampleDataFile,
    APISampleLabelFile,
    APISampleDataCollection,
    APISampleLabel,
    APISampleLabelCollection,
)
from .sample_tags import APISampleTag, APISampleTagCollection
from .instance_tags import APIInstanceTag
from .access import (
    APIGeneralAccess,
    APIGeneralAccessCollection,
    APIInstanceAccess,
    APIInstanceAccessCollection,
    APIModelAccess,
    APIModelAccessCollection,
)
from .role import (
    APIUserRoleGeneral,
    APIUserRoleGeneralCollection,
    APIUserRoleModel,
    APIUserRoleModelCollection,
    APIUserRoleInstance,
    APIUserRoleInstanceCollection,
)
from .parameters import (
    APIInstanceParameter,
    APIInstanceParameterCollection,
    APIModelParameter,
    APIModelParameterCollection,
)
from .label_request import APILabelRequest, APILabelRequestCollection


api = Api()


def init_app(app):

    api.add_resource(APIUser, "/api/user")
    api.add_resource(APIUserCollection, "/api/user/<string:user_uuid>")

    api.add_resource(APILogin, "/api/login")
    api.add_resource(APILogout, "/api/logout")

    api.add_resource(APIModel, "/api/model")
    api.add_resource(APIModelCollection, "/api/model/<string:model_uuid>")
    api.add_resource(APIModelCode, "/api/model/<string:model_uuid>/code")
    api.add_resource(
        APIModelVisualPlugin, "/api/model/<string:model_uuid>/visualplugin"
    )
    api.add_resource(
        APIModelRequestPlugin, "/api/model/<string:model_uuid>/requestplugin"
    )
    api.add_resource(APIModelParameter, "/api/model/<string:model_uuid>/parameter")
    api.add_resource(
        APIModelParameterCollection,
        "/api/model/<string:model_uuid>/parameter/<string:param_uuid>",
    )

    api.add_resource(APIModelAccess, "/api/model/<string:model_uuid>/access")
    api.add_resource(
        APIModelAccessCollection,
        "/api/model/<string:model_uuid>/access/<string:access_uuid>",
    )

    api.add_resource(APIInstance, "/api/model/<string:model_uuid>/instance")
    api.add_resource(
        APIInstanceCollection,
        "/api/model/<string:model_uuid>/instance/<string:instance_uuid>",
    )
    api.add_resource(
        APIInstanceTrainingData,
        "/api/model/<string:model_uuid>/instance/<string:instance_uuid>/training",
    )
    api.add_resource(
        APIInstanceInferenceData,
        "/api/model/<string:model_uuid>/instance/<string:instance_uuid>/inference",
    )
    api.add_resource(
        APIInstanceParameter,
        "/api/model/<string:model_uuid>/instance/<string:instance_uuid>/parameter",
    )
    api.add_resource(
        APIInstanceParameterCollection,
        "/api/model/<string:model_uuid>/instance/<string:instance_uuid>/parameter/<string:param_uuid>",
    )
    api.add_resource(
        APIInstanceDescriptor,
        "/api/model/<string:model_uuid>/instance/<string:instance_uuid>/descriptor",
    )
    api.add_resource(
        APIInstanceDescriptorCollection,
        "/api/model/<string:model_uuid>/instance/<string:instance_uuid>/descriptor/<string:descriptor_uuid>",
    )
    api.add_resource(
        APIInstanceDescriptorFile,
        "/api/model/<string:model_uuid>/instance/<string:instance_uuid>/descriptor/<string:descriptor_uuid>/file",
    )

    api.add_resource(
        APIInstanceTag,
        "/api/model/<string:model_uuid>/instance/<string:instance_uuid>/tags",
    )

    api.add_resource(
        APISample,
        "/api/model/<string:model_uuid>/instance/<string:instance_uuid>/sample",
    )
    api.add_resource(
        APISampleCollection,
        "/api/model/<string:model_uuid>/instance/<string:instance_uuid>/sample/<string:sample_uuid>",
    )

    api.add_resource(
        APISampleTag,
        "/api/model/<string:model_uuid>/instance/<string:instance_uuid>/sample/<string:sample_uuid>/tags",
    )

    api.add_resource(
        APISampleTagCollection,
        "/api/model/<string:model_uuid>/instance/<string:instance_uuid>/sample/<string:sample_uuid>/tags/<string:tag>",
    )

    api.add_resource(
        APISampleData,
        "/api/model/<string:model_uuid>/instance/<string:instance_uuid>/sample/<string:sample_uuid>/data",
    )
    api.add_resource(
        APISampleDataCollection,
        "/api/model/<string:model_uuid>/instance/<string:instance_uuid>/sample/<string:sample_uuid>/data/<string:data_uuid>",
    )
    api.add_resource(
        APISampleDataFile,
        "/api/model/<string:model_uuid>/instance/<string:instance_uuid>/sample/<string:sample_uuid>/data/<string:data_uuid>/file",  # noqa: E501
    )

    api.add_resource(
        APISampleLabel,
        "/api/model/<string:model_uuid>/instance/<string:instance_uuid>/sample/<string:sample_uuid>/label",
    )
    api.add_resource(
        APISampleLabelCollection,
        "/api/model/<string:model_uuid>/instance/<string:instance_uuid>/sample/<string:sample_uuid>/label/<string:label_uuid>",
    )
    api.add_resource(
        APISampleLabelFile,
        "/api/model/<string:model_uuid>/instance/<string:instance_uuid>/sample/<string:sample_uuid>/label/<string:label_uuid>/file",  # noqa: E501
    )

    api.add_resource(
        APIInstanceAccess,
        "/api/model/<string:model_uuid>/instance/<string:instance_uuid>/access",
    )
    api.add_resource(
        APIInstanceAccessCollection,
        "/api/model/<string:model_uuid>/instance/<string:instance_uuid>/access/<string:access_uuid>",
    )

    api.add_resource(
        APILabelRequest,
        "/api/model/<string:model_uuid>/instance/<string:instance_uuid>/label_request",
    )
    api.add_resource(
        APILabelRequestCollection,
        "/api/model/<string:model_uuid>/instance/<string:instance_uuid>/label_request/<string:request_uuid>",
    )

    api.add_resource(APIGeneralAccess, "/api/access")
    api.add_resource(APIGeneralAccessCollection, "/api/access/<string:access_uuid>")

    api.add_resource(APIUserRoleGeneral, "/api/userroles/general")
    api.add_resource(
        APIUserRoleGeneralCollection, "/api/userroles/general/<string:role_uuid>"
    )
    api.add_resource(APIUserRoleModel, "/api/userroles/model")
    api.add_resource(
        APIUserRoleModelCollection, "/api/userroles/model/<string:role_uuid>"
    )
    api.add_resource(APIUserRoleInstance, "/api/userroles/instance")
    api.add_resource(
        APIUserRoleInstanceCollection, "/api/userroles/instance/<string:role_uuid>"
    )

    api.init_app(app)
