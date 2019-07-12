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
import time

from openstack import exceptions
from openstack.network.v2 import security_group
from openstack.network.v2 import security_group_rule


from opentelekom.tests.functional import base
from opentelekom.tests.functional.vpc.v1 import fixture_vpc
from opentelekom.tests.functional.kms.v1 import fixture_kms
from opentelekom.tests.functional.rds.v3 import fixture_rds

from opentelekom.rds.v3 import instance as _db

class TestDB(base.BaseFunctionalTest):

    def setUp(self):
        super().setUp()

        self.prefix = self.test_suite_prefix + "-rds3"

        self.vpcFixture = self.useFixture(fixture_vpc.VpcFixture(self.user_cloud))
        self.cmkFixture = self.useFixture(fixture_kms.KmsFixture(self.user_cloud))
        self.rdsFixture = self.useFixture(fixture_rds.RdsFixture(self.user_cloud))

        self.vpcFixture.createTestSubnet1(self.prefix)
        self.cmkFixture.aquireTestKey(self.test_suite_prefix)
        self.rdsFixture.createTestSecGroupRds1(self.prefix)
        self.rdsFixture.createTestRds1(self.prefix, self.vpcFixture.sn1,
            self.rdsFixture.rds1_sg, self.cmkFixture.key)

    def test_rds_enc_found_update(self):
        db_found = self.user_cloud.rdsv3.get_db(self.rdsFixture.rds1)
        self.assertFalse(db_found is None)
        self.assertTrue( isinstance(db_found, _db.DB) )
        self.assertEqual(db_found.id, self.rdsFixture.rds1.id)

        db_found2 = self.user_cloud.rdsv3.find_db(self.prefix+ "-db1")
        self.assertFalse(db_found2 is None)
        self.assertTrue( isinstance(db_found2, _db.DB) )
        self.assertEqual(db_found2.id, self.rdsFixture.rds1.id)
        

    def tearDown(self):
        super().tearDown()
        
        # check non-existence
        #instances = self.user_cloud.rdsv3.dbs()
        #myClusters = list(filter(lambda inst: inst.name.startswith(self.prefix+ "-db1"), instances))
        #self.assertEqual(len(myClusters), 0)
