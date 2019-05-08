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
from opentelekom.tests.functional import base
from opentelekom.tests.functional.vpc.v1 import fixture_vpc
from opentelekom.tests.functional.kms.v1 import fixture_kms
from opentelekom.tests.functional.css.v1 import fixture_css


from opentelekom.vpc.vpc_service import VpcService
from opentelekom.css.css_service import CssService

class TestCluster(base.BaseFunctionalTest):

    def setUp(self):
        super().setUp()

        self.prefix = "rbe-sdktest-css"

        self.vpcFixture = self.useFixture(fixture_vpc.VpcFixture(self.user_cloud))
        self.cmkFixture = self.useFixture(fixture_kms.KmsFixture(self.user_cloud))
        self.cssFixture = self.useFixture(fixture_css.CssFixture(self.user_cloud))

        self.vpcFixture.createTestSubnet1(self.prefix)
        self.cmkFixture.aquireTestKey("rbe-sdktest")
        self.cssFixture.createTestSecGroupCss(self.prefix)
        self.cssFixture.createTestCss(prefix=self.prefix, subnet=self.vpcFixture.sn1,
            secgroup=self.cssFixture.sg_css, key=self.cmkFixture.key)

    def test_cluster_found_update(self):
        clusters = list(self.user_cloud.css.clusters())
        self.assertGreater(len(clusters), 0)
        cluster_found = list(filter(lambda x: x['name'] == self.prefix +"-css", clusters ))
        self.assertEqual(len(cluster_found), 1)
    
        # TODO: restart, expand tests

        found_cluster = self.user_cloud.cluster.get_cluster(self.css.id)
        self.assertFalse(found_cluster is not None)
        self.assertEqual(found_cluster.id, self.css.id)
        self.assertEqual(found_cluster.name, self.css.name)

        found_again = self.user_cloud.cluster.find_cluster(self.css.name)
        self.assertTrue(found_again)
        self.assertEqual(found_again.id, self.css.id)


    def tearDown(self):
        super().tearDown()
