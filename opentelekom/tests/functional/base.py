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
from six.moves import reduce

from opentelekom import connection as otc_connection
from openstack.tests.functional import base

from opentelekom.rds.rds_service import Rds3Service
from opentelekom.kms.kms_service import KmsService


class BaseFunctionalTest(base.BaseFunctionalTest):

    def _set_user_cloud(self, **kwargs):
        """ This is where the new services are added to the Openstack SDK as extra services """
        user_config = self.config.get_one(
            cloud=self._demo_name, **kwargs)
        self.user_cloud = otc_connection.Connection(config=user_config)
        base._disable_keep_alive(self.user_cloud)
                                                    
    def _find_enabled_key(self):
         # because of the delayed delete, just look for an enabled key to reuse first
        cmks = list(self.user_cloud.kms.keys())
        enabledKeys = list(filter(lambda res: res.key_alias.startswith(self.CMK_PREFIX) and int(res.key_state)==2, cmks))
        enabledKeys.sort(key=lambda x: x.key_alias)
        return enabledKeys[0] if len(enabledKeys)>0 else None
        
    def _find_next_version(self):
        cmks = list(self.user_cloud.kms.keys())
        _vexp = re.compile('^' + self.CMK_PREFIX + '-([0-9]+)$')
        # search for matching names and extract the highest serial version number
        cmk_last_serial = reduce(max, map(lambda vers: int(_vexp.match(vers.key_alias).group(1)), cmks), 0)
        cmk_last_serial += 1
        return "{prefix}-{serial:06d}".format(serial=cmk_last_serial, prefix=self.CMK_PREFIX)

    def _prepare_key(self):
        self.addCleanup(self.cleanup)

        self.CMK_PREFIX = "rbe-sdktest-key"
        key = None
        if self.reuse:
            # try to reuse key in case of no lifecycle test
            key = self._find_enabled_key()
        if key is None:
            # create a key (if none is available or no reuse)
            self.CMK_NAME = self._find_next_version()            
            key = self.user_cloud.kmsv1.create_key(
                 key_alias=self.CMK_NAME,
                 key_description='Open Telekom SDK test key')
        self.key = self.user_cloud.kmsv1.get_key(key)       


    def setUp(self):
        super().setUp()

        self.user_cloud.add_service(KmsService("kmsv1"))

        self.key = None
        self.reuse = True
        self.destroy = False

    def tearDown(self):
        super().tearDown()

    def cleanup(self):
        """ cleanup is called even if setup fails """
        if self.key is not None and self.destroy:
            # schedule deletion
            pending_days=7
            self.user_cloud.kmsv1.schedule_delete_key(self.key, pending_days=pending_days)
 