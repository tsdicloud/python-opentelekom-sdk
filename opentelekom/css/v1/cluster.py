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

class Cluster(otc_resource.OtcResource, otc_resource.TagMixin):
    resources_key = "clusters"
    resource_key = "cluster"
    base_path = "/clusters"

     # capabilities
    allow_create = True
    allow_commit = False
    allow_list = True
    allow_fetch = True
    allow_delete = True

    create_method = 'POST'

    _query_mapping = resource.QueryParameters(
        **resource.TagMixin._tag_query_parameters
    )

    # Properties
    #: name: Name of the vpc. The name is the unique identity of a queue. It
    #: must not exceed 64 bytes in length, and it is limited to US-ASCII
    #: letters, digits, underscores, and hyphens.
    name = resource.Body("name")
    #: instance: the instance description for all cluster members
    instance = resource.Body("instance", type=dict)
    #: datastore: Datastore description object (optional)
    datastore = resource.Body("datastore", type=dict)
    #: instanceNum: size of the cluster
    instanceNum = resource.Body("instanceNum", type=int)
    #: diskEncryption: Disk encryption object with required references
    #: and options for encryption
    diskEncryption = resource.Body("diskEncryption", type=dict)
    #: httpsEncryption: enable/disable https (optional, default True)
    httpsEnable = resource.Body("httpsEnable") # value true or false, but NOT a bool
    #: -- get/fetch
    #: status: cluster status
    status = resource.Body("status")
    #: created: creation timestamp
    created = resource.Body("created")
    #: updated: last update timestamp
    updated = resource.Body("updated")
    #: endpoint: usr access point from Internet (IP)
    endpoint = resource.Body("endpoint")
    #: endpoint: usr access point from Internet (IP)
    diskEncrypted = resource.Body("diskEncrypted", type=bool)
    #: cmkId: key the cluster is encrpyted with
    cmkId = resource.Body("cmkId")
    #: clusters: details abut the cluster nodes
    clusters = resource.Body("clusters", type=list)
    #: actionProgess: details about the creation process progress
    actionProgress = resource.Body("actionProgress", type=dict)
    #: actions: current cluster behavior
    actions = resource.Body("actions", type=list)
    #: vpcId: vpc of the cluster location
    vpcId = resource.Body("vpcId")
    #: netId: subnet of the cluster location
    subnetId = resource.Body("subnetId")
    #: securityGroupId: the security group protevting the cluster
    securityGroupId = resource.Body("securityGroupId")
