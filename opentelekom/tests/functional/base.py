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

import re
import os

from six.moves import reduce

from opentelekom import connection as otc_connection
from openstack.tests.functional import base

from opentelekom.rds.rds_service import Rds3Service
from opentelekom.kms.kms_service import KmsService

from unittest import case

class BaseFunctionalTest(base.BaseFunctionalTest):

    def _set_user_cloud(self, **kwargs):
        """ This is where the new services are added to the Openstack SDK as extra services """
        user_config = self.config.get_one(
            cloud=self._demo_name, **kwargs)
        self.user_cloud = otc_connection.Connection(config=user_config)
        base._disable_keep_alive(self.user_cloud)
                                                    
    def setUp(self):
        super().setUp()

        self.user_cloud.add_service(KmsService("kmsv1"))

        self.key = None
        self.reuse = True
        self.destroy = False

        self.test_suite_prefix = os.environ.get('OTC_TEST_SUITE', 'sdktest')
        self.test_key = os.environ.get('OTC_TEST_KEY', self.test_suite_prefix)
        self.test_ssh_key = os.environ.get('OTC_TEST_SSH_KEY', self.test_suite_prefix)

        # FIXME workaroud AttributeError: 'NoneType' object has no attribute 'result_supports_subtests'
        # for subtests in combination with pdb (bug before late 3.7)
        self._outcome = case._Outcome()




    def _checkTags(self, proxy, resource, prefix, component):
        tag1 = "_ENV"
        tag2 = "_COMPONENT"

        proxy.add_tag(resource, tag1, prefix)
        res = proxy.fetch_tags(resource)
        self.assertEqual( res.tags[tag1], prefix )

        proxy.remove_tag(resource, tag1)
        res = proxy.fetch_tags(resource)
        self.assertFalse(res.tags)

        proxy.set_tags(resource, tags={ tag1: prefix+'-x', tag2: component })
        res = proxy.fetch_tags(resource)
        self.assertGreater(len(res.tags), 1)
        self.assertEqual( res.tags[tag1], prefix + '-x')
        self.assertEqual( res.tags[tag2], component )
        proxy.remove_all_tags(resource)
        res = proxy.fetch_tags(resource)
        self.assertFalse(res.tags)


    def tearDown(self):
        super().tearDown()
