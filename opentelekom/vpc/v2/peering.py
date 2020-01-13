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
from openstack import utils

from opentelekom import otc_resource


class VpcInfoSpec(otc_resource.OtcSubResource):
    #: vpc_id: the vpc id for one of the peering partners
    vpc_id = resource.Body("vpc_id")
    #---- get/list
    #: project_id: vpc endpoint is not dependent on project_id, so
    #: it has to be in the request body or get parameters
    tenant_id = resource.Body("tenant_id")


class Peering(otc_resource.OtcResource, otc_resource.TagMixin):
    """ FIXME: Note that peerings can only operate on the artificial endpoint peervpc """

    resources_key = "peerings"
    resource_key = "peering" # top structure is a dict for vpc
    base_path = "/vpc/peerings"

     # capabilities
    allow_create = True
    allow_commit = True
    allow_list = True
    allow_fetch = True
    allow_delete = True

    create_method = 'POST'

    _query_mapping = resource.QueryParameters(
        "name", "status", "vpc_id", project_id="tenant_id",
        **resource.TagMixin._tag_query_parameters
    )

    # Properties
    #---- create
    #: name: Name of the peering, not longer than 64 characters.
    name = resource.Body("name")
    #: request_vpc_info: the requesting peering partner info 
    request_vpc_info = resource.Body("request_vpc_info", type=VpcInfoSpec)
    #: accept_vpc_info: the requesting peering partner info 
    accept_vpc_info = resource.Body("accept_vpc_info", type=VpcInfoSpec)
    #---- get/list
    #: status: the peering status
    status = resource.Body("status")

    def _action(self, session, action):
        """Perform stack actions"""
        url = utils.urljoin(self.base_path, self._get_id(self), action)
        resp = session.put(url)
        return resp.json()

    def accept(self, session):
        session = self._get_session(session)
        return self._action(session, 'accept')

    def reject(self, session):
        session = self._get_session(session)
        return self._action(session, 'reject')

class PeeringRoute(otc_resource.OtcResource):
    resources_key = "routes"
    resource_key = "route" # top structure is a dict for vpc
    base_path = "/routes"

     # capabilities
    allow_create = True
    allow_commit = False
    allow_list = True
    allow_fetch = True
    allow_delete = True

    create_method = 'POST'

    _query_mapping = resource.QueryParameters(
        "destination", "type", "vpc_id", 
        project_id="tenant_id",
        **resource.TagMixin._tag_query_parameters
    )

    # Properties
    #---- create
    #: vpc_id: the vpc id for one of the peering partners
    vpc_id = resource.Body("vpc_id")
    #: destination: Destination CIDR block
    destination = resource.Body("destination")
    #: nexthop: Addtional hop CIDR, optional
    nexthop = resource.Body("nexthop")
    #: type: type of the route, only "peering" at the moment
    type = resource.Body("type")
    #---- get/list
    #: project_id: vpc endpoint is not dependent on project_id, so
    #: it has to be in the request body or get parameters
    project_id = resource.Body("tenant_id")

    def _prepare_request(self, requires_id=True, prepend_key=True,
                         base_path=None):
        '''This is a workaround for the non-properly working default value of
        the resource framework see openstacksdk.compute.v2.server.'''
        self.type = "peering"
        return super()._prepare_request(requires_id=requires_id,
                                prepend_key=prepend_key, base_path=base_path)
