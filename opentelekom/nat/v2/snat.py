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


class Rule(otc_resource.OtcResource):
    resources_key = "snat_rules"
    resource_key = "snat_rule"
    base_path = "/snat_rules"

     # capabilities
    allow_create = True
    allow_commit = False
    allow_list = True
    allow_fetch = True
    allow_delete = True

    create_method = 'POST'
    
    # note that tenant_id is automatically set by this sdk
    # to model uniform behavior of all services on project
    _query_mapping = resource.QueryParameters(
        "id", 
        "tenant_id",
        "nat_gateway_id",
        "admin_state_up",
        "cidr",
        "status",
        "created_at",
        "admin_state_up",
        subnet_id="network_id", 
        eip_id="floating_ip_id",
        eip="floating_ip_address",
        **resource.TagMixin._tag_query_parameters
    )

    # Properties
    #--- Create
    #: nat_gateway_id: the id of the gateway the rule is for
    nat_gateway_id = resource.Body('nat_gateway_id', alternate_id=True)
    #:  subnet_id=network_id: variant 1 - use a subnet id for the rule
    #: each subnet needs an own EIP then
    subnet_id = resource.Body('network_id')
    #: cidr: variant 2 - use a CIDR for the rule
    cidr = resource.Body('cidr')
    #: source_type: if set to 1, the rule is restricted to cidr specification only
    #: (optional)
    source_type = resource.Body('source_type', type=int)
    #: eip_id=floating_ip_id: the EIP id the SNAT route communicated with the internet
    eip_id = resource.Body('floating_ip_id')
    #--- get/query
    #: status: state of the gateway (to wait for)
    status = resource.Body('status')
    #: admin_state_up: administration state
    admin_state_up = resource.Body('admin_state_up')
    #: created_at: creation data (format YYYY-MM-DD hh:mm:ss.uuuuuu)
    created_at = resource.Body('created_at')
    #: tenant_id / project_id: the id of the project the gateway belongs to
    project_id = resource.Body('tenant_id')
    #: eip=floating_ip_address: the gateway internet IP
    eip = resource.Body('floating_ip_address')



