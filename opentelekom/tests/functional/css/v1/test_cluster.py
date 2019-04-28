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

from opentelekom.vpc.vpc_service import VpcService
from opentelekom.css.css_service import CssService

class TestCluster(base.BaseFunctionalTest):

    def setUp(self):
        super().setUp()
        self.user_cloud.add_service(VpcService("vpc"))
        self.user_cloud.add_service(CssService("css"))

        self.VPC_NAME = "rbe-vpc-sdktest-css"
        self.SN_NAME = "rbe-sn-sdktest-css"
        self.vpc = self.user_cloud.vpc.create_vpc(
            name=self.VPC_NAME,
            cidr="10.249.0.0/16")
        self.sn = self.user_cloud.vpc.create_subnet(
            vpc=self.vpc,
            name=self.SN_NAME,
            cidr="10.249.0.0/21",
            gateway_ip="10.249.0.1"
            )
        self.user_cloud.vpc.wait_for_status(self.sn)

        self.SEC_GROUP = "rbe-sec-sdktest-css"
        self.secgroup = self.user_cloud.network.create_security_group(name=self.SEC_GROUP,
          description="Css cluster access control")
        assert isinstance(self.secgroup, security_group.SecurityGroup)
        self.assertEqual(self.SEC_GROUP, self.secgroup.name)
        self.rul = self.user_cloud.network.create_security_group_rule(
            direction="ingress", ethertype="IPv4",
            port_range_max=22, port_range_min=22,
            protocol="tcp", security_group_id=self.secgroup.id)
        assert isinstance(self.rul, security_group_rule.SecurityGroupRule)
        self.CLUSTERNAME = "rbe-css-sdktest1"
        self._prepare_key()

        instanceSpec = {
            "flavorRef": "css.medium.8",
            "volume": {
                "volume_type": "COMMON",
                "size": 100
            },
            "nics": {
                "vpcId": self.vpc.id,
                "netId": self.sn.id,
                "securityGroudId": self.secgroup.id
            }
        }
        self.cluster = self.user_cloud.css.create_css(name=self.CLUSTERNAME, instanceNum=2, 
            instance=instanceSpec, diskEncryption={ "systemEncrypted": "1", "systemCmkid": self.key.key_id })
        self.conn.user_cloud.css.wait_for_status(self.cluster)

    def test_cluster_found_update(self):
        clusters = list(self.user_cloud.css.clusters())
        self.assertGreater(len(clusters), 0)
        cluster_found = list(filter(lambda x: x['name'] == self.CLUSTERNAME, clusters ))
        self.assertEqual(len(cluster_found), 1)
    
        # TODO: restart, expand tests

        found_cluster = self.user_cloud.cluster.get_cluster(self.cluster.id)
        self.assertFalse(found_cluster is not None)
        self.assertEqual(found_cluster.id, self.cluster.id)
        self.assertEqual(found_cluster.name, self.cluster.name)

    def tearDown(self):
        super().tearDown()
        if self.cluster is not None:
            self.user_cloud.css.delete_css(self.cluster)
            self.user_cloud.css.wait_for_delete(self.cluster)
        if self.secgroup is not None:
            rules = self.user_cloud.network.security_group_rules(security_group_id=self.secgroup.id)    
            for rule in rules:
                self.user_cloud.network.delete_security_group_rule(rule)
            self.secgroup = self.user_cloud.network.delete_security_group(self.secgroup)
        if self.sn is not None:
            self.user_cloud.vpc.delete_subnet(subnet=self.sn.id)
            self.user_cloud.vpc.wait_for_delete(self.sn)
        if self.vpc is not None:
            self.user_cloud.vpc.delete_vpc(self.vpc.id)


