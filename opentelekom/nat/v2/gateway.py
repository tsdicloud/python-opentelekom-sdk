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

from openstack import resource
from openstack import utils

from opentelekom import otc_resource


class Service(otc_resource.OtcResource, otc_resource.TagMixin):
    resources_key = "nat_gateways"
    resource_key = "nat_gateway"
    base_path = "/nat_gateways"

     # capabilities
    allow_create = True
    allow_commit = True
    allow_list = True
    allow_fetch = True
    allow_delete = True

    create_method = 'POST'
    
    # note that tenant_id is automatically set by this sdk
    # to model uniform behavior of all services on project
    _query_mapping = resource.QueryParameters(
        "id", 
        "name", 
        "description",
        "admin_state_up",
        "tenant_id",
        "spec",
        "status",
        "created_at",
        vpc_id="router_id",
        subnet_id="internal_network_id",
        **resource.TagMixin._tag_query_parameters
    )

    # Properties
    #--- Create
    #: tenant_id: the project ID is in the body for this service
    #: for ease of use, the field is computed for you
    tenant_id = resource.Computed('tenant_id')
    #: name: the name for the gateway
    name = resource.Body('name')
    #: description: description of the gateway
    description = resource.Body('description')
    #: spec: size specification of the gateway: 1=small, 4=extra large
    spec = resource.Body('spec')
    #: vpc_id=router_id: the vpc id (aka. router id) the gateway belongs to
    #: you have to use vpc peering for using the natting gateway with
    #: multiple VPC
    vpc_id = resource.Body('router_id')
    #: subnet=internal_network_id: the subnet the gateway is located
    subnet_id = resource.Body('internal_network_id')
    #--- get/query
    #: status: state of the gateway (to wait for)
    status = resource.Body('status')
    #: admin_state_up: administration state
    admin_state_up = resource.Body('admin_state_up')
    #: created_at: creation data (format YYYY-MM-DD hh:mm:ss.uuuuuu)

