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

import six

from openstack import exceptions
from opentelekom.tests.functional import base

from opentelekom.rds.rds_service import Rds3Service

class TestFlavor(base.BaseFunctionalTest):

    def setUp(self):
        super().setUp()
        self.user_cloud.add_service(Rds3Service("rdsv3"))

    def test_flavor_found(self):
        flavors = list(self.user_cloud.rdsv3.flavors(engine_name='mysql',version_name='5.6'))
        self.assertGreater(len(flavors), 0)

"""         for flavor in flavors:
            self.assertIsInstance(flavor.id, six.string_types)
            self.assertIsInstance(flavor.name, six.string_types)
            self.assertIsInstance(flavor.disk, int)
            self.assertIsInstance(flavor.ram, int)
            self.assertIsInstance(flavor.vcpus, int) """