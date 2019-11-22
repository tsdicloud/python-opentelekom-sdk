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
from openstack.network.v2 import security_group
from openstack.network.v2 import security_group_rule


from opentelekom.tests.functional import base
from opentelekom.tests.functional.vpc.v1 import fixture_vpc
from opentelekom.tests.functional.csbs.v1 import fixture_csbs


from opentelekom.vpc.vpc_service import VpcService


class TestBackup(base.BaseFunctionalTest):

    def setUp(self):
        super().setUp()

        self.prefix = self.test_suite_prefix + "-csbs"

        self.vpcFixture  = self.useFixture(fixture_vpc.VpcFixture(self.user_cloud))
        self.csbsFixture = self.useFixture(fixture_csbs.CsbsFixture(self.user_cloud))
        self.vpcFixture.createTestSubnet1(self.prefix)
        self.csbsFixture.createTestSecGroupCsbs1(self.prefix)
        self.csbsFixture.createTestSimpleServer(self.prefix,
            self.vpcFixture.sn1,
            self.csbsFixture.csbs1_sg)
        self.csbsFixture.createTestCsbsPolicy(self.prefix,
            [ self.csbsFixture.simpleserver ])


    def check_list(self):
        policies = list(self.user_cloud.csbs.policies())
        self.assertGreater(len(policies), 0)
        policies_found = list(filter(lambda x: x['name'] == self.prefix +"-policy", policies ))
        self.assertEqual(len(policies_found), 1)


    def check_get(self):
        found_policy = self.user_cloud.csbs.get_policy(self.policy)
        self.assertTrue(found_policy)
        self.assertEqual(found_policy.id, self.csbsFixture.policy.id)
        self.assertEqual(found_policy.name, self.csbsFixture.policy.name)


    def check_update_find(self):
        self.policy.name = prefix + "newpolicy"
        self.policy.scheduled_operations.enabled = False
        self.policy.scheduled_operations.operation_definition.retention_duration_days = "-1"
        self.policy.scheduled_operations.operation_definition.max_backups="1" 

        found_again = self.user_cloud.csbs.find_policy(self.csbsFixture.policy.name)
        self.assertTrue(found_again)
        self.assertEqual(found_again.id, self.csbsFixture.policy.id)
        self.assertEqual(found_again.name, self.csbsFixture.policy.name)
        self.assertEqual(found_again.description, self.csbsFixture.policy.description)
        self.assertEqual(found_again.scheduled_operations.enabled,
            self.csbsFixture.policy.scheduled_operations.enabled)
        self.assertEqual(
            found_again.scheduled_operations.operation_definition.max_backups,
            self.csbsFixture.policy.scheduled_operations.operation_definition.max_backups)
        self.assertEqual(
            found_again.scheduled_operations.operation_definition.retention_duration_days,
            self.csbsFixture.policy.scheduled_operations.operation_definition.retention_duration_days)


    def test_lifecycle(self):
        with self.subTest(msg="Stage 1: Test listing a policy"):
            self.check_list()
        with self.subTest(msg="Stage 2: Test getting the policy"):
            self.check_get()
        with self.subTest(msg="Stage 3: Test policy update and check get"):
            self.check_update_find()

    def tearDown(self):
        super().tearDown()
