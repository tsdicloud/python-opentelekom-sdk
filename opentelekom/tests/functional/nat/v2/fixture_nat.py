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
from openstack.network.v2 import network as _net

from opentelekom.tests.functional import base

from opentelekom.nat.nat_service import NatService
from opentelekom.vpc.v1 import vpc as _vpc

class NatFixture(fixtures.Fixture):
    """ This is a fixture mixin for vpc features """
    
    def __init__(self, user_cloud):
        self.user_cloud=user_cloud


    def setUp(self):
        super().setUp()
        self.user_cloud.add_service(NatService("nat"))


    def addNatGateway(self, prefix, subnet, eip):
        """ Fixture to add a natting gateway and a 
            snat rule for the given subnet 
            
            :param prefix: name prefix
            :param vpc: id or ~opentelekom.vpc.v1.vpc.Vpc object
                   to associate the gateway to  
            """ 
        vpc_id=subnet.vpc_id
        self.nat = self.user_cloud.nat.create_nat(
            name=prefix + "-natgw",
            description="Open telekom SDK test for nat gateway",
            vpc_id=vpc_id,
            subnet_id=subnet.id,
            spec="1"
            )
        self.addCleanup(self._cleanupNatGateway)
        self.user_cloud.nat.wait_for_status(self.nat)

        # add SNAT rule to subnet
        eip_id = eip.id if hasattr(eip, 'id') else eip
        self.user_cloud.nat.create_snat_rule(
            nat_gateway_id=self.nat.id,
            subnet_id=subnet.id,
            eip_id=eip_id)
        self.addCleanup(self._cleanupSnatRules)

    def _cleanupSnatRules(self):
        if hasattr(self, 'nat') and self.nat is not None:
            # cleanup rules first
            rules = self.user_cloud.nat.snat_gw_rules(self.nat)
            for rule in rules:
                self.user_cloud.nat.delete_snat_rule(rule)
                self.user_cloud.nat.wait_for_delete(rule)

    def _cleanupNatGateway(self):
        if hasattr(self, 'nat') and self.nat is not None:
            self.user_cloud.nat.delete_nat(self.nat)
            self.user_cloud.nat.wait_for_delete(self.nat)
