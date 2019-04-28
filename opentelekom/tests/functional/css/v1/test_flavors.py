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

from opentelekom.css.css_service import CssService

from opentelekom.tests.functional import base

class TestFlavors(base.BaseFunctionalTest):

    def setUp(self):
        super().setUp()
        self.user_cloud.add_service(CssService("css"))

    def test_flavors(self):
        flavors = list(self.user_cloud.css.flavors())
        self.assertFalse(flavors is None)
        self.assertGreater(len(flavors), 0)

    def tearDown(self):
        super().tearDown()
        pass

