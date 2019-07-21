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


def _match_spec(res, **params):
    '''Find/compare nodes given a specification of the node.
       login and count are ignored beacause we want to has a
       match on technical resource tape and size'''
    
    if ( not res.metadata.name.startswith( params['name']) ):
        return False

    # check basic compute spec
    if ( res.spec.flavor != params['flavor'] or 
            res.spec.availability_zone != params['availability_zone'] ):
        return False

    # check root volume spec
    if (res.spec.root_volume.size != int(params['root_volume']['size']) or
            res.spec.root_volume.type != params['root_volume']['type']):
        return False

    # TODO public_ip is not considered yet
    #if (( hasattr(res.spec.public_ip, 'ids') and res.spec.public_ip.ids != module.params['public_ip']['ids'] ) or
    #        ( hasattr(res.spec.public_ip, 'floating_ip') and
    #            res.public_ip.spec.floating_ip.type != module.params['public_ip']['type'] or
    #            res.public_ip.spec.floating_ip.bandwidth.size != module.params['public_ip']['bandwidth'] or
    #            res.public_ip.spec.floating_ip.bandwidth.sharetype  != module.params['public_ip']['sharetype']  or
    #            res.public_ip.spec.count != module.params['public_ip']['count'] )):
    #    return False
    
    # list of data volumes must have the same size
    if len(res.spec.data_volumes) != len(params['data_volumes']):
        return False

    # if they have the same size, element in the list must have a
    # corresponding on in the other (both ways!)
    volumes = res.spec.data_volumes.copy()
    for volspec in params['data_volumes']:
        found = False
        for volpos, volres in enumerate(volumes):
            if (volres.type == volspec['type'] and 
                    volres.size == int(volspec['size']) ):
                # consume matching entry (to handle dupicates properly)
                volumes.pop(volpos)
                found = True
                break
        # a spec is not contained
        if not found:
            return False

    # at the end, all data_volumes from node must be consumed
    if volumes:
        # node has more volumes than spec
        return False

    return True


def _filter_for_delete(cloud, cluster_id, **params):
    nodes = list(cloud.cce2.cluster_nodes(cluster_id))
    if 'name' in params:
        nodes = filter( lambda res: res.name.startswith(params['name']), nodes )
    if 'flavor' in params:
        nodes = filter( lambda res: res.spec.flavor == params['flavor'], nodes )
    if 'availability_zone' in params:
        nodes = filter( lambda res: res.spec.availability_zone == params['availability_zone'], nodes )
    return list(nodes)

