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

from unittest import mock

from openstack import exceptions

from opentelekom.vpc.vpc_service import VpcService

from opentelekom.tests.functional import base

from opentelekom.tests.unit.vpc.v1 import fixture_vpc
from opentelekom.tests.unit.otc_mockservice import OtcMockService, OtcMockResponse 


class TestVpc(base.BaseFunctionalTest):

    def setUp(self):
        super().setUp()

        self.prefix = "rbe-sdkunit-vpc"

        self.vpcFixture = self.useFixture(fixture_vpc.VpcFixture(self.user_cloud))
        self.vpcFixture.createTestVpc(self.prefix)    

    class MockVpcList(OtcMockService):
        responses = [
            OtcMockResponse(method="GET",
                        url_match="vpc",
                        path="/v1/0391e4486e864c26be5654c522f440f2/vpcs",
                        status_code=200,
                        json={"vpcs":[{"id":"7f4d8a07-df6c-4c86-919f-4fa201463d65","name":"rbe-sdkunit-vpc-vpc","cidr":"10.248.0.0/16","status":"OK","routes":[],"enable_shared_snat":False,"enterprise_project_id":"0"},
                                      {"id":"8865cc93-36d5-410e-9865-57333f370e53","name":"vpc-poc-admin","cidr":"10.19.0.0/16","status":"OK","routes":[],"enable_shared_snat":False,"enterprise_project_id":"0"},
                                      {"id":"aa188bb4-465e-4b35-9d12-72d8ecfe7d1c","name":"vpc-poc-admin5","cidr":"10.13.0.0/16","status":"OK","routes":[],"enable_shared_snat":False,"enterprise_project_id":"0"},
                                      {"id":"dd586f4d-2490-450f-9afe-77f19e44c490","name":"rbe-vpc-profidata-test","cidr":"172.16.0.0/12","status":"OK","routes":[],"enable_shared_snat":False,"enterprise_project_id":"0"}]}
                        )
        ]

    @mock.patch.object(requests.Session, "request", side_effect=MockVpcList().request)
    def test_list_vpcs(self, mock):
         vpcs = list(self.user_cloud.vpc.vpcs())
         self.assertGreater(len(vpcs), 0)
         vpcfound = list(filter(lambda x: x['name'] == self.prefix + "-vpc", vpcs ))
         self.assertEqual(len(vpcfound), 1)

    class MockVpcFind(OtcMockService):
        responses = [
            # detect name or id type by trying value as id first
            OtcMockResponse(method="GET",
                        url_match="vpc",
                        path="/v1/0391e4486e864c26be5654c522f440f2/vpcs/rbe-sdkunit-vpc-vpc",
                        status_code=400,
                        json={"code":"VPC.0101","message":"getVpc error vpcId is invalid."}),
            # name handling is done by search in the list query
            OtcMockResponse(method="GET",
                        url_match="vpc",
                        path="/v1/0391e4486e864c26be5654c522f440f2/vpcs",
                        status_code=200,
                        json={"vpcs":[{"id":"7f4d8a07-df6c-4c86-919f-4fa201463d65","name":"rbe-sdkunit-vpc-vpc","cidr":"10.248.0.0/16","status":"OK","routes":[],"enable_shared_snat":False,"enterprise_project_id":"0"},
                                      {"id":"8865cc93-36d5-410e-9865-57333f370e53","name":"vpc-poc-admin","cidr":"10.19.0.0/16","status":"OK","routes":[],"enable_shared_snat":False,"enterprise_project_id":"0"},
                                      {"id":"aa188bb4-465e-4b35-9d12-72d8ecfe7d1c","name":"vpc-poc-admin5","cidr":"10.13.0.0/16","status":"OK","routes":[],"enable_shared_snat":False,"enterprise_project_id":"0"},
                                      {"id":"dd586f4d-2490-450f-9afe-77f19e44c490","name":"rbe-vpc-profidata-test","cidr":"172.16.0.0/12","status":"OK","routes":[],"enable_shared_snat":False,"enterprise_project_id":"0"}]}
                        )

        ]

    @mock.patch.object(requests.Session, "request", side_effect=MockVpcFind().request)
    def test_find_by_name(self, mock):
        #self.MockVpcFind.assertServicesCalled()
        vpcfound2 = self.user_cloud.vpc.find_vpc(self.prefix + "-vpc")
        self.assertFalse(vpcfound2 is None)
        self.assertEqual(vpcfound2.id, self.vpcFixture.vpc.id)

    class MockVpcUpdate(OtcMockService):
        responses = [
            # update
            OtcMockResponse(method="PUT",
                        url_match="vpc",
                        path="/v1/0391e4486e864c26be5654c522f440f2/vpcs/7f4d8a07-df6c-4c86-919f-4fa201463d65",
                        status_code=200,
                        json={"vpc":{"id":"7f4d8a07-df6c-4c86-919f-4fa201463d65","name":"rbe-sdktest-vpc-vpc","cidr":"10.248.0.0/16","status":"OK","routes":[],"enable_shared_snat": True,"enterprise_project_id":"0"}}),
        ]

    @mock.patch.object(requests.Session, "request", side_effect=MockVpcUpdate().request)
    def test_update(self, mock):
        vpc = self.user_cloud.vpc.update_vpc(self.vpcFixture.vpc.id, enable_shared_snat=True)
        self.assertTrue(vpc)
        self.assertEqual(vpc.id, self.vpcFixture.vpc.id)
        self.assertEqual(vpc.enable_shared_snat, True)

    def tearDown(self):
        super().tearDown()

        
