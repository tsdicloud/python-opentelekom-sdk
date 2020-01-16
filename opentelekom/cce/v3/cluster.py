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
# import six
from openstack import exceptions

from openstack import resource
from opentelekom import otc_resource
from opentelekom.cce.v3 import cce_resource


class HostNetworkSpec(otc_resource.OtcSubResource):
    # Properties
    #: ID of the high-speed network that is used to create a bare metal node.
    highway_subnet = resource.Body('highwaySubnet')
    #: ID of the subnet that is used to create a node.
    subnet = resource.Body('subnet')
    #: ID of the VPC that is used to create a node.
    vpc = resource.Body('vpc')

class ContainerNetworkSpec(otc_resource.OtcSubResource):
    # Properties
    #: internal kube network type; one of overlay_l2, 
    #: underlay_ipvlan, vpc-router
    mode = resource.Body('mode')
    #: IP range of internal addresses in the cluster as CIDR
    cidr = resource.Body('cidr')

class AuthenticationProxySpec(otc_resource.OtcSubResource):
    #: ca certificate of the authenticating proxy, base64 encoded
    ca = resource.Body('ca')

class AuthenticationSpec(otc_resource.OtcSubResource):
    # Properties
    #: type of authentication for the new cluster:
    #: values: x509 authenticating_proxy
    mode = resource.Body('mode')
    #: values for the authentication proxy
    authenticating_proxy = resource.Body('authenticatingProxy', type=AuthenticationProxySpec)


class ClusterSpec(otc_resource.OtcSubResource):
    #: Cluster type.
    type = resource.Body('type')
    #: Cluster flavors.
    flavor = resource.Body('flavor')
    #: Cluster version ['v1.9.2-r2', 'v1.11.3-r1'].
    version = resource.Body('version')
    #: Cluster description.
    description = resource.Body('description')
    #: Node network parameters.
    host_network = resource.Body('hostNetwork', type=HostNetworkSpec)
    #: Container network parameters.
    container_network = resource.Body('containerNetwork', type=ContainerNetworkSpec)
    #: Billing mode of the cluster. Currently, only pay-per-use is supported.
    billing = resource.Body('billingMode', type=int)
    #: Extended parameters.
    extended_param = resource.Body('extendParam', type=dict)
    # pure return values
    authentication = resource.Body('authentication', type=AuthenticationSpec)


class StatusSpec(otc_resource.OtcSubResource):
    # Properties
    #: Cluster status.
    status = resource.Body('phase')
    #: Access address of the kube-apiserver in the cluster.
    endpoints = resource.Body('endpoints', type=dict)


class Cluster(cce_resource.Cce2Resource):
    base_path = '/clusters'

    resources_key = "items"

    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    # Properties
    #: specification
    spec = resource.Body('spec', type=ClusterSpec)
    #: status
    status_info = resource.Body('status', type=StatusSpec)

    def _prepare_request(self, requires_id=True, prepend_key=True,
                         base_path=None):
        '''This is a workaround for the non-properly working default value of
           the resource framework see openstacksdk.compute.v2.server.'''
        self.kind = "Cluster"
        self.api_version = "v3"
    
        return super()._prepare_request(requires_id=requires_id,
            prepend_key=prepend_key, base_path=base_path)
 

    def fetch(self, session, requires_id=True,
         base_path=None, error_message=None, **params):
         """ Work around fetch exception when getting cluster state
             during cluster deletion"""
         previous_state = self
         try:
             return super().fetch(session=session, requires_id=requires_id,
                 base_path=base_path, error_message=error_message, **params)
         except exceptions.HttpException as internal:
             if "E.CFE.5000102" in internal.response.text: 
                 return previous_state
             else:
                 raise internal