class TestNodeFiltering(base.BaseFunctionalTest):
    ''' A test to debug the filters used in the ansible module for cce nodes'''

    class Module:
        def __init__(self, params):
            self.params=params

    def setUp(self):
        super().setUp()

        self.prefix = "rbe-sdkunit-filter"
        self.cluster_id="0aa55501-a3e8-11e9-9e49-0255ac101611"
        self.user_cloud.add_service( cce_service.CceService("ccev2.0", aliases=["cce2"]) )

        self.module = self.Module({
            'name': self.prefix + "-node",
            'flavor': "s2.large.1",
            'availability_zone': "eu-de-01",
            'root_volume': {
                'type': "SATA",
                'size': "100"
            },
            'data_volumes': [
                {
                    'type': "SATA",
                    'size': "150"
                }
            ]
        })



    class MockNodesActiveList(OtcMockService):
        responses = [
            OtcMockResponse(method="GET",
                        url_match="cce",
                        path="/api/v3/projects/0391e4486e864c26be5654c522f440f2/clusters/0aa55501-a3e8-11e9-9e49-0255ac101611/nodes",
                        status_code=200,
                        json= {"kind":"List","apiVersion":"v3","items":[
                            {"kind":"Node","apiVersion":"v3","metadata":{"name":"rbe-sdkunit-filter-node-t4ywk","uid":"65a87e5d-a3e9-11e9-92b3-0255ac101711","creationTimestamp":"2019-07-11 14:37:23.976068 +0000 UTC","updateTimestamp":"2019-07-11 14:41:20.812487 +0000 UTC","annotations":{"kubernetes.io/node-pool.id":"eu-de-01#s2.large.1#EulerOS 2.2"}},"spec":{"flavor":"s2.large.1","az":"eu-de-01","os":"EulerOS 2.2","login":{"sshKey":"dummy-key","userPassword":{}},"rootVolume":{"volumetype":"SATA","size":100},"dataVolumes":[{"volumetype":"SATA","size":150}],"publicIP":{"eip":{"bandwidth":{}}},"nodeNicSpec":{"primaryNic":{}},"billingMode":0},"status":{"phase":"Active","serverId":"fc65016a-f558-4095-8258-2dcc8e7a2f7a","privateIP":"10.248.2.138"}},
                            {"kind":"Node","apiVersion":"v3","metadata":{"name":"rbe-sdkunit-filter-node-n8u63","uid":"65a9727f-a3e9-11e9-92b3-0255ac101711","creationTimestamp":"2019-07-11 14:37:23.982322 +0000 UTC","updateTimestamp":"2019-07-11 14:41:20.641575 +0000 UTC","annotations":{"kubernetes.io/node-pool.id":"eu-de-01#s2.large.1#EulerOS 2.2"}},"spec":{"flavor":"s2.large.1","az":"eu-de-01","os":"EulerOS 2.2","login":{"sshKey":"dummy-key","userPassword":{}},"rootVolume":{"volumetype":"SATA","size":100},"dataVolumes":[{"volumetype":"SATA","size":150}],"publicIP":{"eip":{"bandwidth":{}}},"nodeNicSpec":{"primaryNic":{}},"billingMode":0},"status":{"phase":"Active","serverId":"f8e3b401-d191-43d3-b828-ee67f060aee7","privateIP":"10.248.6.110"}},
                            {"kind":"Node","apiVersion":"v3","metadata":{"name":"rbe-sdkunit-filter-node-lnmtx","uid":"65a73294-a3e9-11e9-92b3-0255ac101711","creationTimestamp":"2019-07-11 14:37:23.96758 +0000 UTC","updateTimestamp":"2019-07-11 14:41:20.815918 +0000 UTC","annotations":{"kubernetes.io/node-pool.id":"eu-de-01#s2.large.1#EulerOS 2.2"}},"spec":{"flavor":"s2.large.1","az":"eu-de-01","os":"EulerOS 2.2","login":{"sshKey":"dummy-key","userPassword":{}},"rootVolume":{"volumetype":"SATA","size":100},"dataVolumes":[{"volumetype":"SSD","size":150}],"publicIP":{"eip":{"bandwidth":{}}},"nodeNicSpec":{"primaryNic":{}},"billingMode":0},"status":{"phase":"Active","serverId":"df6e4fa8-75b0-4a36-b182-7bc6bee5b0c6","privateIP":"10.248.7.196"}},
                            {"kind":"Node","apiVersion":"v3","metadata":{"name":"rbe-sdkunit-filter-node-t4ywk","uid":"65a87e6d-a3e9-11e9-92b3-0255ac101711","creationTimestamp":"2019-07-11 14:37:23.976068 +0000 UTC","updateTimestamp":"2019-07-11 14:41:20.812487 +0000 UTC","annotations":{"kubernetes.io/node-pool.id":"eu-de-01#s2.large.1#EulerOS 2.2"}},"spec":{"flavor":"s2.large.1","az":"eu-de-01","os":"EulerOS 2.2","login":{"sshKey":"dummy-key","userPassword":{}},"rootVolume":{"volumetype":"SATA","size":150},"dataVolumes":[{"volumetype":"SATA","size":150}],"publicIP":{"eip":{"bandwidth":{}}},"nodeNicSpec":{"primaryNic":{}},"billingMode":0},"status":{"phase":"Active","serverId":"fc65016a-f558-4095-8258-2dcc8e7a2f7b","privateIP":"10.248.2.139"}},
                            {"kind":"Node","apiVersion":"v3","metadata":{"name":"rbe-sdkunit-filter-node-n8u63","uid":"65a9728f-a3e9-11e9-92b3-0255ac101711","creationTimestamp":"2019-07-11 14:37:23.982322 +0000 UTC","updateTimestamp":"2019-07-11 14:41:20.641575 +0000 UTC","annotations":{"kubernetes.io/node-pool.id":"eu-de-02#s2.large.1#EulerOS 2.2"}},"spec":{"flavor":"s2.large.1","az":"eu-de-02","os":"EulerOS 2.2","login":{"sshKey":"dummy-key","userPassword":{}},"rootVolume":{"volumetype":"SATA","size":100},"dataVolumes":[{"volumetype":"SATA","size":150}],"publicIP":{"eip":{"bandwidth":{}}},"nodeNicSpec":{"primaryNic":{}},"billingMode":0},"status":{"phase":"Active","serverId":"f8e3b401-d191-43d3-b828-ee67f060aee8","privateIP":"10.248.6.111"}},
                            {"kind":"Node","apiVersion":"v3","metadata":{"name":"rbe-sdkunit-filter-node-lnmtx","uid":"65a73295-a3e9-11e9-92b3-0255ac101711","creationTimestamp":"2019-07-11 14:37:23.96758 +0000 UTC","updateTimestamp":"2019-07-11 14:41:20.815918 +0000 UTC","annotations":{"kubernetes.io/node-pool.id":"eu-de-02#s2.large.1#EulerOS 2.2"}},"spec":{"flavor":"s2.large.1","az":"eu-de-02","os":"EulerOS 2.2","login":{"sshKey":"dummy-key","userPassword":{}},"rootVolume":{"volumetype":"SATA","size":100},"dataVolumes":[{"volumetype":"SATA","size":150}],"publicIP":{"eip":{"bandwidth":{}}},"nodeNicSpec":{"primaryNic":{}},"billingMode":0},"status":{"phase":"Active","serverId":"df6e4fa8-75b0-4a36-b182-7bc6bee5b0c7","privateIP":"10.248.7.197"}},
                            {"kind":"Node","apiVersion":"v3","metadata":{"name":"rbe-sdkunit-filter-node-t4ywk","uid":"65a87e5d-a3e9-11e9-92b3-0255ac101711","creationTimestamp":"2019-07-11 14:37:23.976068 +0000 UTC","updateTimestamp":"2019-07-11 14:41:20.812487 +0000 UTC","annotations":{"kubernetes.io/node-pool.id":"eu-de-01#s2.large.4#EulerOS 2.2"}},"spec":{"flavor":"s2.large.4","az":"eu-de-01","os":"EulerOS 2.2","login":{"sshKey":"dummy-key","userPassword":{}},"rootVolume":{"volumetype":"SATA","size":100},"dataVolumes":[{"volumetype":"SATA","size":150}],"publicIP":{"eip":{"bandwidth":{}}},"nodeNicSpec":{"primaryNic":{}},"billingMode":0},"status":{"phase":"Active","serverId":"fc65016a-f558-4095-8258-2dcc8e7a2fcc","privateIP":"10.248.2.140"}},
                            {"kind":"Node","apiVersion":"v3","metadata":{"name":"rbe-sdkunit-filter-node-n8u63","uid":"65a9737f-a3e9-11e9-92b3-0255ac101711","creationTimestamp":"2019-07-11 14:37:23.982322 +0000 UTC","updateTimestamp":"2019-07-11 14:41:20.641575 +0000 UTC","annotations":{"kubernetes.io/node-pool.id":"eu-de-01#s2.large.4#EulerOS 2.2"}},"spec":{"flavor":"s2.large.4","az":"eu-de-01","os":"EulerOS 2.2","login":{"sshKey":"dummy-key","userPassword":{}},"rootVolume":{"volumetype":"SATA","size":100},"dataVolumes":[{"volumetype":"SATA","size":150}],"publicIP":{"eip":{"bandwidth":{}}},"nodeNicSpec":{"primaryNic":{}},"billingMode":0},"status":{"phase":"Active","serverId":"f8e3b401-d191-43d3-b828-ee67f060aee9","privateIP":"10.248.6.112"}},
                            {"kind":"Node","apiVersion":"v3","metadata":{"name":"rbe-sdkunit-filter-node2-n8u63","uid":"65a9747f-a3e9-11e9-92b3-0255ac101711","creationTimestamp":"2019-07-11 14:37:23.982322 +0000 UTC","updateTimestamp":"2019-07-11 14:41:20.641575 +0000 UTC","annotations":{"kubernetes.io/node-pool.id":"eu-de-01#s2.large.4#EulerOS 2.2"}},"spec":{"flavor":"s2.large.4","az":"eu-de-01","os":"EulerOS 2.2","login":{"sshKey":"dummy-key","userPassword":{}},"rootVolume":{"volumetype":"SATA","size":100},"dataVolumes":[{"volumetype":"SATA","size":100},{"volumetype":"SATA","size":200}],"publicIP":{"eip":{"bandwidth":{}}},"nodeNicSpec":{"primaryNic":{}},"billingMode":0},"status":{"phase":"Active","serverId":"f8e3b401-d191-43d3-b828-ee67f060aef0","privateIP":"10.248.6.113"}},
                            {"kind":"Node","apiVersion":"v3","metadata":{"name":"rbe-sdkunit-filter-node2-n8u63","uid":"65a9744f-a3e9-11e9-92b3-0255ac101711","creationTimestamp":"2019-07-11 14:37:23.982322 +0000 UTC","updateTimestamp":"2019-07-11 14:41:20.641575 +0000 UTC","annotations":{"kubernetes.io/node-pool.id":"eu-de-01#s2.large.4#EulerOS 2.2"}},"spec":{"flavor":"s2.large.4","az":"eu-de-01","os":"EulerOS 2.2","login":{"sshKey":"dummy-key","userPassword":{}},"rootVolume":{"volumetype":"SATA","size":100},"dataVolumes":[{"volumetype":"SATA","size":200},{"volumetype":"SATA","size":200}],"publicIP":{"eip":{"bandwidth":{}}},"nodeNicSpec":{"primaryNic":{}},"billingMode":0},"status":{"phase":"Active","serverId":"f8e3b402-d191-43d3-b828-ee67f060aef0","privateIP":"10.248.6.113"}},
                            {"kind":"Node","apiVersion":"v3","metadata":{"name":"rbe-sdkunit-filter-node2-lnmtx","uid":"65a73594-a3e9-11e9-92b3-0255ac101711","creationTimestamp":"2019-07-11 14:37:23.96758 +0000 UTC","updateTimestamp":"2019-07-11 14:41:20.815918 +0000 UTC","annotations":{"kubernetes.io/node-pool.id":"eu-de-01#s2.large.4#EulerOS 2.2"}},"spec":{"flavor":"s2.large.4","az":"eu-de-01","os":"EulerOS 2.2","login":{"sshKey":"dummy-key","userPassword":{}},"rootVolume":{"volumetype":"SATA","size":100},"dataVolumes":[{"volumetype":"SATA","size":150}],"publicIP":{"eip":{"bandwidth":{}}},"nodeNicSpec":{"primaryNic":{}},"billingMode":0},"status":{"phase":"Active","serverId":"df6e4fa8-75b0-4a36-b182-7bc6bee5b0c8","privateIP":"10.248.7.198"}}]}
                        )
        ]


    @mock.patch.object(requests.Session, "request", side_effect=MockNodesActiveList().request)
    def test_match_basic(self, mock):
        spec2module = self.module
        def _match(res):
            return _match_spec(res, **spec2module.params)

        nodes = list(filter(_match, self.user_cloud.cce2.cluster_nodes(self.cluster_id)) )
        self.assertEqual(len(nodes), 2)
        self.assertEqual(nodes[0].id, "65a87e5d-a3e9-11e9-92b3-0255ac101711")
        self.assertEqual(nodes[1].id, "65a9727f-a3e9-11e9-92b3-0255ac101711")

    @mock.patch.object(requests.Session, "request", side_effect=MockNodesActiveList().request)
    def test_match_az(self, mock):
        spec2module = self.module
        spec2module.params['availability_zone'] = 'eu-de-02'
    
        def _match(res):
            return _match_spec(res, **spec2module.params)

        nodes = list(filter(_match, self.user_cloud.cce2.cluster_nodes(self.cluster_id)) )
        self.assertEqual(len(nodes), 2)
        self.assertEqual(nodes[0].id, "65a9728f-a3e9-11e9-92b3-0255ac101711")
        self.assertEqual(nodes[1].id, "65a73295-a3e9-11e9-92b3-0255ac101711")

    @mock.patch.object(requests.Session, "request", side_effect=MockNodesActiveList().request)
    def test_match_flavor(self, mock):
        spec2module = self.module
        spec2module.params['flavor'] = 's2.large.4'
    
        def _match(res):
            return _match_spec(res, **spec2module.params)

        nodes = list(filter(_match, self.user_cloud.cce2.cluster_nodes(self.cluster_id)) )
        self.assertEqual(len(nodes), 3)
        self.assertEqual(nodes[0].id, "65a87e5d-a3e9-11e9-92b3-0255ac101711")
        self.assertEqual(nodes[1].id, "65a9737f-a3e9-11e9-92b3-0255ac101711")
        self.assertEqual(nodes[2].id, "65a73594-a3e9-11e9-92b3-0255ac101711")


    @mock.patch.object(requests.Session, "request", side_effect=MockNodesActiveList().request)
    def test_match_name(self, mock):
        spec2module = self.module
        spec2module.params['flavor'] = 's2.large.4'
        spec2module.params['name'] = 'rbe-sdkunit-filter-node2'
        spec2module.params['data_volumes'][0]['size'] = '150'
    
        def _match(res):
            return _match_spec(res, **spec2module.params)

        nodes = list(filter(_match, self.user_cloud.cce2.cluster_nodes(self.cluster_id)) )
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].id, "65a73594-a3e9-11e9-92b3-0255ac101711")


    @mock.patch.object(requests.Session, "request", side_effect=MockNodesActiveList().request)
    def test_match_data_volume_type(self, mock):
        spec2module = self.module
        spec2module.params['data_volumes'][0]['type'] = 'SSD'

        def _match(res):
            return _match_spec(res, **spec2module.params)

        nodes = list(filter(_match, self.user_cloud.cce2.cluster_nodes(self.cluster_id)) )
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].id, "65a73294-a3e9-11e9-92b3-0255ac101711")

        spec2module.params['data_volumes'][0]['type'] = 'SAS'
        nodes = list(filter(_match, self.user_cloud.cce2.cluster_nodes(self.cluster_id)) )
        self.assertFalse(nodes)


    @mock.patch.object(requests.Session, "request", side_effect=MockNodesActiveList().request)
    def test_match_spec4(self, mock):
        spec2module = self.module
        spec2module.params['root_volume']['size'] = 150
    
        def _match(res):
            return _match_spec(res, **spec2module.params)

        nodes = list(filter(_match, self.user_cloud.cce2.cluster_nodes(self.cluster_id)) )
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].id, "65a87e6d-a3e9-11e9-92b3-0255ac101711")

        spec2module.params['root_volume']['size'] = 200
        nodes = list(filter(_match, self.user_cloud.cce2.cluster_nodes(self.cluster_id)) )
        self.assertFalse(nodes)

    @mock.patch.object(requests.Session, "request", side_effect=MockNodesActiveList().request)
    def test_match_data_volumes(self, mock):
        spec2module = self.module
        spec2module.params['flavor'] = 's2.large.4'
        spec2module.params['name'] = 'rbe-sdkunit-filter-node2'
        spec2module.params['data_volumes'][0]['size'] = '200'
        spec2module.params['data_volumes'].append({
            'size': '100',
            'type': 'SATA'
        })

        def _match(res):
            return _match_spec(res, **spec2module.params)

        nodes = list(filter(_match, self.user_cloud.cce2.cluster_nodes(self.cluster_id)) )
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].id, "65a9747f-a3e9-11e9-92b3-0255ac101711")

    @mock.patch.object(requests.Session, "request", side_effect=MockNodesActiveList().request)
    def test_no_match_data_volumes(self, mock):
        spec2module = self.module
        spec2module.params['flavor'] = 's2.large.4'
        spec2module.params['name'] = 'rbe-sdkunit-filter-node2'
        spec2module.params['data_volumes'][0]['size'] = '100'
        spec2module.params['data_volumes'].append({
            'size': '100',
            'type': 'SATA'
        })

        def _match(res):
            return _match_spec(res, **spec2module.params)

        nodes = list(filter(_match, self.user_cloud.cce2.cluster_nodes(self.cluster_id)) )
        self.assertFalse(nodes)

    @mock.patch.object(requests.Session, "request", side_effect=MockNodesActiveList().request)
    def test_too_few_data_volumes(self, mock):
        spec2module = self.module
        spec2module.params['flavor'] = 's2.large.4'
        spec2module.params['name'] = 'rbe-sdkunit-filter-node2'
        spec2module.params['data_volumes'][0]['size'] = '200'
        spec2module.params['data_volumes'].append({
            'size': '200',
            'type': 'SATA'
        })
        spec2module.params['data_volumes'].append({
            'size': '200',
            'type': 'SATA'
        })

        def _match(res):
            return _match_spec(res, **spec2module.params)

        nodes = list(filter(_match, self.user_cloud.cce2.cluster_nodes(self.cluster_id)) )
        self.assertFalse(nodes)

    @mock.patch.object(requests.Session, "request", side_effect=MockNodesActiveList().request)
    def test_same_double_data_volumes(self, mock):
        spec2module = self.module
        spec2module.params['flavor'] = 's2.large.4'
        spec2module.params['name'] = 'rbe-sdkunit-filter-node2'
        spec2module.params['data_volumes'][0]['size'] = '200'
        spec2module.params['data_volumes'].append({
            'size': '200',
            'type': 'SATA'
        })

        def _match(res):
            return _match_spec(res, **spec2module.params)

        nodes = list(filter(_match, self.user_cloud.cce2.cluster_nodes(self.cluster_id)) )
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].id, "65a9744f-a3e9-11e9-92b3-0255ac101711")

    @mock.patch.object(requests.Session, "request", side_effect=MockNodesActiveList().request)
    def test_delete_name(self, mock):
        spec2module = self.Module( { 'name': 'rbe-sdkunit-filter-node2' } )

        nodes = _filter_for_delete(self.user_cloud, self.cluster_id, **spec2module.params)
        self.assertEqual(len(nodes), 3)
        self.assertEqual(nodes[0].id, "65a9747f-a3e9-11e9-92b3-0255ac101711")
        self.assertEqual(nodes[1].id, "65a9744f-a3e9-11e9-92b3-0255ac101711")
        self.assertEqual(nodes[2].id, "65a73594-a3e9-11e9-92b3-0255ac101711")

        spec2module.params['availability_zone'] = "eu-de-02"
        nodes = _filter_for_delete(self.user_cloud, self.cluster_id, **spec2module.params)
        self.assertEqual(len(nodes), 0)

    @mock.patch.object(requests.Session, "request", side_effect=MockNodesActiveList().request)
    def test_delete_az(self, mock):
        spec2module = self.Module( { 'availability_zone': 'eu-de-02' } )

        nodes = _filter_for_delete(self.user_cloud, self.cluster_id, **spec2module.params)
        self.assertEqual(len(nodes), 2)
        self.assertEqual(nodes[0].id, "65a9728f-a3e9-11e9-92b3-0255ac101711")
        self.assertEqual(nodes[1].id, "65a73295-a3e9-11e9-92b3-0255ac101711")

        spec2module.params['flavor'] = "s2.large.1"
        nodes = _filter_for_delete(self.user_cloud, self.cluster_id, **spec2module.params)
        self.assertEqual(len(nodes), 2)
        self.assertEqual(nodes[0].id, "65a9728f-a3e9-11e9-92b3-0255ac101711")
        self.assertEqual(nodes[1].id, "65a73295-a3e9-11e9-92b3-0255ac101711")

        spec2module.params['flavor'] = "s2.large.4"
        nodes = _filter_for_delete(self.user_cloud, self.cluster_id, **spec2module.params)
        self.assertEqual(len(nodes), 0)

        spec2module.params.pop('flavor')
        spec2module.params['name'] = 'rbe-sdkunit-filter-node'
        nodes = _filter_for_delete(self.user_cloud, self.cluster_id, **spec2module.params)
        self.assertEqual(len(nodes), 2)
        self.assertEqual(nodes[0].id, "65a9728f-a3e9-11e9-92b3-0255ac101711")
        self.assertEqual(nodes[1].id, "65a73295-a3e9-11e9-92b3-0255ac101711")

        spec2module.params['name'] = 'rbe-sdkunit-filter-node2'
        nodes = _filter_for_delete(self.user_cloud, self.cluster_id, **spec2module.params)
        self.assertEqual(len(nodes), 0)
    
    @mock.patch.object(requests.Session, "request", side_effect=MockNodesActiveList().request)
    def test_delete_flavor(self, mock):
        spec2module = self.Module( { 'flavor': "s2.large.4" } )

        nodes = _filter_for_delete(self.user_cloud, self.cluster_id, **spec2module.params)
        self.assertEqual(len(nodes), 5)
        self.assertEqual(nodes[0].id,"65a87e5d-a3e9-11e9-92b3-0255ac101711")
        self.assertEqual(nodes[1].id,"65a9737f-a3e9-11e9-92b3-0255ac101711")
        self.assertEqual(nodes[2].id,"65a9747f-a3e9-11e9-92b3-0255ac101711")
        self.assertEqual(nodes[3].id,"65a9744f-a3e9-11e9-92b3-0255ac101711")
        self.assertEqual(nodes[4].id,"65a73594-a3e9-11e9-92b3-0255ac101711")

        spec2module.params['name'] = "rbe-sdkunit-filter-node-"
        nodes = _filter_for_delete(self.user_cloud, self.cluster_id, **spec2module.params)
        self.assertEqual(len(nodes), 2)
        self.assertEqual(nodes[0].id,"65a87e5d-a3e9-11e9-92b3-0255ac101711")
        self.assertEqual(nodes[1].id,"65a9737f-a3e9-11e9-92b3-0255ac101711")
