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

from openstack.tests.unit import base

from opentelekom.rds.v3 import datastore

DATASTORE_NAME = 'MySQL'
EXAMPLE = {
    'datastore_name': DATASTORE_NAME
}


class TestDataStore(base.TestCase):

    def test_basic(self):
        sot = datastore.Version()
        self.assertTrue(sot.allow_list)
        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertFalse(sot.allow_delete)

    def test_make_it(self):
        sot = datastore.Version(**EXAMPLE)
        self.assertEqual('/datastores', sot.base_path)
        self.assertEqual('MySQL', sot.datastore_name) 