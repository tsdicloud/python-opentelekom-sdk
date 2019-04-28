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

from opentelekom.vpc.vpc_service import VpcService
from opentelekom.rds.rds_service import Rds3Service

from opentelekom.rds.v3 import instance as _db


class TestDB(base.BaseFunctionalTest):

    def setUp(self):
        super().setUp()
        self.user_cloud.add_service(VpcService("vpc"))
        self.user_cloud.add_service(Rds3Service("rdsv3"))

        self.VPC_NAME = "rbe-vpc-sdktest-rds3"
        self.SN_NAME = "rbe-sn-sdktest-rds3"

        self.vpc = self.user_cloud.vpc.create_vpc(
            name=self.VPC_NAME,
            cidr="10.248.0.0/16")
        self.addCleanup(self.cleanup_sn)
        self.sn = self.user_cloud.vpc.create_subnet(
            vpc=self.vpc,
            name=self.SN_NAME,
            cidr="10.248.0.0/21",
            gateway_ip="10.248.0.1"
            )
        self.addCleanup(self.cleanup_vpc)
        self.user_cloud.vpc.wait_for_status(self.sn)

        self.SEC_GROUP = "rbe-sec-sdktest-rds3"
        self.secgroup = self.user_cloud.network.create_security_group(name=self.SEC_GROUP,
          description="Rds3 cluster access control")
        assert isinstance(self.secgroup, security_group.SecurityGroup)
        self.assertEqual(self.SEC_GROUP, self.secgroup.name)
        self.rul = self.user_cloud.network.create_security_group_rule(
            direction="ingress", ethertype="IPv4",
            port_range_max=22, port_range_min=22,
            protocol="tcp", security_group_id=self.secgroup.id)
        assert isinstance(self.rul, security_group_rule.SecurityGroupRule)
        self.addCleanup(self.cleanup_secgroup)
        
        self._prepare_key()

        self.CLUSTERNAME = "rbe-sdktest-rds3"
        # check non-existence
        instances = self.user_cloud.rdsv3.dbs()
        myClusters = list(filter(lambda inst: inst.name.startswith(self.CLUSTERNAME), instances))
        self.assertEqual(len(myClusters), 0)

        # create
        self.db_enc = self.user_cloud.rdsv3.create_db(
            name=self.CLUSTERNAME,
            datastore = {
                'type': 'mysql',
                'version': "5.7"
            }, 
            flavor_ref="rds.mysql.c2.medium",
            volume= {
                'type': 'COMMON',
                'size': 100
            },
            disk_encryption_id=self.key.key_id,
            region="eu-de",
            availability_zone="eu-de-01",
            vpc_id=self.vpc.id,
            subnet_id=self.sn.id,
            security_group_id=self.secgroup.id,
            password="Test@12345678")
            # region=self.user_cloud.session.get_project_id(),
        self.addCleanup(self.cleanup_db)
        self.user_cloud.rdsv3.wait_for_status(self.db_enc)

    def test_cluster_found_update(self):
        db_found = self.user_cloud.rdsv3.get_db(self.db_enc)
        self.assertFalse(db_found is None)
        self.assertTrue( isinstance(db_found, _db.DB) )
        self.assertEqual(db_found.id, self.db_enc.id)
        

    def tearDown(self):
        super().tearDown()


    def cleanup_db(self):
        if self.db_enc is not None:
            self.user_cloud.rdsv3.delete_db(self.db_enc)
            self.user_cloud.rdsv3.wait_for_delete(self.db_enc)
            # subnet still has some delay until it could be deleted, so delay the next clenup
            # a litte bit
            time.sleep(20)
    
    def cleanup_secgroup(self):
        if self.secgroup is not None:
            rules = self.user_cloud.network.security_group_rules(security_group_id=self.secgroup.id)    
            for rule in rules:
                self.user_cloud.network.delete_security_group_rule(rule)
            self.secgroup = self.user_cloud.network.delete_security_group(self.secgroup)

    def cleanup_sn(self):
        if self.sn is not None:
            self.user_cloud.vpc.delete_subnet(subnet=self.sn.id)
            self.user_cloud.vpc.wait_for_delete(self.sn)

    def cleanup_vpc(self):
        if self.vpc is not None:
            self.user_cloud.vpc.delete_vpc(self.vpc.id)


