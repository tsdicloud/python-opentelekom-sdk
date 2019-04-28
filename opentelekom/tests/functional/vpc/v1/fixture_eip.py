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
from openstack.network.v2 import network as _net

from opentelekom.tests.functional import base

class EipFixture(fixtures.Fixture):
    """ This is a fixture mixin for vpc features """

    def __init__(self, user_cloud):
        self.user_cloud=user_cloud

    def aquireEIP(self):
        external_networks = list(self.user_cloud.network.networks(is_router_external=True,
            project_id=self.user_cloud.session.get_project_id()))
        if not external_networks:
            raise exceptions.InvalidResourceQuery(message="No external network found in project for EIP creation")
        external_network = external_networks[0]

        # try to find a free eip first
        eips = self.user_cloud.network.ips(
            floating_network_id=external_network.id,
            project_id=self.user_cloud.session.get_project_id())
        eips = list(filter( lambda ip: ip.port_id is None, eips))
        if eips:
            eip = eips[0]
        else:
            # if none found: allocate a new EIP
            eip = self.user_cloud.network.create_ip(
                floating_network_id=external_network.id)
 
        # create book-keeping of eips for potential cleanup
        if not hasattr(self, 'eips'):
            self.eips = list()
        if eip is not None:    
            self.eips.append(eip)
        return eip

    def cleanupEIPs(self):
        """ In this case, cleanup is not associated automatically
            if you NOT want to reuse EIPs, add self.cleanup(self.cleanupEIPs)
            to your setup code after creation of each EIP """
        if hasattr(self, 'eips'):
            while self.eips:
                eip = self.eips.pop()
                self.user_cloud.network.delete_ip(eip)