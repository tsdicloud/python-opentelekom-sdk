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

class ClusterCertSpec(otc_resource.OtcSubResource):
    # Properties
    #: server: url endpoint the certificate is for
    server = resource.Body('server')
    #: certificate-authority-data: root certificate to trust
    ca_cert = resource.Body('certificate-authority-data')

class ClusterCertListSpec(otc_resource.OtcSubResource):
    # Properties
    name = resource.Body('name')
    #: Cluster information.
    cluster = resource.Body('cluster', type=ClusterCertSpec)

class UserSpec(otc_resource.OtcSubResource):
    # Properties
    #: client certificate for the user
    cert = resource.Body('client-certificate-data')
    #: client private key for the user
    key = resource.Body('client-key-data')

class UserListSpec(otc_resource.OtcSubResource):
    # Properties
    name = resource.Body('name')
    #: Cluster information.
    user = resource.Body('user', type=UserSpec)

class ContextSpec(otc_resource.OtcSubResource):
    # Properties
    #: Cluster name
    cluster = resource.Body('cluster')
    #: User name
    user = resource.Body('users')

class ContextListSpec(otc_resource.OtcSubResource):
    # Properties
    name = resource.Body('name')
    #: Context information.
    contexts = resource.Body('context', type=ContextSpec)

class ClusterCertificate(otc_resource.OtcResource):
    base_path = '/clusters/%(cluster_id)s/clustercert'

    allow_create = False
    allow_fetch = True
    allow_commit = False
    allow_delete = False
    allow_list = False

    # Properties
    cluster_id = resource.URI('cluster_id')

    # we do not use Cce2Resource because status and Id handling is not required 
    # here and can have sid effects ic used by coincidence.
    #: Headers 
    kind = resource.Body('kind')
    api_version = resource.Body('apiVersion')

    clusters = resource.Body('clusters', type=list, list_type=ClusterCertListSpec)
    #: User certificates.
    users = resource.Body('users', type=list, list_type=UserListSpec)
    #: contexts
    contexts = resource.Body('contexts', type=list, list_type=ContextListSpec)
    #: Context information.
    current_context = resource.Body('current_context')

    def _prepare_request(self, requires_id=True, prepend_key=True,
        base_path=None):
        '''This is a workaround for the non-properly working default value of
           the resource framework see openstacksdk.compute.v2.server.'''
        self.kind = "Config"
        self.api_version = "v1"
    
        return super()._prepare_request(requires_id=requires_id,
            prepend_key=prepend_key, base_path=base_path)
