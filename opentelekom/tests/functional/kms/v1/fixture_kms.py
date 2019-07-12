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
import re
import fixtures

from openstack import exceptions

from opentelekom.tests.functional import base

from opentelekom.kms.kms_service import KmsService

class KmsFixture(fixtures.Fixture):
    """ This is a fixture mixin for KMS CustomerMasterKeys features """
    
    def __init__(self, user_cloud):
        self.user_cloud=user_cloud

    def setUp(self):
        super().setUp()
        self.user_cloud.add_service(KmsService("kmsv1"))

        self.key = None
        self.reuse = True
        self.destroy = False
                                     
    def _find_enabled_key(self, name):
         # because of the delayed delete, just look for an enabled key to reuse first
        cmks = list(self.user_cloud.kms.keys())
        enabledKeys = list(filter(lambda res: res.name.startswith(name) and int(res.key_state)==2, cmks))
        enabledKeys.sort(key=lambda x: x.name)
        return enabledKeys[0] if len(enabledKeys)>0 else None
        
    def _find_next_version(self, name):
        cmks = list(self.user_cloud.kms.keys())
        _vexp = re.compile('^' + name + '-([0-9]+)$')
        # search for matching names and extract the highest serial version number
        cmk_last_serial = six.moves.reduce(max, map(lambda vers: int(_vexp.match(vers.name).group(1)), cmks), 0)
        cmk_last_serial += 1
        return "{prefix}-{serial:06d}".format(serial=cmk_last_serial, prefix=name)

    def aquireTestKey(self, prefix):
        name = prefix + "-key"
        key = None
        if self.reuse:
            # try to reuse key in case of no lifecycle test
            key = self._find_enabled_key(name)
        if key is None:
            # create a key (if none is available or no reuse)
            self.CMK_NAME = self._find_next_version(name)            
            key = self.user_cloud.kmsv1.create_key(
                 name=self.CMK_NAME,
                 key_description='Open Telekom SDK test key')
        self.key = key       
        self.addCleanup(self._cleanupCustomerMasterKey)
        self.key = self.user_cloud.kmsv1.get_key(key)

    def _cleanupCustomerMasterKey(self):
        """ cleanup is called even if setup fails """
        if hasattr(self, 'key') and self.key is not None and self.destroy:
            # schedule deletion
            pending_days=7
            self.user_cloud.kmsv1.schedule_delete_key(self.key, pending_days=pending_days)