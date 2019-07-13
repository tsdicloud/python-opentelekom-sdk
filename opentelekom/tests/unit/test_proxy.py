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

from opentelekom.cce import cce_service
from opentelekom import otc_proxy

from opentelekom.tests.unit.otc_mockservice import OtcMockService, OtcMockResponse 

from opentelekom.tests.functional import base

class TestOtcProxy(base.BaseFunctionalTest):

    def setUp(self):
        super().setUp()

        self.prefix = "rbe-sdkunit-proxy"
        self.user_cloud.add_service( cce_service.CceService("ccev2.0", aliases=["cce2"]) )


    class MockNodesActiveList(OtcMockService):
        responses = [
            OtcMockResponse(method="GET",
                        url_match="cce",
                        path="/api/v3/projects/0391e4486e864c26be5654c522f440f2/clusters/0aa55501-a3e8-11e9-9e49-0255ac101611/nodes",
                        status_code=200,
                        max_calls=2,
                        json= {"kind":"List","apiVersion":"v3","items":[
                            {"kind":"Node","apiVersion":"v3","metadata":{"name":"rbe-sdkunit-proxy-node-t4ywk","uid":"65a87e5d-a3e9-11e9-92b3-0255ac101711","creationTimestamp":"2019-07-11 14:37:23.976068 +0000 UTC","updateTimestamp":"2019-07-11 14:41:20.812487 +0000 UTC","annotations":{"kubernetes.io/node-pool.id":"eu-de-01#s2.large.1#EulerOS 2.2"}},"spec":{"flavor":"s2.large.1","az":"eu-de-01","os":"EulerOS 2.2","login":{"sshKey":"dummy-key","userPassword":{}},"rootVolume":{"volumetype":"SATA","size":100},"dataVolumes":[{"volumetype":"SATA","size":150}],"publicIP":{"eip":{"bandwidth":{}}},"nodeNicSpec":{"primaryNic":{}},"billingMode":0},"status":{"phase":"Active","serverId":"fc65016a-f558-4095-8258-2dcc8e7a2f7a","privateIP":"10.248.2.138"}},
                            {"kind":"Node","apiVersion":"v3","metadata":{"name":"rbe-sdkunit-proxy-node-n8u63","uid":"65a9727f-a3e9-11e9-92b3-0255ac101711","creationTimestamp":"2019-07-11 14:37:23.982322 +0000 UTC","updateTimestamp":"2019-07-11 14:41:20.641575 +0000 UTC","annotations":{"kubernetes.io/node-pool.id":"eu-de-01#s2.large.1#EulerOS 2.2"}},"spec":{"flavor":"s2.large.1","az":"eu-de-01","os":"EulerOS 2.2","login":{"sshKey":"dummy-key","userPassword":{}},"rootVolume":{"volumetype":"SATA","size":100},"dataVolumes":[{"volumetype":"SATA","size":150}],"publicIP":{"eip":{"bandwidth":{}}},"nodeNicSpec":{"primaryNic":{}},"billingMode":0},"status":{"phase":"Creating","serverId":"f8e3b401-d191-43d3-b828-ee67f060aee7","privateIP":"10.248.6.110"}},
                            {"kind":"Node","apiVersion":"v3","metadata":{"name":"rbe-sdkunit-proxy-node-lnmtx","uid":"65a73294-a3e9-11e9-92b3-0255ac101711","creationTimestamp":"2019-07-11 14:37:23.967580 +0000 UTC","updateTimestamp":"2019-07-11 14:41:20.815918 +0000 UTC","annotations":{"kubernetes.io/node-pool.id":"eu-de-01#s2.large.1#EulerOS 2.2"}},"spec":{"flavor":"s2.large.1","az":"eu-de-01","os":"EulerOS 2.2","login":{"sshKey":"dummy-key","userPassword":{}},"rootVolume":{"volumetype":"SATA","size":100},"dataVolumes":[{"volumetype":"SATA","size":150}],"publicIP":{"eip":{"bandwidth":{}}},"nodeNicSpec":{"primaryNic":{}},"billingMode":0},"status":{"phase":"Active","serverId":"df6e4fa8-75b0-4a36-b182-7bc6bee5b0c6","privateIP":"10.248.7.196"}}]}
                        ),
            OtcMockResponse(method="GET",
                        url_match="cce",
                        path="/api/v3/projects/0391e4486e864c26be5654c522f440f2/clusters/0aa55501-a3e8-11e9-9e49-0255ac101611/nodes",
                        status_code=200,
                        max_calls=1,
                        json= {"kind":"List","apiVersion":"v3","items":[
                            {"kind":"Node","apiVersion":"v3","metadata":{"name":"rbe-sdkunit-proxy-node-t4ywk","uid":"65a87e5d-a3e9-11e9-92b3-0255ac101711","creationTimestamp":"2019-07-11 14:37:23.976068 +0000 UTC","updateTimestamp":"2019-07-11 14:41:20.812487 +0000 UTC","annotations":{"kubernetes.io/node-pool.id":"eu-de-01#s2.large.1#EulerOS 2.2"}},"spec":{"flavor":"s2.large.1","az":"eu-de-01","os":"EulerOS 2.2","login":{"sshKey":"dummy-key","userPassword":{}},"rootVolume":{"volumetype":"SATA","size":100},"dataVolumes":[{"volumetype":"SATA","size":150}],"publicIP":{"eip":{"bandwidth":{}}},"nodeNicSpec":{"primaryNic":{}},"billingMode":0},"status":{"phase":"Active","serverId":"fc65016a-f558-4095-8258-2dcc8e7a2f7a","privateIP":"10.248.2.138"}},
                            {"kind":"Node","apiVersion":"v3","metadata":{"name":"rbe-sdkunit-proxy-node-n8u63","uid":"65a9727f-a3e9-11e9-92b3-0255ac101711","creationTimestamp":"2019-07-11 14:37:23.982322 +0000 UTC","updateTimestamp":"2019-07-11 14:41:20.641575 +0000 UTC","annotations":{"kubernetes.io/node-pool.id":"eu-de-01#s2.large.1#EulerOS 2.2"}},"spec":{"flavor":"s2.large.1","az":"eu-de-01","os":"EulerOS 2.2","login":{"sshKey":"dummy-key","userPassword":{}},"rootVolume":{"volumetype":"SATA","size":100},"dataVolumes":[{"volumetype":"SATA","size":150}],"publicIP":{"eip":{"bandwidth":{}}},"nodeNicSpec":{"primaryNic":{}},"billingMode":0},"status":{"phase":"Active","serverId":"f8e3b401-d191-43d3-b828-ee67f060aee7","privateIP":"10.248.6.110"}},
                            {"kind":"Node","apiVersion":"v3","metadata":{"name":"rbe-sdkunit-proxy-node-lnmtx","uid":"65a73294-a3e9-11e9-92b3-0255ac101711","creationTimestamp":"2019-07-11 14:37:23.96758 +0000 UTC","updateTimestamp":"2019-07-11 14:41:20.815918 +0000 UTC","annotations":{"kubernetes.io/node-pool.id":"eu-de-01#s2.large.1#EulerOS 2.2"}},"spec":{"flavor":"s2.large.1","az":"eu-de-01","os":"EulerOS 2.2","login":{"sshKey":"dummy-key","userPassword":{}},"rootVolume":{"volumetype":"SATA","size":100},"dataVolumes":[{"volumetype":"SATA","size":150}],"publicIP":{"eip":{"bandwidth":{}}},"nodeNicSpec":{"primaryNic":{}},"billingMode":0},"status":{"phase":"Active","serverId":"df6e4fa8-75b0-4a36-b182-7bc6bee5b0c6","privateIP":"10.248.7.196"}}]}
                        )
        ]

    @mock.patch.object(requests.Session, "request", side_effect=MockNodesActiveList.request)
    def test_not_mocked_exception(self, mock):
        def _node_selector():
            return self.user_cloud.cce2.cluster_nodes("0aa55501-a3e8-11e9-9e49-000000000")
        with self.assertRaisesRegex(AssertionError, "not mocked!"):
            self.user_cloud.cce2.wait_for_status_all(_node_selector, status="Active", failures=None, interval=1, wait=20, attribute='status')

    @mock.patch.object(requests.Session, "request", side_effect=MockNodesActiveList.request)
    def test_wait_all_ok(self, mock):
        def _node_selector():
            return self.user_cloud.cce2.cluster_nodes("0aa55501-a3e8-11e9-9e49-0255ac101611")
        self.user_cloud.cce2.wait_for_status_all(_node_selector, status="Active", failures=None, interval=1, wait=2000, attribute='status')
        # assertion is done by call limits of mock

    class MockLimitedCall(OtcMockService):
        responses = [
            OtcMockResponse(method="GET",
                        url_match="cce",
                        path="/api/v3/projects/0391e4486e864c26be5654c522f440f2/clusters/0aa55501-a3e8-11e9-9e49-0255ac101611/nodes",
                        status_code=200,
                        max_calls=1,
                        json= {"kind":"List","apiVersion":"v3","items":[
                            {"kind":"Node","apiVersion":"v3","metadata":{"name":"rbe-sdkunit-proxy-node-t4ywk","uid":"65a87e5d-a3e9-11e9-92b3-0255ac101711","creationTimestamp":"2019-07-11 14:37:23.976068 +0000 UTC","updateTimestamp":"2019-07-11 14:41:20.812487 +0000 UTC","annotations":{"kubernetes.io/node-pool.id":"eu-de-01#s2.large.1#EulerOS 2.2"}},"spec":{"flavor":"s2.large.1","az":"eu-de-01","os":"EulerOS 2.2","login":{"sshKey":"dummy-key","userPassword":{}},"rootVolume":{"volumetype":"SATA","size":100},"dataVolumes":[{"volumetype":"SATA","size":150}],"publicIP":{"eip":{"bandwidth":{}}},"nodeNicSpec":{"primaryNic":{}},"billingMode":0},"status":{"phase":"Active","serverId":"fc65016a-f558-4095-8258-2dcc8e7a2f7a","privateIP":"10.248.2.138"}},
                            {"kind":"Node","apiVersion":"v3","metadata":{"name":"rbe-sdkunit-proxy-node-n8u63","uid":"65a9727f-a3e9-11e9-92b3-0255ac101711","creationTimestamp":"2019-07-11 14:37:23.982322 +0000 UTC","updateTimestamp":"2019-07-11 14:41:20.641575 +0000 UTC","annotations":{"kubernetes.io/node-pool.id":"eu-de-01#s2.large.1#EulerOS 2.2"}},"spec":{"flavor":"s2.large.1","az":"eu-de-01","os":"EulerOS 2.2","login":{"sshKey":"dummy-key","userPassword":{}},"rootVolume":{"volumetype":"SATA","size":100},"dataVolumes":[{"volumetype":"SATA","size":150}],"publicIP":{"eip":{"bandwidth":{}}},"nodeNicSpec":{"primaryNic":{}},"billingMode":0},"status":{"phase":"Creating","serverId":"f8e3b401-d191-43d3-b828-ee67f060aee7","privateIP":"10.248.6.110"}},
                            {"kind":"Node","apiVersion":"v3","metadata":{"name":"rbe-sdkunit-proxy-node-lnmtx","uid":"65a73294-a3e9-11e9-92b3-0255ac101711","creationTimestamp":"2019-07-11 14:37:23.967580 +0000 UTC","updateTimestamp":"2019-07-11 14:41:20.815918 +0000 UTC","annotations":{"kubernetes.io/node-pool.id":"eu-de-01#s2.large.1#EulerOS 2.2"}},"spec":{"flavor":"s2.large.1","az":"eu-de-01","os":"EulerOS 2.2","login":{"sshKey":"dummy-key","userPassword":{}},"rootVolume":{"volumetype":"SATA","size":100},"dataVolumes":[{"volumetype":"SATA","size":150}],"publicIP":{"eip":{"bandwidth":{}}},"nodeNicSpec":{"primaryNic":{}},"billingMode":0},"status":{"phase":"Active","serverId":"df6e4fa8-75b0-4a36-b182-7bc6bee5b0c6","privateIP":"10.248.7.196"}}]}
                        ),
        ]

    @mock.patch.object(requests.Session, "request", side_effect=MockLimitedCall.request)
    def test_called_too_often_exception(self, mock):
        def _node_selector():
            return self.user_cloud.cce2.cluster_nodes("0aa55501-a3e8-11e9-9e49-0255ac101611")
        with self.assertRaisesRegex(AssertionError, "more often called"):
            self.user_cloud.cce2.wait_for_status_all(_node_selector, status="Active", failures=None, interval=1, wait=20, attribute='status')

    class MockNodesErrorList(OtcMockService):
        responses = [
            OtcMockResponse(method="GET",
                        url_match="cce",
                        path="/api/v3/projects/0391e4486e864c26be5654c522f440f2/clusters/0aa55501-a3e8-11e9-9e49-0255ac101611/nodes",
                        status_code=200,
                        max_calls=1,
                        json= {"kind":"List","apiVersion":"v3","items":[
                            {"kind":"Node","apiVersion":"v3","metadata":{"name":"rbe-sdkunit-proxy-node-t4ywk","uid":"65a87e5d-a3e9-11e9-92b3-0255ac101711","creationTimestamp":"2019-07-11 14:37:23.976068 +0000 UTC","updateTimestamp":"2019-07-11 14:41:20.812487 +0000 UTC","annotations":{"kubernetes.io/node-pool.id":"eu-de-01#s2.large.1#EulerOS 2.2"}},"spec":{"flavor":"s2.large.1","az":"eu-de-01","os":"EulerOS 2.2","login":{"sshKey":"dummy-key","userPassword":{}},"rootVolume":{"volumetype":"SATA","size":100},"dataVolumes":[{"volumetype":"SATA","size":150}],"publicIP":{"eip":{"bandwidth":{}}},"nodeNicSpec":{"primaryNic":{}},"billingMode":0},"status":{"phase":"Active","serverId":"fc65016a-f558-4095-8258-2dcc8e7a2f7a","privateIP":"10.248.2.138"}},
                            {"kind":"Node","apiVersion":"v3","metadata":{"name":"rbe-sdkunit-proxy-node-n8u63","uid":"65a9727f-a3e9-11e9-92b3-0255ac101711","creationTimestamp":"2019-07-11 14:37:23.982322 +0000 UTC","updateTimestamp":"2019-07-11 14:41:20.641575 +0000 UTC","annotations":{"kubernetes.io/node-pool.id":"eu-de-01#s2.large.1#EulerOS 2.2"}},"spec":{"flavor":"s2.large.1","az":"eu-de-01","os":"EulerOS 2.2","login":{"sshKey":"dummy-key","userPassword":{}},"rootVolume":{"volumetype":"SATA","size":100},"dataVolumes":[{"volumetype":"SATA","size":150}],"publicIP":{"eip":{"bandwidth":{}}},"nodeNicSpec":{"primaryNic":{}},"billingMode":0},"status":{"phase":"Creating","serverId":"f8e3b401-d191-43d3-b828-ee67f060aee7","privateIP":"10.248.6.110"}},
                            {"kind":"Node","apiVersion":"v3","metadata":{"name":"rbe-sdkunit-proxy-node-lnmtx","uid":"65a73294-a3e9-11e9-92b3-0255ac101711","creationTimestamp":"2019-07-11 14:37:23.967580 +0000 UTC","updateTimestamp":"2019-07-11 14:41:20.815918 +0000 UTC","annotations":{"kubernetes.io/node-pool.id":"eu-de-01#s2.large.1#EulerOS 2.2"}},"spec":{"flavor":"s2.large.1","az":"eu-de-01","os":"EulerOS 2.2","login":{"sshKey":"dummy-key","userPassword":{}},"rootVolume":{"volumetype":"SATA","size":100},"dataVolumes":[{"volumetype":"SATA","size":150}],"publicIP":{"eip":{"bandwidth":{}}},"nodeNicSpec":{"primaryNic":{}},"billingMode":0},"status":{"phase":"Creating","serverId":"df6e4fa8-75b0-4a36-b182-7bc6bee5b0c6","privateIP":"10.248.7.196"}}]}
                        ),
            OtcMockResponse(method="GET",
                        url_match="cce",
                        path="/api/v3/projects/0391e4486e864c26be5654c522f440f2/clusters/0aa55501-a3e8-11e9-9e49-0255ac101611/nodes",
                        status_code=200,
                        max_calls=1,
                        json= {"kind":"List","apiVersion":"v3","items":[
                            {"kind":"Node","apiVersion":"v3","metadata":{"name":"rbe-sdkunit-proxy-node-t4ywk","uid":"65a87e5d-a3e9-11e9-92b3-0255ac101711","creationTimestamp":"2019-07-11 14:37:23.976068 +0000 UTC","updateTimestamp":"2019-07-11 14:41:20.812487 +0000 UTC","annotations":{"kubernetes.io/node-pool.id":"eu-de-01#s2.large.1#EulerOS 2.2"}},"spec":{"flavor":"s2.large.1","az":"eu-de-01","os":"EulerOS 2.2","login":{"sshKey":"dummy-key","userPassword":{}},"rootVolume":{"volumetype":"SATA","size":100},"dataVolumes":[{"volumetype":"SATA","size":150}],"publicIP":{"eip":{"bandwidth":{}}},"nodeNicSpec":{"primaryNic":{}},"billingMode":0},"status":{"phase":"Active","serverId":"fc65016a-f558-4095-8258-2dcc8e7a2f7a","privateIP":"10.248.2.138"}},
                            {"kind":"Node","apiVersion":"v3","metadata":{"name":"rbe-sdkunit-proxy-node-n8u63","uid":"65a9727f-a3e9-11e9-92b3-0255ac101711","creationTimestamp":"2019-07-11 14:37:23.982322 +0000 UTC","updateTimestamp":"2019-07-11 14:41:20.641575 +0000 UTC","annotations":{"kubernetes.io/node-pool.id":"eu-de-01#s2.large.1#EulerOS 2.2"}},"spec":{"flavor":"s2.large.1","az":"eu-de-01","os":"EulerOS 2.2","login":{"sshKey":"dummy-key","userPassword":{}},"rootVolume":{"volumetype":"SATA","size":100},"dataVolumes":[{"volumetype":"SATA","size":150}],"publicIP":{"eip":{"bandwidth":{}}},"nodeNicSpec":{"primaryNic":{}},"billingMode":0},"status":{"phase":"Active","serverId":"f8e3b401-d191-43d3-b828-ee67f060aee7","privateIP":"10.248.6.110"}},
                            {"kind":"Node","apiVersion":"v3","metadata":{"name":"rbe-sdkunit-proxy-node-lnmtx","uid":"65a73294-a3e9-11e9-92b3-0255ac101711","creationTimestamp":"2019-07-11 14:37:23.96758 +0000 UTC","updateTimestamp":"2019-07-11 14:41:20.815918 +0000 UTC","annotations":{"kubernetes.io/node-pool.id":"eu-de-01#s2.large.1#EulerOS 2.2"}},"spec":{"flavor":"s2.large.1","az":"eu-de-01","os":"EulerOS 2.2","login":{"sshKey":"dummy-key","userPassword":{}},"rootVolume":{"volumetype":"SATA","size":100},"dataVolumes":[{"volumetype":"SATA","size":150}],"publicIP":{"eip":{"bandwidth":{}}},"nodeNicSpec":{"primaryNic":{}},"billingMode":0},"status":{"phase":"Error","serverId":"df6e4fa8-75b0-4a36-b182-7bc6bee5b0c6","privateIP":"10.248.7.196"}}]}
                        )
        ]

    @mock.patch.object(requests.Session, "request", side_effect=MockNodesErrorList.request)
    def test_wait_all_error(self, mock):
        def _node_selector():
            return self.user_cloud.cce2.cluster_nodes("0aa55501-a3e8-11e9-9e49-0255ac101611")

        with self.assertRaisesRegex(exceptions.ResourceFailure, "transitioned to failure"):
            self.user_cloud.cce2.wait_for_status_all(_node_selector, status="Active", failures=None, interval=1, wait=20, attribute='status')

    class MockNodesDisappearList1(OtcMockService):
        responses = [
            OtcMockResponse(method="GET",
                        url_match="cce",
                        path="/api/v3/projects/0391e4486e864c26be5654c522f440f2/clusters/0aa55501-a3e8-11e9-9e49-0255ac101611/nodes",
                        status_code=200,
                        max_calls=1,
                        json= {"kind":"List","apiVersion":"v3","items":[
                            {"kind":"Node","apiVersion":"v3","metadata":{"name":"rbe-sdkunit-proxy-node-t4ywk","uid":"65a87e5d-a3e9-11e9-92b3-0255ac101711","creationTimestamp":"2019-07-11 14:37:23.976068 +0000 UTC","updateTimestamp":"2019-07-11 14:41:20.812487 +0000 UTC","annotations":{"kubernetes.io/node-pool.id":"eu-de-01#s2.large.1#EulerOS 2.2"}},"spec":{"flavor":"s2.large.1","az":"eu-de-01","os":"EulerOS 2.2","login":{"sshKey":"dummy-key","userPassword":{}},"rootVolume":{"volumetype":"SATA","size":100},"dataVolumes":[{"volumetype":"SATA","size":150}],"publicIP":{"eip":{"bandwidth":{}}},"nodeNicSpec":{"primaryNic":{}},"billingMode":0},"status":{"phase":"Active","serverId":"fc65016a-f558-4095-8258-2dcc8e7a2f7a","privateIP":"10.248.2.138"}},
                            {"kind":"Node","apiVersion":"v3","metadata":{"name":"rbe-sdkunit-proxy-node-n8u63","uid":"65a9727f-a3e9-11e9-92b3-0255ac101711","creationTimestamp":"2019-07-11 14:37:23.982322 +0000 UTC","updateTimestamp":"2019-07-11 14:41:20.641575 +0000 UTC","annotations":{"kubernetes.io/node-pool.id":"eu-de-01#s2.large.1#EulerOS 2.2"}},"spec":{"flavor":"s2.large.1","az":"eu-de-01","os":"EulerOS 2.2","login":{"sshKey":"dummy-key","userPassword":{}},"rootVolume":{"volumetype":"SATA","size":100},"dataVolumes":[{"volumetype":"SATA","size":150}],"publicIP":{"eip":{"bandwidth":{}}},"nodeNicSpec":{"primaryNic":{}},"billingMode":0},"status":{"phase":"Creating","serverId":"f8e3b401-d191-43d3-b828-ee67f060aee7","privateIP":"10.248.6.110"}},
                            {"kind":"Node","apiVersion":"v3","metadata":{"name":"rbe-sdkunit-proxy-node-lnmtx","uid":"65a73294-a3e9-11e9-92b3-0255ac101711","creationTimestamp":"2019-07-11 14:37:23.967580 +0000 UTC","updateTimestamp":"2019-07-11 14:41:20.815918 +0000 UTC","annotations":{"kubernetes.io/node-pool.id":"eu-de-01#s2.large.1#EulerOS 2.2"}},"spec":{"flavor":"s2.large.1","az":"eu-de-01","os":"EulerOS 2.2","login":{"sshKey":"dummy-key","userPassword":{}},"rootVolume":{"volumetype":"SATA","size":100},"dataVolumes":[{"volumetype":"SATA","size":150}],"publicIP":{"eip":{"bandwidth":{}}},"nodeNicSpec":{"primaryNic":{}},"billingMode":0},"status":{"phase":"Creating","serverId":"df6e4fa8-75b0-4a36-b182-7bc6bee5b0c6","privateIP":"10.248.7.196"}}]}
                        ),
            OtcMockResponse(method="GET",
                        url_match="cce",
                        path="/api/v3/projects/0391e4486e864c26be5654c522f440f2/clusters/0aa55501-a3e8-11e9-9e49-0255ac101611/nodes",
                        status_code=200,
                        max_calls=1,
                        json= {"kind":"List","apiVersion":"v3","items":[
                            {"kind":"Node","apiVersion":"v3","metadata":{"name":"rbe-sdkunit-proxy-node-t4ywk","uid":"65a87e5d-a3e9-11e9-92b3-0255ac101711","creationTimestamp":"2019-07-11 14:37:23.976068 +0000 UTC","updateTimestamp":"2019-07-11 14:41:20.812487 +0000 UTC","annotations":{"kubernetes.io/node-pool.id":"eu-de-01#s2.large.1#EulerOS 2.2"}},"spec":{"flavor":"s2.large.1","az":"eu-de-01","os":"EulerOS 2.2","login":{"sshKey":"dummy-key","userPassword":{}},"rootVolume":{"volumetype":"SATA","size":100},"dataVolumes":[{"volumetype":"SATA","size":150}],"publicIP":{"eip":{"bandwidth":{}}},"nodeNicSpec":{"primaryNic":{}},"billingMode":0},"status":{"phase":"Active","serverId":"fc65016a-f558-4095-8258-2dcc8e7a2f7a","privateIP":"10.248.2.138"}},
                            {"kind":"Node","apiVersion":"v3","metadata":{"name":"rbe-sdkunit-proxy-node-n8u63","uid":"65a9727f-a3e9-11e9-92b3-0255ac101711","creationTimestamp":"2019-07-11 14:37:23.982322 +0000 UTC","updateTimestamp":"2019-07-11 14:41:20.641575 +0000 UTC","annotations":{"kubernetes.io/node-pool.id":"eu-de-01#s2.large.1#EulerOS 2.2"}},"spec":{"flavor":"s2.large.1","az":"eu-de-01","os":"EulerOS 2.2","login":{"sshKey":"dummy-key","userPassword":{}},"rootVolume":{"volumetype":"SATA","size":100},"dataVolumes":[{"volumetype":"SATA","size":150}],"publicIP":{"eip":{"bandwidth":{}}},"nodeNicSpec":{"primaryNic":{}},"billingMode":0},"status":{"phase":"Active","serverId":"f8e3b401-d191-43d3-b828-ee67f060aee7","privateIP":"10.248.6.110"}},
                            {"kind":"Node","apiVersion":"v3","metadata":{"name":"rbe-sdkunit-proxy-node-lnmtx","uid":"65a73294-a3e9-11e9-92b3-0255ac101711","creationTimestamp":"2019-07-11 14:37:23.96758 +0000 UTC","updateTimestamp":"2019-07-11 14:41:20.815918 +0000 UTC","annotations":{"kubernetes.io/node-pool.id":"eu-de-01#s2.large.1#EulerOS 2.2"}},"spec":{"flavor":"s2.large.1","az":"eu-de-01","os":"EulerOS 2.2","login":{"sshKey":"dummy-key","userPassword":{}},"rootVolume":{"volumetype":"SATA","size":100},"dataVolumes":[{"volumetype":"SATA","size":150}],"publicIP":{"eip":{"bandwidth":{}}},"nodeNicSpec":{"primaryNic":{}},"billingMode":0},"status":{"phase":"Deleted","serverId":"df6e4fa8-75b0-4a36-b182-7bc6bee5b0c6","privateIP":"10.248.7.196"}}]}
                        )
        ]

    @mock.patch.object(requests.Session, "request", side_effect=MockNodesDisappearList1.request)
    def test_wait_all_disappear(self, mock):
        def _node_selector():
            return self.user_cloud.cce2.cluster_nodes("0aa55501-a3e8-11e9-9e49-0255ac101611")

        with self.assertRaisesRegex(exceptions.ResourceFailure, "disappeared"):
            self.user_cloud.cce2.wait_for_status_all(_node_selector, status="Active", failures=None, interval=1, wait=20, attribute='status')

    # ==== check wait_for_delete_all ====
    