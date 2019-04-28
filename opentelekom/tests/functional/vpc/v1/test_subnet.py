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


class TestSubnet(base.BaseFunctionalTest):

    def setUp(self):
        super().setUp()
        self.user_cloud.add_service(VpcService("vpc"))
        self.VPC_NAME = "rbe-vpc-sdktest4"
        self.SN1_NAME = "rbe-sn-sdktest4-1"
        self.SN2_NAME = "rbe-sn-sdktest4-2"
        self.vpc = self.user_cloud.vpc.create_vpc(
            name=self.VPC_NAME,
            cidr="10.250.0.0/16")
        self.sn1 = self.user_cloud.vpc.create_subnet(
            vpc=self.vpc,
            name=self.SN1_NAME,
            cidr="10.250.0.0/21",
            gateway_ip="10.250.0.1",
            dhcp_enable=False
            )
        self.sn2 = self.user_cloud.vpc.create_subnet(
            vpc=self.vpc,
            name=self.SN2_NAME,
            cidr="10.250.128.0/21",
            gateway_ip="10.250.128.7",
            availability_zone="eu-de-02",
            dnsList=["4.4.4.4", "5.5.5.5", "6.6.6.6"]
            )
        # it takes some time for the subnet to become active
        # but onl active subnets are assigned to vpcs
        self.user_cloud.vpc.wait_for_status(self.sn1)
        self.user_cloud.vpc.wait_for_status(self.sn2)

    def test_subnet_found_and_updated(self):
        subnets = list(self.user_cloud.vpc.subnets())
        self.assertGreater(len(subnets), 0)
        snfound = list(filter(lambda x: x['name'] == self.SN1_NAME or x['name'] == self.SN2_NAME, subnets ))
        self.assertEqual(len(snfound), 2)
    
        #remember that name is mandatory on update
        self.user_cloud.vpc.update_subnet(self.sn1, name=self.sn1.name, primary_dns="4.4.4.4", secondary_dns="5.5.5.5")

        found_sn1 = self.user_cloud.vpc.get_subnet(self.sn1.id)
        self.assertFalse(found_sn1 is None)
        self.assertEqual(found_sn1.id, self.sn1.id)
        self.assertEqual(found_sn1.primary_dns, "4.4.4.4")
        self.assertEqual(found_sn1.secondary_dns, "5.5.5.5")

        opts = [ { "opt_name": "ntp", "opt_value": "10.100.0.33,10.100.0.34" } ]
        new_name = self.sn2.name + "-x"
        self.user_cloud.vpc.update_subnet(self.sn2, name=new_name, extra_dhcp_opts=opts)

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
        if self.sn2 is not None:
            self.user_cloud.vpc.delete_subnet(subnet=self.sn2.id)
            self.user_cloud.vpc.wait_for_delete(self.sn2)
        if self.sn1 is not None:
            result=self.user_cloud.vpc.delete_subnet(subnet=self.sn1)
            self.user_cloud.vpc.wait_for_delete(result) # testing also the chained API calls
        if self.vpc is not None:
            self.user_cloud.vpc.delete_vpc(self.vpc.id)
