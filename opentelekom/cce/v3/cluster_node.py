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
from openstack import exceptions

from openstack import resource
from opentelekom import otc_resource
from opentelekom.cce.v3 import cce_resource

class VolumeSpec(resource.Resource):
    # Properties
    #: Disk Size in GB.
    size = resource.Body('size', type=int)
    #: Volume type: [SATA, SAS, SSD].
    type = resource.Body('volumetype')

class PublicIPSpec(resource.Resource):
    # Properties:
    #: List of IDs for the existing floating ips.
    ids = resource.Body('ids')
    #: Count of the IP addresses to be dynamically created.
    count = resource.Body('count', type=int)
    #: Elastic IP address. Dict of {
    #:     type,
    #:     bandwidth:{
    #:        chargemode, size, sharetype
    #:     }
    #: }.
    floating_ip = resource.Body('eip', type=dict)

class LoginSpec(resource.Resource):
    # Properties:
    #: SSH login key references
    sshKey = resource.Body('sshKey')

class NodeSpec(resource.Resource):
    # Properties
    #: Flavor (mandatory)
    flavor = resource.Body('flavor')
    #: Name of the AZ where the node resides.
    availability_zone = resource.Body('az')
    #: System disk parameters of the node.
    root_volume = resource.Body('rootVolume', type=VolumeSpec)
    #: Data disk parameters of a node. At present, only one data
    #: disk can be configured
    data_volumes = resource.Body('dataVolumes', type=list,
                                 list_type=VolumeSpec)
    #: Parameters for logging in to the node.
    login = resource.Body('login', type=LoginSpec)
    #: Operating System of the node. Currently only EulerOS is supported.
    # FIXME not part of the API yet (or anymore?)
    # os = resource.Body('os', default="")
    #: Elastic IP address parameters of a node.
    public_ip = resource.Body('publicIP', type=PublicIPSpec)
    #: Number of nodes.
    count = resource.Body('count', type=int)

class StatusSpec(resource.Resource):
    # Properties
    #: ID of the VM where the node resides in the ECS.
    instance_id = resource.Body('serverId')
    #: Elastic IP address of a node.
    floating_ip = resource.Body('publicIP')
    #: Private IP address of a node.
    private_ip = resource.Body('privateIP')
    #: Status.
    status = resource.Body('phase')

class ClusterNode(cce_resource.Cce2Resource):

    base_path = '/clusters/%(cluster_id)s/nodes'

    resources_key = "items"

    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    # Properties
    #: Cluster id.
    cluster_id = resource.URI('cluster_id')
    #: Spec
    spec = resource.Body('spec', type=NodeSpec)
    #: Cluster status structure
    status_info = resource.Body('status', type=StatusSpec)    


    def _prepare_request(self, requires_id=True, prepend_key=True,
                         base_path=None):
        '''This is a workaround for the non-properly working default value of the resource framework
           see openstacksdk.compute.v2.server.'''
        self.kind = "Node"
        self.api_version = "v3"

        return super()._prepare_request(requires_id=requires_id,
            prepend_key=prepend_key, base_path=base_path)

