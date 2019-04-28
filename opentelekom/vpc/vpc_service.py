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


from keystoneauth1.exceptions.catalog import EndpointNotFound
from openstack import service_description

from opentelekom.vpc.v1 import _proxy

class VpcService(service_description.ServiceDescription):
    """A VPC service that eases use of openstack networking on Open Telekom Cloud"""

    #valid_versions = [service_filter.ValidVersion('v1')]

    supported_versions = {
        '1': _proxy.Proxy
    }
