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

from opentelekom.dms.dms_service import DmsService


class DmsFixture(fixtures.Fixture):
    """ Fixture for an CSS cluster """ 
    
    def __init__(self, user_cloud):
        self.user_cloud=user_cloud

    def setUp(self):
        super().setUp()
        self.user_cloud.add_service(DmsService("dmsv1"))

    def createTestQueue(self, prefix):
        self.queue = self.user_cloud.dmsv1.create_queue(
            name=prefix + "-q",
            queue_mode="NORMAL",
            description="Open Telekom functional SDK test",
            redrive_policy="enable",
            max_consume_count=10
        )
        self.addCleanup(self._cleanupTestQueue)

    def _cleanupTestQueue(self):
        if hasattr(self, 'queue') and self.queue:
            self.user_cloud.dmsv1.delete_queue(self.queue)

    def createTestQueueGroup(self, prefix):
        self.queue_group = self.user_cloud.dmsv1.create_queue_group(
            name=prefix + "-qgroup",
            queue=self.queue
        )
        self.addCleanup(self._cleanupTestQueueGroup)

    def _cleanupTestQueueGroup(self):
        if hasattr(self, 'queue_group') and self.queue_group:
            self.user_cloud.dmsv1.delete_queue_group(self.queue, self.queue_group)

    def tearDown(self):
        super().tearDown()
