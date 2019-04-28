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

from opentelekom.dms.v1 import _proxy

class DmsService(service_description.ServiceDescription):
    """The Distributed Message Service DMS v1.0"""

    #valid_versions = [service_filter.ValidVersion('v1')]

    supported_versions = {
        '1': _proxy.Proxy
    }

    # additional fixup behavior for OpenTelekomCloud
    # if endpoint is not in catalog and there is no override, use a default
    # default endpoint and override are completed by the project_id if {project_id} placeholder is in the url
    # def _make_proxy(self, instance):
    #     endpoint_override = instance.config.get_endpoint(self.service_type)
    #     if endpoint_override is not None:
    #         project_id = instance.session.get_project_id(instance.auth)
    #         instance.config[self.service_type + '_endpoint_override'] = endpoint_override % project_id 

    #     try:
    #         proxy_obj = super()._make_proxy(instance)
    #     except EndpointNotFound: 
    #         if endpoint_override is None:
    #             endpoint_override = "https://rds.eu-de.otc.t-systems.com/v3/%(project_id)s"
    #             project_id = instance.session.get_project_id(instance.auth)
    #             instance.config[self.service_type + '_endpoint_override'] = endpoint_override % project_id 
    
    #     proxy_obj = super()._make_proxy(instance)
    #     return proxy_obj
    