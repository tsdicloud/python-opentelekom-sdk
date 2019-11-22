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

from opentelekom.csbs.csbs_service import CsbsService
from opentelekom.csbs.v1 import policy

class CsbsFixture(fixtures.Fixture):
    """ Fixture for an (encypted) RDS database """ 
    
    def __init__(self, user_cloud):
        self.user_cloud=user_cloud


    def setUp(self):
        super().setUp()
        self.user_cloud.add_service(CsbsService("karbor", aliases=["csbs"]))


    def createTestSecGroupCsbs1(self, prefix):
        """ Fixture for a security group """ 
        self.csbs1_sg = self.user_cloud.network.create_security_group(name=prefix+"-sg",
            description="Security group for csbs server fixture")
        self.user_cloud.network.create_security_group_rule(
            direction="ingress", ethertype="IPv4",
            port_range_max=22, port_range_min=22,
            protocol="tcp", security_group_id=self.csbs1_sg.id)
        self.addCleanup(self._cleanupTestSecGroupCsbs1)


    def _deleteSecGroupCsbs1(self, id_or_name):
        secgroup = self.user_cloud.network.find_security_group(id_or_name)
        if secgroup is not None:
            
            rules = self.user_cloud.network.security_group_rules(security_group_id=secgroup.id)    
            for rule in rules:
                self.user_cloud.network.delete_security_group_rule(rule)
            self.user_cloud.network.delete_security_group(secgroup)


    def _cleanupTestSecGroupCsbs1(self):
        if hasattr(self, 'csbs1_sg') and self.csbs1_sg is not None:
            # we have to wait until cluster really disappears from network
            for count in utils.iterate_timeout(
                timeout=500,
                message="Timeout deleting rds security group",
                wait=10):
                try:
                    return self.user_cloud.network.delete_security_group(self.csbs1_sg)
                except exceptions.ConflictException:
                    pass


    def createTestSimpleServer(self, prefix, subnet, secgroup, 
            imagename="Standard_CentOS_7_latest", flavorname="s2.medium.1",
            keyname="brederle-master"):
        # TODO: use a pre-created master ssh key for tests!
        flavor_id = self.user_cloud.compute.find_flavor(flavorname).id
        image_id = self.user_cloud.compute.find_image(imagename).id

        self.simplevolume = self.user_cloud.block_storage.create_volume(
            name=prefix + "-simple-vol001",
            image_id=image_id,
            volume_type="SATA",
            size=10)
        self.addCleanup(self._cleanupTestCsbsSimpleVolume)
        self.user_cloud.block_storage.wait_for_status(
            self.simplevolume,
            status='available',
            failures=['error'],
            interval=5)

        self.simpleserver = self.user_cloud.compute.create_server(
            project_id=self.user_cloud.session.get_project_id(),
            name=prefix+"-simple", 
            flavor_id=flavor_id, 
            block_device_mapping=[{ 
                  "boot_index": "0",
                  "source_type": "volume",
                  "destination_type": "volume",
                  "uuid": self.simplevolume.id
                }],
            networks=[{"uuid": subnet.id}], 
            key_name=keyname,
            security_groups = [{ "id": secgroup.id }] )
        self.addCleanup(self._cleanupTestCsbsSimpleServer)
        self.user_cloud.compute.wait_for_server(self.simpleserver, interval=5)


    def _cleanupTestCsbsSimpleServer(self):
        if hasattr(self, 'simpleserver') and self.simpleserver is not None:
            self.user_cloud.compute.delete_server(self.simpleserver)
            self.user_cloud.compute.wait_for_delete(self.simpleserver)


    def _cleanupTestCsbsSimpleVolume(self):
        if hasattr(self, 'simplevolume') and self.simplevolume is not None:
            self.user_cloud.block_storage.delete_volume(self.simplevolume)
            self.user_cloud.block_storage.wait_for_delete(self.simplevolume)
            # add some additional idle time because the network required some time to register that the resource is really deleted

    
    def createTestCsbsPolicy(self, prefix, servers):

        serverResourceList = [ policy.ResourceSpec(
                id = server.id,
                os_type = "OS::Nova::Server"
            ) for server in servers ]

        self.policy = self.user_cloud.csbs.create_policy(
            name=prefix+"policy1",
            description="Opentelekom SDK CSBS test policy",
            parameters=policy.ParameterSpec(),
            resources= serverResourceList,
            scheduled_operations=policy.ScheduledOperationSpec(
                enabled=True,
                name=prefix+"scheduling1",
                decription="Opentelekom SDK CSBS test schedule",
                operation_type="backup",
                operation_definition = policy.OperationDefinitionSpec(
                    max_backups = "-1",
                    retention_duration_days = "1"
                ),
                trigger = policy.TriggerSpec( 
                    properties = policy.TriggerPropertiesSpec(
                        pattern = "BEGIN:VCALENDAR\r\nBEGIN:VEVENT\r\nRRULE:FREQ=WEEKLY;BYDAY=TH;BYHOUR=12;BYMINUTE=27\r\nEND:VEVENT\r \nEND:VCALENDAR\r\n"
                ))
            )
        )
        self.addCleanup(self._cleanupTestPolicy)


    def _cleanupTestPolicy(self):
        if hasattr(self, 'policy') and self.policy is not None:
            policy_job = self.user_cloud.csbs.delete_policy(self.policy)
            self.user_cloud.csbs.wait_for_delete(policy_job)