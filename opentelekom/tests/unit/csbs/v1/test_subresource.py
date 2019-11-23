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
import requests
import unittest
from unittest import mock

from openstack import exceptions

from opentelekom import otc_proxy

from opentelekom.csbs import csbs_service
from opentelekom.csbs.v1 import policy

from opentelekom.tests.unit.otc_mockservice import OtcMockService, OtcMockResponse 

from opentelekom.tests.functional import base


class TestSubREsource(base.BaseFunctionalTest):
    ''' A test for proper handling of sub-resource specifications '''

    def setUp(self):
        super().setUp()

        self.prefix = "rbe-sdkunit-subresource"

    # description="Opentelekom SDK CSBS test schedule",


    def test_spec_nonone(self):
        scheduled_operation = policy.ScheduledOperationSpec(
            enabled=True,
            name=self.prefix+"scheduling1",
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

        # description="Opentelekom SDK CSBS test policy",
        pol = policy.Policy(
            name=self.prefix+"policy1",
           parameters=policy.PolicyParametersSpec(),
            resources=[ policy.ResourceSpec(
                id = "1",
                type = "OS::Nova::Server",
                name = "SimpleServer bak" ) ],
            scheduled_operations= [ scheduled_operation ]
        )
        #result = scheduled_operation.to_dict()

        req = pol._prepare_request(requires_id=False)
        import pdb; pdb.set_trace()        
