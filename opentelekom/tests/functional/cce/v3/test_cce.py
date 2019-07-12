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

from opentelekom.tests.functional.vpc.v1 import fixture_vpc
from opentelekom.tests.functional.cce.v3 import fixture_cce


from opentelekom.vpc.vpc_service import VpcService
from opentelekom.cce.cce_service import CceService

from opentelekom.cce.v3 import cluster

class TestCce2(base.BaseFunctionalTest):

    def setUp(self, **kwargs):
        super().setUp()

        self.prefix = self.test_suite_prefix + "-cce"

        self.vpcFixture  = self.useFixture(fixture_vpc.VpcFixture(self.user_cloud))
        self.cce2Fixture = self.useFixture(fixture_cce.Cce2Fixture(self.user_cloud))

        self.vpcFixture.createTestSubnet1(self.prefix)
        self.cce2Fixture.createTestCluster(prefix=self.prefix, subnet=self.vpcFixture.sn1)
        self.cce2Fixture.createSomeNodes1(prefix=self.prefix, ssh_key=self.test_suite_ssh_key)



    def check_list(self):
        clusters = list(self.user_cloud.cce2.clusters())
        self.assertGreater(len(clusters), 0)
        cluster_found = list(filter(lambda x: x['name'] == self.prefix +"-cce2", clusters ))
        self.assertEqual(len(cluster_found), 1)

    def check_name_id(self):
        '''TODO Move to unit tests
           Check that for some cases, the metadata.uid is set by setting the standard openstack id'''
        found_cluster = self.user_cloud.cce2._get_resource(cluster.Cluster, "123456789")
        self.assertEqual(found_cluster.id, "123456789")

        found_cluster.id = "987654321"
        self.assertEqual(found_cluster.id, "987654321")
        self.assertEqual(found_cluster.metadata.uid, "987654321")

        found_cluster.name = "xxx"
        self.assertEqual(found_cluster.name, "xxx")
        self.assertEqual(found_cluster.metadata.name, "xxx")


    def check_get(self):
        found_cluster = self.user_cloud.cce2.get_cluster(self.cce2Fixture.cce2.id)
        self.assertTrue(found_cluster)
        self.assertEqual(found_cluster.id, self.cce2Fixture.cce2.id)
        self.assertEqual(found_cluster.name, self.cce2Fixture.cce2.name)


    def check_find(self):
        found_cluster = self.user_cloud.cce2.find_cluster(self.cce2Fixture.cce2.name)
        self.assertTrue(found_cluster)
        self.assertEqual(found_cluster.id, self.cce2Fixture.cce2.id)

    # def check_update(self):

    def test_cluster(self):
        '''We want to use cleanup, so we have to chunk the functional test not by test_ methods
        A non-obvious case for subTests to continue testing even if parts fail'''
        with self.subTest(msg="TODO move to unittest: Check handling of special attrs"):
            self.check_name_id()
        with self.subTest(msg="Stage 1: Test Cce cluster list"):
            self.check_list()
        with self.subTest(msg="Stage 2: Test Cce cluster get"):
            self.check_get()
        with self.subTest(msg="Stage 3: Test Cce cluster find"):
            self.check_find()


    def tearDown(self):
        super().tearDown()
