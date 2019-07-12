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
from openstack import utils

from openstack.network.v2 import security_group, security_group_rule

from opentelekom.css import css_service

class CssFixture(fixtures.Fixture):
    """ Fixture for an CSS cluster """ 
    
    def __init__(self, user_cloud):
        self.user_cloud=user_cloud

    def setUp(self):
        super().setUp()
        self.user_cloud.add_service(css_service.CssService("css"))


    def createTestSecGroupCss(self, prefix):
        """ Fixture for a security group """
        # avoid creation of multiple security groups with the same name
        sg_name = prefix+"-css-sg"
        secgroup = self.user_cloud.network.find_security_group(sg_name)
        if not secgroup:
            self.sg_css = self.user_cloud.network.create_security_group(name=sg_name,
                description="Security group for css fixture")
            self.user_cloud.network.create_security_group_rule(
                direction="ingress", ethertype="IPv4",
                port_range_max=22, port_range_min=22,
                protocol="tcp", security_group_id=self.sg_css.id)
        else:
            self.sg_css = secgroup
        self.addCleanup(self._cleanupTestSecGroupCss)

    def _cleanupTestSecGroupCss(self):
        if hasattr(self, 'sg_css') and self.sg_css:
            for count in utils.iterate_timeout(
                timeout=500,
                message="Timeout deleting rds security group",
                wait=10):
                try:
                    return self.user_cloud.network.delete_security_group(self.sg_css.id)
                except exceptions.ConflictException:
                    pass

    def createTestCss(self, prefix, subnet, secgroup, key):
        vpc_id=subnet.vpc_id
        self.css = self.user_cloud.css.create_cluster( **{ 'name': prefix + "-css", 
            'instanceNum': 1, 
            'instance': {
                "flavorRef": "css.medium.8",
                "volume": {
                    "volume_type": "COMMON",
                    "size": 100
                },
                "nics": {
                    "vpcId": vpc_id,
                    "netId": subnet.id,
                    "securityGroupId": secgroup.id,
                }
            },
            "httpsEnable": "true",
            "diskEncryption": { 
                "systemEncrypted": "1", 
                "systemCmkid": key.id, 
            }
        })
        self.addCleanup(self._cleanupTestCss)
        self.user_cloud.css.wait_for_status(self.css)

    def _cleanupTestCss(self):
        if hasattr(self, 'css') and self.css:
            self.user_cloud.css.delete_cluster(self.css)
            self.user_cloud.css.wait_for_delete(self.css)

    def tearDown(self):
        super().tearDown()

