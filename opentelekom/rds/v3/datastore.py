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
from openstack import utils

from openstack import resource
from opentelekom import otc_resource


class Version(otc_resource.OtcResource):
    """DB Engine version information"""
    base_path = '/datastores/%(engine_name)s'

    #: Data store name
    datastore_name = resource.URI("engine_name")

    # capabilities
    allow_list = True

    #: Properties
    #: the id of a datastore/db_engine description
    id = resource.Body('id')
    #: the version string of the datastore/db_engine
    versionName = resource.Body('name')
