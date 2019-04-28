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


class Subnet(resource.Resource):
    resources_key = "subnets"
    resource_key = "subnet" # top structure is a dict for subnet
    base_path = "/subnets"

     # capabilities
    allow_create = True
    allow_commit = True
    allow_list = True
    allow_fetch = True
    allow_delete = False  # see below

    create_method = 'POST'

    # required for update
    parent_vpc_id = resource.URI("parent_vpc_id")

    # Properties
    #: name: Name of the vpc. The name is the unique identity of a queue. It
    #: must not exceed 64 bytes in length, and it is limited to US-ASCII
    #: letters, digits, underscores, and hyphens.
    name = resource.Body("name")
    #: cidr: the cidr ip range, subrange of the vpc 
    cidr = resource.Body("cidr")
    #: gateway_ip: ip of the subnet gateway (usually .1)
    gateway_ip = resource.Body("gateway_ip")    
    #: enable_shared_snat: Switch to enable shared SNAT (optional)
    dhcp_enable = resource.Body("dhcp_enable", type=bool)
    #: primary_dns: IP address of a DNS servers (optional)
    primary_dns = resource.Body("primary_dns")
    #: secondary_dns: IP address of a DNS servers (optional)
    secondary_dns = resource.Body("secondary_dns")
    #: dnsList: alternative DNS server list is primary/secondary is not enough (optional)
    dnsList = resource.Body("dnsList", type=list, default=["100.125.4.25", "8.8.8.8"], coerce_to_default=True)
    #: availability_zone: availability_zone for the subnet(backward compatibility only)
    availability_zone = resource.Body("availability_zone")
    #: vpc_id: the vpc the subnet belongs to
    vpc_id = resource.Body("vpc_id")
    #: extra_dhcp_opts: additional dhcp behavior options
    extra_dhcp_opts = resource.Body("extra_dhcp_opts", type=list)
    #----
    #: status: the status of the subnet to observe
    status = resource.Body("status")
 

class VpcSubnetAssoc(resource.Resource):
    """A special resource to handle the abnormal DELETE case for subnets on VPC
    """
    resources_key = "subnets"
    base_path = "/vpcs/%(vpc_id)s/subnets"

     # capabilities
    allow_list = True
    allow_delete = True

    # Properties
    #: name: Name of the vpc. The name is the unique identity of a queue. It
    #: must not exceed 64 bytes in length, and it is limited to US-ASCII
    #: letters, digits, underscores, and hyphens.
    vpc_id = resource.URI("vpc_id")
    #: the subnet id to address
    id = resource.Body("id")
 