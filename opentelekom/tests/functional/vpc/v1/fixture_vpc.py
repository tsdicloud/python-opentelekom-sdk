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
import os
import openstack.config

from openstack import exceptions
from opentelekom import connection as otc_connection
from opentelekom.tests.functional import base

from opentelekom.vpc.vpc_service import VpcService


FOREIGN_CLOUD_NAME = os.getenv('OTC_FOREIGN_CLOUD', 'otc-foreign-tenant')
FOREIGN_CLOUD_REGION = openstack.config.get_cloud_region(cloud=FOREIGN_CLOUD_NAME)


class VpcFixture(fixtures.Fixture):
    """ This is a fixture for vpc features 

    FIXME: At the moment, version detection does not work properly,
    which forces the need for the following config variable settings:
    vpc2.0_api_version: 2
    vpc_api_version: 1
    """


    def __init__(self, user_cloud):
        self.user_cloud=user_cloud

    def _connect_other_cloud(self, cloud_name, **kwargs):
        other_config = openstack.config.OpenStackConfig().get_one(
            cloud=cloud_name, **kwargs)
        other_cloud = otc_connection.Connection(config=other_config)
        sess = other_cloud.config.get_session()
        sess.keep_alive = False
        return other_cloud

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


    def _cleanupTestVpc(self):
        if hasattr(self, 'vpc') and self.vpc is not None:
            self.user_cloud.vpc.delete_vpc(self.vpc)


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


    def _cleanupTestSubnet1(self):
        if hasattr(self, 'sn1') and self.sn1 is not None:
            self.user_cloud.vpc.delete_subnet(subnet=self.sn1.id)
            self.user_cloud.vpc.wait_for_delete(self.sn1)




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


    def _cleanupTestSubnet2(self):
        if hasattr(self, 'sn2') and self.sn2 is not None:
            self.user_cloud.vpc.delete_subnet(subnet=self.sn2.id)
            self.user_cloud.vpc.wait_for_delete(self.sn2)


    def createPeeringTestVpc(self, prefix):
        """ Fixture to add a test vpc and subnet1 """ 
        self.peering_vpc = self.user_cloud.vpc.create_vpc(
            name=prefix + "-peering-vpc",
            cidr="10.148.0.0/16") # has to be disjoint
        self.addCleanup(self._cleanupPeeringTestVpc)


    def _cleanupPeeringTestVpc(self):
        if hasattr(self, 'peering_vpc') and self.peering_vpc is not None:
            self.user_cloud.vpc.delete_vpc(self.peering_vpc)


    def createPeeringTestSubnet(self, prefix):
        """ Fixture to add a peeringtest vpc and subnet1 """ 
        self.peering_sn1 = self.user_cloud.vpc.create_subnet(
            vpc=self.peering_vpc,
            name=prefix + "-peering-sn1",
            cidr="10.148.0.0/21",
            gateway_ip="10.148.0.1")
        self.addCleanup(self._cleanupPeeringTestSubnet)
        self.user_cloud.vpc.wait_for_status(self.peering_sn1)


    def _cleanupPeeringTestSubnet(self):
        if hasattr(self, 'peering_sn1') and self.peering_sn1 is not None:
            self.user_cloud.vpc.delete_subnet(subnet=self.peering_sn1.id)
            self.user_cloud.vpc.wait_for_delete(self.peering_sn1)


    def connectForeignCloud(self):
        """ Fixture to add a test vpc and subnet1 """ 

    def createForeignTestVpc(self, prefix):
        self.foreign_cloud = self._connect_other_cloud(FOREIGN_CLOUD_NAME)
        self.foreign_cloud.add_service( VpcService("vpc", aliases=['vpc1'] ))      # v1 service registration
        self.foreign_cloud.add_service( VpcService("vpc2.0", aliases=['vpc2'] ))  # v2 service registration

        self.foreign_vpc = self.foreign_cloud.vpc.create_vpc(
            name=prefix + "-foreign-vpc",
            cidr="10.111.0.0/16")
        self.addCleanup(self._cleanupForeignTestVpc)

    def _cleanupForeignTestVpc(self):
        if hasattr(self, 'foreign_vpc') and self.foreign_vpc is not None:
            self.foreign_cloud.vpc.delete_vpc(self.foreign_vpc)


    def createForeignTestSubnet(self, prefix):
        """ Fixture to add a peeringtest vpc and subnet1 """ 
        self.foreign_sn1 = self.foreign_cloud.vpc.create_subnet(
            vpc=self.foreign_vpc,
            name=prefix + "-peering-sn1",
            cidr="10.111.0.0/21",
            gateway_ip="10.111.0.1")
        self.addCleanup(self._cleanupForeignTestSubnet)
        self.user_cloud.vpc.wait_for_status(self.foreign_sn1)


    def _cleanupForeignTestSubnet(self):
        if hasattr(self, 'foreign_sn1') and self.foreign_sn1 is not None:
            self.foreign_cloud.vpc.delete_subnet(subnet=self.foreign_sn1.id)
            self.foreign_cloud.vpc.wait_for_delete(self.foreign_sn1)
