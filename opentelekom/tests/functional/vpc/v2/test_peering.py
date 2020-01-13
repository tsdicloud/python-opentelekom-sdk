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
from opentelekom.vpc.v2.peering import VpcInfoSpec

from opentelekom.tests.functional.vpc.v1 import fixture_vpc


class TestPeering(base.BaseFunctionalTest):

    def setUp(self):
        super().setUp()

        self.prefix = self.test_suite_prefix + "-peering"

        self.vpcFixture = self.useFixture(fixture_vpc.VpcFixture(self.user_cloud))
        self.vpcFixture.createTestVpc(self.prefix)

        self.user_cloud.add_service( VpcService("peervpc") )  # v2.0 service registration with artificial, non-project endpoint
    

    def test_local_peering(self):
        self.vpcFixture.createPeeringTestVpc(self.prefix)
        self.assertTrue(self.vpcFixture.peering_vpc)
        self.local_peering = self.user_cloud.peervpc.create_peering(name=self.prefix +"-local-peering",
            #request_vpc_info = {
            #    "vpc_id": self.vpcFixture.vpc.id,
            #},
            #accept_vpc_info = {
            #    "vpc_id": self.vpcFixture.peering_vpc.id,
            #}
            request_vpc_info = VpcInfoSpec(
                vpc_id=self.vpcFixture.vpc.id,
            ),
            accept_vpc_info = VpcInfoSpec(
                vpc_id=self.vpcFixture.peering_vpc.id,
            )
        )
        self.addCleanup(self._cleanupLocalPeering)


    def _cleanupLocalPeering(self):
        if hasattr(self, 'local_peering') and self.local_peering is not None:
            self.user_cloud.peervpc.delete_peering(self.local_peering)
            self.user_cloud.peervpc.wait_for_delete(self.local_peering)




    def test_remote_peering(self):
        # create the peering
        self.vpcFixture.createForeignTestVpc(self.prefix)
        self.assertTrue(self.vpcFixture.foreign_vpc)
        self.remote_peering = self.user_cloud.peervpc.create_peering(name=self.prefix +"-remote-peering",
            request_vpc_info = VpcInfoSpec(
                vpc_id=self.vpcFixture.vpc.id,
            ),
            accept_vpc_info = VpcInfoSpec(
                vpc_id=self.vpcFixture.foreign_vpc.id,
                tenant_id=self.vpcFixture.foreign_cloud.session.get_project_id()
            )
            #request_vpc_info = {
            #    "vpc_id": self.vpcFixture.vpc.id,
            #},
            #accept_vpc_info = {
            #    "vpc_id": self.vpcFixture.foreign_vpc.id,
            #    "tenant_id": self.vpcFixture.foreign_cloud.session.get_project_id()
            #}
        )
        self.addCleanup(self._cleanupRemotePeering)
        self.vpcFixture.foreign_cloud.add_service( VpcService("peervpc") )  # v2.0 service registration with artificial, non-project endpoint name

        # check peering status
        peering_status = self.user_cloud.peervpc.get_peering(self.remote_peering)
        self.assertEqual(peering_status.status, "PENDING_ACCEPTANCE") 
        foreign_status = self.vpcFixture.foreign_cloud.peervpc.get_peering(self.remote_peering)
        self.assertEqual(foreign_status.status, "PENDING_ACCEPTANCE") 

        # accept peering
        self.vpcFixture.foreign_cloud.peervpc.accept_peering(self.remote_peering)

        # check peering status
        self.user_cloud.peervpc.wait_for_status(self.remote_peering, "ACTIVE")
        self.vpcFixture.foreign_cloud.peervpc.wait_for_status(self.remote_peering, "ACTIVE")



    def test_remote_reject_peering(self):
        # create the peering
        self.vpcFixture.createForeignTestVpc(self.prefix)
        self.assertTrue(self.vpcFixture.foreign_vpc)
        self.remote_peering = self.user_cloud.peervpc.create_peering(name=self.prefix +"-remote-peering",
            request_vpc_info = VpcInfoSpec(
                vpc_id=self.vpcFixture.vpc.id,
            ),
            accept_vpc_info = VpcInfoSpec(
                vpc_id=self.vpcFixture.foreign_vpc.id,
                tenant_id=self.vpcFixture.foreign_cloud.session.get_project_id()
            )
            #request_vpc_info = {
            #    "vpc_id": self.vpcFixture.vpc.id,
            #    #"tenant_id": self.user_cloud.session.get_project_id()
            #},
            #accept_vpc_info = {
            #    "vpc_id": self.vpcFixture.foreign_vpc.id,
            #    "tenant_id": self.vpcFixture.foreign_cloud.session.get_project_id()
            #}
        )
        self.addCleanup(self._cleanupRemotePeering)
        self.vpcFixture.foreign_cloud.add_service( VpcService("peervpc") )  # v2.0 service registration with artificial, non-project endpoint

        # check peering status
        peering_status = self.user_cloud.peervpc.get_peering(self.remote_peering)
        self.assertEqual(peering_status.status, "PENDING_ACCEPTANCE") 
        foreign_status = self.vpcFixture.foreign_cloud.peervpc.get_peering(self.remote_peering)
        self.assertEqual(foreign_status.status, "PENDING_ACCEPTANCE") 

        # accept peering
        self.vpcFixture.foreign_cloud.peervpc.reject_peering(self.remote_peering)

        # check peering status
        self.user_cloud.peervpc.wait_for_status(self.remote_peering, "REJECTED")
        self.vpcFixture.foreign_cloud.peervpc.wait_for_status(self.remote_peering, "REJECTED")



    def _cleanupRemotePeering(self):
        if hasattr(self, 'remote_peering') and self.remote_peering is not None:
            self.user_cloud.peervpc.delete_peering(self.remote_peering)
            self.user_cloud.peervpc.wait_for_delete(self.remote_peering)



    def tearDown(self):
        super().tearDown()

        
