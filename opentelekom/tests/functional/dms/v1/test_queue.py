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

from opentelekom.dms.dms_service import DmsService


class TestQueue(base.BaseFunctionalTest):

    def setUp(self):
        super().setUp()
        self.user_cloud.add_service(DmsService("dmsv1"))

        self.QUEUE_NAME = "rbe-dms-testsdkq1"
        self.queue = self.user_cloud.dmsv1.create_queue(
            name=self.QUEUE_NAME,
            queue_mode="NORMAL",
            description="Open Telekom functional SDK test",
            redrive_policy="enable",
            max_consume_count=10
        )

    def test_queue_found(self):
        queues = list(self.user_cloud.dmsv1.queues(include_deadletter=True))
        self.assertGreater(len(queues), 0)
        #import pdb; pdb.set_trace()
        qfound = list(filter(lambda x: x['name'] == self.QUEUE_NAME, queues ))
        self.assertEqual(len(qfound), 1)
        
        found_queue = self.user_cloud.dmsv1.get_queue(self.queue.id)
        self.assertFalse(found_queue is None)
        self.assertEqual(found_queue.id, self.queue.id)

    def tearDown(self):
        super().tearDown()
        if self.queue is not None:
            self.user_cloud.dmsv1.delete_queue(self.queue)
