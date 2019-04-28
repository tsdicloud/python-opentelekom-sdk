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

from opentelekom.kms.kms_service import KmsService


class TestCustomeMasterKey(base.BaseFunctionalTest):

    def setUp(self):
        super().setUp()
        self.user_cloud.add_service(VpcService("vpc"))

        self.VPC_NAME = "rbe-vpc-sdktest1"
        self.vpc = self.user_cloud.vpc.create_vpc(
            name=self.VPC_NAME,
            cidr="10.255.0.0/16")

    def test_vpc_found(self):
        vpcs = list(self.user_cloud.vpc.vpcs())
        self.assertGreater(len(vpcs), 0)
        #import pdb; pdb.set_trace()
        vpcfound = list(filter(lambda x: x['name'] == self.VPC_NAME, vpcs ))
        self.assertEqual(len(vpcfound), 1)
        

    def test_vpc_update(self):
        self.user_cloud.vpc.update_vpc(self.vpc.id, enable_shared_snat=True)

        found_vpc = self.user_cloud.vpc.get_vpc(self.vpc.id)
        self.assertFalse(found_vpc is None)
        self.assertEqual(found_vpc.id, self.vpc.id)
        self.assertEqual(found_vpc.enable_shared_snat, True)


    def tearDown(self):
        super().tearDown()
        if self.vpc is not None:
            self.user_cloud.vpc.delete_vpc(self.vpc.id)
