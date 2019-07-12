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
from opentelekom.tests.functional.vpc.v1 import fixture_vpc

class TestNatGateway(base.BaseFunctionalTest):

    def setUp(self):
        super().setUp()

class TestSubnet(base.BaseFunctionalTest):

    def setUp(self):
        super().setUp()

        self.prefix = self.test_suite_prefix + "-subnet"

        self.vpcFixture = self.useFixture(fixture_vpc.VpcFixture(self.user_cloud))
        self.vpcFixture.createTestSubnet1(self.prefix)
        self.vpcFixture.addTestSubnet2(self.prefix)

    def test_subnet_found_and_updated(self):
        subnets = list(self.user_cloud.vpc.subnets())
        self.assertGreater(len(subnets), 0)
        sn1_name = self.prefix +"-sn1"
        sn2_name = self.prefix +"-sn2"
        snfound = list(filter(lambda x: x['name'] == sn1_name or x['name'] == sn2_name, subnets ))
        self.assertEqual(len(snfound), 2)
    
        #remember that name is mandatory on update
        self.user_cloud.vpc.update_subnet(self.vpcFixture.sn1, name=self.sn1.name, primary_dns="4.4.4.4", secondary_dns="5.5.5.5")

        found_sn1 = self.user_cloud.vpc.get_subnet(self.vpcFixture.sn1.id)
        self.assertFalse(found_sn1 is None)
        self.assertEqual(found_sn1.id, self.vpcFixture.sn1.id)
        self.assertEqual(found_sn1.primary_dns, "4.4.4.4")
        self.assertEqual(found_sn1.secondary_dns, "5.5.5.5")

        opts = [ { "opt_name": "ntp", "opt_value": "10.100.0.33,10.100.0.34" } ]
        new_name = self.prefix + "-snx"
        self.user_cloud.vpc.update_subnet(self.vpcFixture.sn2, name=new_name, extra_dhcp_opts=opts)

        found_sn2 = self.user_cloud.vpc.get_subnet(self.sn2.id)
        self.assertFalse(found_sn2 is None)
        self.assertEqual(found_sn2.id, self.sn2.id)
        self.assertEqual(found_sn2.name, new_name)
        self.assertFalse(found_sn2.extra_dhcp_opts is None)
        self.assertEqual(len(found_sn2.extra_dhcp_opts), 1)
        self.assertEqual(found_sn2.extra_dhcp_opts[0]['opt_name'], "ntp")
        self.assertEqual(found_sn2.extra_dhcp_opts[0]['opt_value'], "10.100.0.33,10.100.0.34")

    def tearDown(self):
        super().tearDown()