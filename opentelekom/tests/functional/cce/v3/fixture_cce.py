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
from openstack.network.v2 import security_group, security_group_rule

from opentelekom.tests.functional import base

from opentelekom.cce import cce_service

class Cce2Fixture(fixtures.Fixture):
    """ Fixture for an CSS cluster """ 
    
    def __init__(self, user_cloud):
        self.user_cloud=user_cloud

    def setUp(self):
        super().setUp()
        self.user_cloud.add_service( cce_service.CceService("ccev2.0", aliases=["cce2"]) )

    def createTestCluster(self, prefix, subnet):
        vpc_id=subnet.vpc_id
        self.cce2 = self.user_cloud.cce2.create_cluster( metadata = {
                'name': prefix + "-cce2"
            },
            spec = { 
            "type": "VirtualMachine",
            "flavor": "cce.s1.small",
            "version": "v1.11.3-r1",
            "description": "OpenTelekom SDK test demo cluster",
            "hostNetwork": {
                "vpc": vpc_id,
                "subnet": subnet.id
            },
            "containerNetwork": {
                "mode": "overlay_l2",
                "cidr": "172.16.0.0/16"
            },
        })
        self.addCleanup(self._cleanupTestCluster)
        self.user_cloud.cce2.wait_for_status(self.cce2)


    def _cleanupTestCluster(self):
        if hasattr(self, 'cce2') and self.cce2:
            self.user_cloud.cce2.delete_cluster(self.cce2)
            self.user_cloud.cce2.wait_for_delete(self.cce2)

    def createSomeNodes1(self, prefix, ssh_key):
        self.user_cloud.cce2.create_cluster_node(self.cce2,
            metadata = {
                'name': prefix + "-node"
            },
            spec = {
                'flavor': "s2.large.1",
                'az': "eu-de-01",
                'login': {
                    'sshKey': ssh_key
                },
                "rootVolume": {
                    "size": 100,
                    "volumeType": "SATA"
                },
                "dataVolumes": [{
                    "size": 150,
                    "volumeType": "SATA"
                }],
                'count': 3
            })
        #self.addCleanup(self._cleanupSomeNodes1)
        # the ids are not in the response to the create call,
        # so we need to query afterwards
        self.user_cloud.cce2.wait_for_status_cluster_nodes(self.cce2)


    def _cleanupSomeNodes1(self):
        '''The cleanup is only used if explicitly registered. The cluster deletes nodes on deletion by default'''
        if hasattr(self, 'cce2') and self.cce2:
            self.user_cloud.cce2.delete_cluster_nodes(self.cce2)
            self.user_cloud.cce2.wait_for_delete_cluster_nodes(self.cce2)


    def tearDown(self):
        super().tearDown()

