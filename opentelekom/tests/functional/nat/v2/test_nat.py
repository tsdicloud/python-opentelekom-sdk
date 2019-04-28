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
from opentelekom.tests.functional.vpc.v1 import fixture_eip
from opentelekom.tests.functional.nat.v2 import fixture_nat

from opentelekom.vpc.vpc_service import VpcService
from opentelekom.nat.nat_service import NatService

class TestNatGateway(base.BaseFunctionalTest):

    def setUp(self):
        super().setUp()

        self.prefix = "rbe-sdktest-nat"

        self.vpcFixture = self.useFixture(fixture_vpc.VpcFixture(self.user_cloud))
        self.vpcFixture.createTestSubnet1(self.prefix)
        
        self.eipFixture = self.useFixture(fixture_eip.EipFixture(self.user_cloud))
        eip = self.eipFixture.aquireEIP()

        self.natFixture = self.useFixture(fixture_nat.NatFixture(self.user_cloud))
        self.natFixture.addNatGateway(self.prefix, subnet=self.vpcFixture.sn1, eip=eip)
        #import pdb; pdb.set_trace()

    def test_nat_found(self):
        pass
