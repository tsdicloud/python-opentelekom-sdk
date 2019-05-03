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
from opentelekom.tests.functional.kms.v1 import fixture_kms

from opentelekom.kms.kms_service import KmsService


class TestCustomeMasterKey(base.BaseFunctionalTest):

    def setUp(self):
        super().setUp()

        self.prefix = "rbe-sdktest"

        self.cmkFixture = self.useFixture(fixture_kms.KmsFixture(self.user_cloud))
        self.cmkFixture.aquireTestKey(self.prefix)    



    def test_cmk_found_enable_disable(self):
        cmk = self.user_cloud.kmsv1.get_key(self.cmkFixture.key)
        self.assertFalse(cmk is None)
        self.assertEqual(cmk.key_id, self.cmkFixture.key.key_id)

        cmk = self.user_cloud.kmsv1.find_key(self.cmkFixture.key.name)
        self.assertFalse(cmk is None)
        self.assertEqual(cmk.key_id, self.cmkFixture.key.key_id)

        cmk_state1 = self.user_cloud.kmsv1.disable_key(self.cmkFixture.key.key_id)
        self.assertFalse(cmk_state1 is None)
        self.assertEqual(cmk_state1.id, self.cmkFixture.key.key_id)
        self.assertTrue(cmk_state1.key_state == 3)

        cmk_state2 = self.user_cloud.kmsv1.enable_key(cmk_state1)
        self.assertFalse(cmk_state2 is None)
        self.assertEqual(cmk_state2.key_id, self.cmkFixture.key.key_id)
        self.assertTrue(cmk_state2.key_state == 2)

    def tearDown(self):
        if self.cmkFixture.key is not None and self.cmkFixture.destroy:
            # schedule deletion
            pending_days=14
            cmk_del1 = self.user_cloud.kmsv1.schedule_delete_key(self.cmkFixture.key, pending_days=pending_days)
            self.assertFalse(cmk_del1 is None)
            self.assertEqual(cmk_del1.id, self.cmkFixture.key.key_id)
            self.assertTrue(cmk_del1.key_state == 4)
            # TODO: check pending days
            # self.assertTrue(cmk_del1.pending_days == pending_days)
            # cancel deletion
            cmk_del2 = self.user_cloud.kmsv1.cancel_delete_key(self.cmkFixture.key)
            self.assertFalse(cmk_del2 is None)
            self.assertEqual(cmk_del2.key_id, self.cmkFixture.key.key_id)
            self.assertTrue(cmk_del2.key_state < 4)
        super().tearDown()
