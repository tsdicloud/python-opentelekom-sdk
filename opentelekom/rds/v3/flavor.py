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
from openstack import utils
from openstack import resource

from openstack import resource
from opentelekom import otc_resource

class Flavor(otc_resource.OtcResource):
    """Database version detail information"""
    base_path = '/flavors/%(engine_name)s'

    #: Data store name
    engine_name = resource.URI("engine_name")
    #: query params: engine version
    _query_mapping = resource.QueryParameters("version_name")

    # capabilities
    allow_list = True

    #: Properties
    #: the flavor identifier of the database
    spec_code = resource.Body('spec_code')
    #: the installation mode (ha, single, ...)
    instance_mode = resource.Body('instance_mode')
    #: number of vcpus
    vcpus = resource.Body('vcpus')
    #: number of vcpus
    ram = resource.Body('ram')
    
    def _action(self, session, action, body):
        """Preform actions given the message body.

        """
        url = utils.urljoin(self.base_path)
        response = session.get(url)
        exceptions.raise_from_response(response)
        return response