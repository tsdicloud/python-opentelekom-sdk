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

from opentelekom.dns.dns_service import DnsService


class TestPrivateDns(base.BaseFunctionalTest):

    def setUp(self):
        super().setUp()

        self.prefix = self.test_suite_prefix + "-dns"
        self.zonename = "sdktest."

        self.vpcFixture = self.useFixture(fixture_vpc.VpcFixture(self.user_cloud))
        self.vpcFixture.createTestVpc(self.prefix)    

        self.user_cloud.add_service( DnsService("dns", aliases=['designate'] ))

        self.zone = self.user_cloud.dns.create_zone(
            name=self.zonename,
            description="SDK test private zone",
            zone_type="private",
            email="sdktest@me.to",
            ttl="500",
            router= {
                'router_id': self.vpcFixture.vpc.id
            }
        )
        self.addCleanup(self._cleanupDnsZone)

        self.recordname = "myhost." + self.zonename
        self.record = self.user_cloud.dns.create_recordset(
            zone=self.zone,
            name=self.recordname,
            description="SDK test private zone entry",
            type="A",
            ttl="300",
            records = [ '10.248.99.44', '10.248.99.45' ]
        )
        self.addCleanup(self._cleanupDnsRecord)


    def _cleanupDnsZone(self):
        if hasattr(self, 'zone') and self.zone:
            self.user_cloud.dns.delete_zone(self.zone)


    def _cleanupDnsRecord(self):
        if hasattr(self, 'record') and self.record:
            self.user_cloud.dns.delete_recordset(self.record)


    def test_zone_recordset_found_update(self):
        zone = self.user_cloud.dns.get_zone(self.zone.id)
        self.assertTrue(zone)
        self.assertEqual(zone.id, self.zone.id)
        self.assertEqual(zone.name, self.zone.name)

        zone_again = self.user_cloud.dns.find_zone(name_or_id=self.zonename, type="private")
        self.assertTrue(zone_again)
        self.assertEqual(zone_again.id, self.zone.id)
        self.assertEqual(zone_again.name, self.zone.name)

        zone_update = self.user_cloud.dns.update_zone(self.zone.id, description="bloed")
        self.assertTrue(zone_update)
        self.assertEqual(zone_update.id, self.zone.id)
        self.assertEqual(zone_update.name, self.zone.name)
        self.assertEqual("bloed", zone_update.description)

        record = self.user_cloud.dns.get_recordset(zone=zone_again, recordset=self.record.id)
        self.assertTrue(record)
        self.assertEqual(record.id, self.record.id)
        self.assertEqual(record.name, self.record.name)

        record_again = self.user_cloud.dns.find_recordset(self.record.name, self.zone)
        self.assertTrue(record_again)
        self.assertEqual(record_again.id, self.record.id)
        self.assertEqual(record_again.name, self.record.name)

        record_update = self.user_cloud.dns.update_recordset(self.record.id, zone=self.zone,
            description="bloed", records=["1.2.3.34"])
        self.assertTrue(record_update)
        self.assertEqual(record_update.id, self.record.id)
        self.assertEqual(record_update.name, self.record.name)
        self.assertEqual("bloed", record_update.description)



    def tearDown(self):
        super().tearDown()
