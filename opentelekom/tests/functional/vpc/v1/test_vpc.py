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

from opentelekom.vpc.vpc_service import VpcService


from opentelekom.tests.functional.vpc.v1 import fixture_vpc

class TestVpc(base.BaseFunctionalTest):

    def setUp(self):
        super().setUp()

        self.prefix = "rbe-sdktest-vpc"

        self.vpcFixture = self.useFixture(fixture_vpc.VpcFixture(self.user_cloud))
        self.vpcFixture.createTestVpc(self.prefix)    

    def test_vpc_found_update(self):
        vpcs = list(self.user_cloud.vpc.vpcs())
        self.assertGreater(len(vpcs), 0)
        #import pdb; pdb.set_trace()
        vpcfound = list(filter(lambda x: x['name'] == self.prefix + "-vpc", vpcs ))
        self.assertEqual(len(vpcfound), 1)
   
        self._checkTags(self.user_cloud.vpc2, self.vpcFixture.vpc,
            prefix=self.prefix, component="vpc")

        self.user_cloud.vpc.update_vpc(self.vpcFixture.vpc.id, enable_shared_snat=True)
        found_vpc = self.user_cloud.vpc.get_vpc(self.vpcFixture.vpc.id)
        self.assertFalse(found_vpc is None)
        self.assertEqual(found_vpc.id, self.vpcFixture.vpc.id)
        self.assertEqual(found_vpc.enable_shared_snat, True)


    def tearDown(self):
        super().tearDown()
