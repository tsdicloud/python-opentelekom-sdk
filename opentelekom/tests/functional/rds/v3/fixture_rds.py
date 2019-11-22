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
import time

from openstack import exceptions
from openstack import utils

from openstack.network.v2 import security_group, security_group_rule

from opentelekom.tests.functional import base

from opentelekom.rds.rds_service import Rds3Service

class RdsFixture(fixtures.Fixture):
    """ Fixture for an (encypted) RDS database """ 
    
    def __init__(self, user_cloud):
        self.user_cloud=user_cloud

    def setUp(self):
        super().setUp()
        self.user_cloud.add_service(Rds3Service("rdsv3"))

    def createTestSecGroupRds1(self, prefix):
        """ Fixture for a security group """ 
        self.rds1_sg = self.user_cloud.network.create_security_group(name=prefix+"-sg",
            description="Security group for rds1 fixture")
        self.user_cloud.network.create_security_group_rule(
            direction="ingress", ethertype="IPv4",
            port_range_max=22, port_range_min=22,
            protocol="tcp", security_group_id=self.rds1_sg.id)
        self.addCleanup(self._cleanupTestSecGroupRds1)

    def _deleteSecGroup(self, id_or_name):
        secgroup = self.user_cloud.network.find_security_group(id_or_name)
        if secgroup is not None:
            
            rules = self.user_cloud.network.security_group_rules(security_group_id=secgroup.id)    
            for rule in rules:
                self.user_cloud.network.delete_security_group_rule(rule)
            self.user_cloud.network.delete_security_group(secgroup)

    def _cleanupTestSecGroupRds1(self):
        if hasattr(self, 'rds1_sg') and self.rds1_sg is not None:
            # we have to wait until cluster really disappears from network
            for count in utils.iterate_timeout(
                timeout=500,
                message="Timeout deleting rds security group",
                wait=10):
                try:
                    return self.user_cloud.network.delete_security_group(self.rds1_sg)
                except exceptions.ConflictException:
                    pass


    def createTestRds1(self, prefix, subnet, secgroup, key):
        vpc_id=subnet.vpc_id
        self.rds1 = self.user_cloud.rdsv3.create_db(
            name=prefix+"-db1",
            datastore = {
                'type': 'mysql',
                'version': "5.7"
            }, 
            flavor_ref="rds.mysql.c2.medium",
            volume= {
                'type': 'COMMON',
                'size': 100
            },
            disk_encryption_id=key.id,
            region="eu-de",
            availability_zone="eu-de-01",
            vpc_id=vpc_id,
            subnet_id=subnet.id,
            security_group_id=secgroup.id,
            password="Test@12345678")
            # region=self.user_cloud.session.get_project_id(),
        self.addCleanup(self._cleanupTestRds1)
        #self.user_cloud.rdsv3.wait_for_db_job(self.rds1)
        self.user_cloud.rdsv3.wait_for_status(self.rds1)


    def _cleanupTestRds1(self):
        if hasattr(self, 'rds1') and self.rds1 is not None:
            rds_job = self.user_cloud.rdsv3.delete_db(self.rds1)
            self.user_cloud.rdsv3.wait_for_delete(rds_job)
            #self.user_cloud.rdsv3.wait_for_db_job(rds_job)
            # add some additional idle time because the network required some time to register that the resource is really deleted

