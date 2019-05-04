# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import uuid

from openstack import resource
from opentelekom import otc_resource

class Vpc(otc_resource.OtcResource, otc_resource.TagMixin):
    resources_key = "vpcs"
    resource_key = "vpc" # top structure is a dict for vpc
    base_path = "/vpcs"

     # capabilities
    allow_create = True
    allow_commit = True
    allow_list = True
    allow_fetch = True
    allow_delete = True

    create_method = 'POST'

    _query_mapping = resource.QueryParameters(
        **resource.TagMixin._tag_query_parameters
    )

    # Properties
    #---- create
    #: name: Name of the vpc. The name is the unique identity of a queue. It
    #: must not exceed 64 bytes in length, and it is limited to US-ASCII
    #: letters, digits, underscores, and hyphens.
    name = resource.Body("name")
    #: cidr: the cidr ip range
    cidr = resource.Body("cidr")
    #: enable_shared_snat: Switch to enable shared SNAT
    enable_shared_snat = resource.Body("enable_shared_snat", type=bool)
    #---- get/list
    #: status: the vpc status
    status = resource.Body("status")
    #: routes: a list of VPC routes
    routes = resource.Body("routes", type=list)
