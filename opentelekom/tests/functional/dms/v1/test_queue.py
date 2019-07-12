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
from opentelekom.tests.functional.dms.v1 import fixture_dms


from opentelekom.dms.dms_service import DmsService


class TestQueue(base.BaseFunctionalTest):

    def setUp(self):
        super().setUp()
        self.user_cloud.add_service(DmsService("dmsv1"))

        self.prefix = self.test_suite_prefix + "-dms"

        self.dmsFixture = self.useFixture(fixture_dms.DmsFixture(self.user_cloud))
        self.dmsFixture.createTestQueue(self.prefix)
        self.dmsFixture.createTestQueueGroup(self.prefix)

    def test_queue_found(self):
        queues = list(self.user_cloud.dmsv1.queues(include_deadletter=True))
        self.assertGreater(len(queues), 0)
        #import pdb; pdb.set_trace()
        qfound = list(filter(lambda x: x['name'] == self.prefix+"-q", queues ))
        self.assertEqual(len(qfound), 1)

        groups = list(self.user_cloud.dmsv1.queue_groups(self.dmsFixture.queue,include_deadletter=True))
        self.assertGreater(len(groups), 0)
        #import pdb; pdb.set_trace()
        gfound = list(filter(lambda x: x['name'] == self.prefix+"-qgroup", groups ))
        self.assertEqual(len(gfound), 1)

        found_queue = self.user_cloud.dmsv1.get_queue(self.dmsFixture.queue.id)
        self.assertTrue(found_queue)
        self.assertEqual(found_queue.id, self.dmsFixture.queue.id)
        found_group = self.user_cloud.dmsv1.get_queue_group(queue=self.dmsFixture.queue.id, 
          group=self.dmsFixture.queue_group.id)
        self.assertTrue(found_group)
        self.assertEqual(found_group.id, self.dmsFixture.queue_group.id)

        found_queue_again = self.user_cloud.dmsv1.find_queue(self.dmsFixture.queue.name)
        self.assertTrue(found_queue_again)
        self.assertEqual(found_queue_again.id, self.dmsFixture.queue.id)
        found_group_again = self.user_cloud.dmsv1.find_queue_group(queue=found_queue_again, 
            name_or_id=self.dmsFixture.queue_group.name)
        self.assertTrue(found_group_again)
        self.assertEqual(found_group_again.id, self.dmsFixture.queue_group.id)

    def tearDown(self):
        super().tearDown()
