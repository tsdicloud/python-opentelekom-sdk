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
import fixtures

from openstack import exceptions
from opentelekom.tests.functional import base

from opentelekom.vpc.vpc_service import VpcService

class VpcFixture(fixtures.Fixture):
    """ This is a fixture for vpc features 

    FIXME: At the moment, version detection does not work properly,
    which forces the need for the following config variable settings:
    vpc2.0_api_version: 2
    vpc_api_version: 1
    """


    def __init__(self, user_cloud):
        self.user_cloud=user_cloud


    def setUp(self):
        super().setUp()
        self.user_cloud.add_service( VpcService("vpc", aliases=['vpc1'] ))      # v1 service registration
        self.user_cloud.add_service( VpcService("vpc2.0", aliases=['vpc2'] ))  # v2 service registration
        #self.user_cloud.vpc2.get_endpoint_data()


    def createTestVpc(self, prefix):
        """ Fixture to add a test vpc and subnet1 """ 
        self.vpc = self.user_cloud.vpc.create_vpc(
            name=prefix + "-vpc",
            cidr="10.248.0.0/16")
        self.addCleanup(self._cleanupTestVpc)

    def createTestSubnet1(self, prefix):
        """ Fixture to add a test vpc and subnet1 """ 
        self.vpc = self.user_cloud.vpc.create_vpc(
            name=prefix + "-vpc",
            cidr="10.248.0.0/16")
        self.addCleanup(self._cleanupTestVpc)
        self.sn1 = self.user_cloud.vpc.create_subnet(
            vpc=self.vpc,
            name=prefix + "-sn1",
            cidr="10.248.0.0/21",
            gateway_ip="10.248.0.1")
        self.addCleanup(self._cleanupTestSubnet1)
        self.user_cloud.vpc.wait_for_status(self.sn1)

    def addTestSubnet2(self, prefix):
        """ Fixture to add another subnet2 """ 
        self.sn2 = self.user_cloud.vpc.create_subnet(
            vpc=self.vpc,
            name=prefix + "-sn2",
            cidr="10.248.32.0/21",
            gateway_ip="10.32.0.1"
            )
        self.addCleanup(self._cleanupTestSubnet2)
        self.user_cloud.vpc.wait_for_status(self.sn2)


    def _cleanupTestVpc(self):
        if hasattr(self, 'vpc') and self.vpc is not None:
            self.user_cloud.vpc.delete_vpc(self.vpc)

    def _cleanupTestSubnet1(self):
        if hasattr(self, 'sn1') and self.sn1 is not None:
            self.user_cloud.vpc.delete_subnet(subnet=self.sn1.id)
            self.user_cloud.vpc.wait_for_delete(self.sn1)

    def _cleanupTestSubnet2(self):
        if hasattr(self, 'sn2') and self.sn2 is not None:
            self.user_cloud.vpc.delete_subnet(subnet=self.sn2.id)
            self.user_cloud.vpc.wait_for_delete(self.sn2)
