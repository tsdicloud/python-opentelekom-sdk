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
import json as _json
import datetime
import requests

from requests.structures import CaseInsensitiveDict

from urllib.parse import urlparse
from unittest import mock


class OtcMockResponse(requests.Response):
    """ This is a simple data structure that describes a url calling pattern and a simple response e.g. srecorded
    from functional tests """

    default_headers = CaseInsensitiveDict( data={"Accept-Ranges": "bytes",
                       "Connection": "keep-alive",
                       "Content-Type": "application/json",
                       "Date": "Thu, 23 May 2019 15:11:11 GMT",
                       "Server": "Web Server",
                       "Strict-Transport-Security": "max-age=31536000; includeSubdomains;",
                       "Vary": "Accept-Charset, Accept-Encoding, Accept-Language, Accept",
                       "X-Content-Type-Options": "nosniff",
                       "X-Download-Options": "noopen",
                       "X-Frame-Options": "SAMEORIGIN",
                       "X-XSS-Protection": "1; mode=block;"
                       })

    def __init__(self, method, url_match, path, json=None, text=None, status_code=200, headers=None, **kwargs):
        """ A very sensitive implementation to imitate most of the 
        implicit behavior the openstacksdk session deends on """
        self.method = method
        self.url_match = url_match
        self.path = path
        self.headers = self.default_headers
        if headers:
            self.headers.update(headers)
        # timestamp representation of the form: Thu, 23 May 2019 15:11:11 GMT
        self.headers['Date'] = datetime.datetime.now().strftime("%a, %x %X %Z")

        if json:
            dump = _json.dumps(json)
            self._content = dump.encode()
            self.headers['Content-Length'] = len(dump)
        else:
            self._content = None

        self.status_code = status_code
        #self.text = text
        #self._content = None
        self.encoding = None
        self.reason = None
        self.num_called = 0

class OtcMockService:
    """ The baseclass for all mocked OTC responses.
    If authentication is needed, the baseclass mocks all the required keystone responses.
    Otherwise, it mocks the matching response for this test """

    @staticmethod
    def _matchURL(method, url, response):
        u = urlparse(url)
        if (response.method == method) and (response.url_match in u.netloc) and (response.path == u.path):
            return True
        else:
            return False

    @classmethod
    def request(cls, method, url, params=None, data=None, headers=None, **kwargs):
        matchURL = lambda x: cls._matchURL(method=method, url=url, response=x) 

        try:
            keystone_response = next(filter(matchURL, cls.keystone_responses))
            keystone_response.num_called += 1
            return keystone_response
        except StopIteration:
            pass
        
        try:
            response = next(filter(matchURL, cls.responses))
            response.num_called += 1
            return response
        except StopIteration:
            u = urlparse(url)
            raise AssertionError(method + " " + u.netloc + " " + u.path + " not mocked!")

    @classmethod
    def assertAuthCalled(cls):
        for resp in cls.keystone_responses:
            if resp.num_called<1:
                raise AssertionError('Keystone authentication NOT properly called!')

    @classmethod
    def assertServicesCalled(cls):
        missingCalls = ""
        for resp in cls.responses:
            if resp.num_called<1:
                missingCalls += resp.method + " " + resp.url_match + " " + resp.path + "\n"
        if len(missingCalls)>0:
            raise AssertionError('Not all expected endpoints called! Missing:\n' + missingCalls)

    responses = []
    keystone_responses = [
        # version call
        OtcMockResponse(method="GET",
                        url_match="iam",
                        path="/v3",
                        status_code=200,
                        json={"version": {"media-types": [{"type": "application/vnd.openstack.identity-v3+json", "base": "application/json"}], "links": [
                            {"rel": "self", "href": "https://iam.eu-de.otc.t-systems.com/v3/"}], "id": "v3.6", "updated": "2016-04-04T00:00:00Z", "status": "stable"}}
                        ),
        # token delivery + catalog
        OtcMockResponse(method="POST",
                        url_match="iam",
                        path="/v3/auth/tokens",
                        status_code=200,
                        headers={"X-Subject-Token": "dummy", },
                        json={"token": {"expires_at": "2219-05-24T15:11:11.815000Z", "methods": ["password"], "catalog":
                                        [{"endpoints": [{"region_id": "eu-de", "id": "af310f1928e94df081c70681f7bd0c99", "region": "eu-de", "interface": "public", "url": "https://vpc.eu-de.otc.t-systems.com"}], "name": "neutron", "id": "17d89ac272864e5db017ace42ec33514", "type": "network"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "2e6291b553f949aa96a5ac35ec42715c", "region": "eu-de", "interface": "public",
                                                         "url": "https://dis.eu-de.otc.t-systems.com"}], "name": "Data Ingestion Service", "id": "a98d684c000c429c8587ecb106ab9c81", "type": "dis"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "6f782d76e02c40a4acdfb80192919511", "region": "eu-de", "interface": "public",
                                                         "url": "https://evs.eu-de.otc.t-systems.com/v3/0391e4486e864c26be5654c522f440f2"}], "name": "cinderv3", "id": "01ddc5a9916c45c2b6f46dc604848cb7", "type": "volumev3"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "727ba225c9c64e888407370cbbd44501", "region": "eu-de", "interface": "public",
                                                         "url": "https://sdrs.eu-de.otc.t-systems.com/v1/0391e4486e864c26be5654c522f440f2"}], "name": "sdrs", "id": "e910f1ad6491403ea2ed913732b0e248", "type": "sdrs"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "1d6167579e084e40bd9f53b74e06adfe", "region": "eu-de", "interface": "public",
                                                         "url": "https://csbs.eu-de.otc.t-systems.com/v1/0391e4486e864c26be5654c522f440f2"}], "name": "karbor", "id": "7e0d2f600d55430fa0a26e17d0f242ee", "type": "data-protect"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "040ef992594245a7808e3d5092a15b63", "region": "eu-de", "interface": "public",
                                                         "url": "https://antiddos.eu-de.otc.t-systems.com/v1/"}], "name": "antiddos", "id": "8d3cfc79bd02415ca1456f4efb2d679e", "type": "Anti-DDoS"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "6e1fda48a2964b95af4cd0ba94f79c14", "region": "eu-de", "interface": "public",
                                                         "url": "https://dcs.eu-de.otc.t-systems.com/v1.0/0391e4486e864c26be5654c522f440f2"}], "name": "dcsv1", "id": "e50ef60d77d241b1831451efcc4b9c53", "type": "dcsv1"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "6901947715a94dd48e961443f937637c", "region": "eu-de", "interface": "public",
                                                         "url": "https://dcs.eu-de.otc.t-systems.com/v1.0/"}], "name": "Distributed Cache Service", "id": "b68904da4654407fa2fe80ebb1517ba1", "type": "dcs"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "c00eb9d4f7a343f3805b10cc00dcb93c", "region": "eu-de", "interface": "public",
                                                         "url": "https://ecs.eu-de.otc.t-systems.com/v1/0391e4486e864c26be5654c522f440f2"}], "name": "ecs", "id": "5e92eb2502a346888ef4701929731729", "type": "ecs"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "1360c0dc80654c5790c1b6d210f34746", "region": "eu-de", "interface": "public",
                                                         "url": "https://ims.eu-de.otc.t-systems.com"}], "name": "glance", "id": "90095f474f054b4ba6e029bc398ccb59", "type": "image"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "f450c790f79e45e9a8c884f1d8980476", "region": "eu-de", "interface": "public",
                                                         "url": "https://dws.eu-de.otc.t-systems.com/v1.0/0391e4486e864c26be5654c522f440f2"}], "name": "dwsv1", "id": "4d2c0faebed04ebfa2c27299025da75f", "type": "dwsv1"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "6fdfaa131aa34627a253aa98791c54ed", "region": "eu-de", "interface": "public",
                                                         "url": "https://nat.eu-de.otc.t-systems.com/v2.0"}], "name": "nat", "id": "26bd550cd8ab4b179465430a578e7f6f", "type": "nat"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "2d0ec9691e104c84961801451a9843c5", "region": "eu-de", "interface": "public",
                                                         "url": "https://cce.eu-de.otc.t-systems.com/api/v1"}], "name": "containerengine", "id": "0a07d1952689433094703fb067377789", "type": "cce"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "33e41106fd5f45b1b2c8385641056240", "region": "eu-de", "interface": "public",
                                                         "url": "https://dcaas.eu-de.otc.t-systems.com/v2.0"}], "name": "direct-connect", "id": "838fc84a2f17440fad58c8afe732829b", "type": "dcaas"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "e2ffee808abc4a60916715b1d4b489dd", "region": "eu-de", "interface": "public",
                                                         "url": "https://ecs.eu-de.otc.t-systems.com/v2/0391e4486e864c26be5654c522f440f2"}], "name": "nova", "id": "b7f2a5b1a019459cb956e43a8cb41e31", "type": "compute"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "52530888eab74e33bdc8fcd7c5f56283", "region": "eu-de", "interface": "public",
                                                         "url": "https://sfs.eu-de.otc.t-systems.com/v2/0391e4486e864c26be5654c522f440f2"}], "name": "manilav2", "id": "0d4d4f2bdff94e88872e13b95522330e", "type": "sharev2"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "fb048f20ebe24bcfadd1fdf3f3233bdb", "region": "eu-de", "interface": "public",
                                                         "url": "https://vbs.eu-de.otc.t-systems.com/v2/0391e4486e864c26be5654c522f440f2"}], "name": "vbsv2", "id": "7c9bb62294754bbab20075fa3013f6d4", "type": "vbsv2"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "8597fe8b1059433caf596b97b3eb314a", "region": "eu-de", "interface": "public",
                                                         "url": "https://deh.eu-de.otc.t-systems.com/v1.0/0391e4486e864c26be5654c522f440f2"}], "name": "deh", "id": "931b440ee0dc465daa213852b7f2560f", "type": "deh"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "1dc3f5d1e8724d33b89b63a11359a1f3", "region": "eu-de", "interface": "public",
                                                         "url": "https://cts.eu-de.otc.t-systems.com/v1.0/0391e4486e864c26be5654c522f440f2"}], "name": "cts", "id": "7a924763ac3d4c52975ff6ee1d57b81a", "type": "cts"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "c797ee4caeba48f7b69b8637263a4b74", "region": "eu-de", "interface": "public",
                                                         "url": "https://kms.eu-de.otc.t-systems.com/v1.0/"}], "name": "key-management", "id": "51b2c52dd9ec41febe6420d0938aaec5", "type": "kms"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "f4be859c14914a4ea9213f60114b221c", "region": "eu-de", "interface": "public",
                                                         "url": "https://iam.eu-de.otc.t-systems.com/v3"}], "name": "keystone", "id": "45a401041b6547f79b976e2d0727c52b", "type": "identity"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "aea68b97168e4a0e8b7021fa84bfb6f8", "region": "eu-de", "interface": "public",
                                                         "url": "https://vpc.eu-de.otc.t-systems.com/v2.0/0391e4486e864c26be5654c522f440f2"}], "name": "vpc2.0", "id": "508f451d620f49559b8d265e1d3414c6", "type": "vpc2.0"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "41ac39ca57fa4386bf4a4dc8fc8dd4cb", "region": "eu-de", "interface": "public",
                                                         "url": "https://ces.eu-de.otc.t-systems.com/V1.0/"}], "name": "cloudeye", "id": "7fd1b40b0aa041c08dee0020c5a2d50a", "type": "ces"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "8862699a760e4d7388c31c62b94db440", "region": "eu-de", "interface": "public",
                                                         "url": "https://antiddos.eu-de.otc.t-systems.com/v1/0391e4486e864c26be5654c522f440f2"}], "name": "anti-ddos", "id": "fd90d9531a914c9a9221dd19f5bd51b0", "type": "antiddos"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "f0f93869dc8c44bd86781b03d7ccb153", "region": "eu-de", "interface": "public",
                                                         "url": "https://elb.eu-de.otc.t-systems.com/v1.0/0391e4486e864c26be5654c522f440f2"}], "name": "elbv1", "id": "efcdc4928b0640c48b1e130a9f418c9c", "type": "elbv1"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "f4ffc9642d2042fcb60ee2859a76f4d9", "region": "eu-de", "interface": "public",
                                                         "url": "https://bms.eu-de.otc.t-systems.com/v1/0391e4486e864c26be5654c522f440f2"}], "name": "bms", "id": "66be4a54f91e4583b9d639d6d5d4d191", "type": "bms"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "4517ce20076646b89be76a48a2255d4e", "region": "eu-de", "interface": "public",
                                                         "url": "https://kms.eu-de.otc.t-systems.com/v1.0/0391e4486e864c26be5654c522f440f2"}], "name": "kmsv1", "id": "2c7f1c1a5a3f4267bfd301b593f3daae", "type": "kmsv1"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "f34477c6a93a48a88cba0f5cd80f210c", "region": "eu-de", "interface": "public",
                                                         "url": "https://maas.eu-de.otc.t-systems.com/v1/0391e4486e864c26be5654c522f440f2"}], "name": "maasv1", "id": "1d10b11e586a4418b2bf9f84f56cdd65", "type": "maasv1"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "78b8f6817db64ccc8073279fdecb89bd", "region": "eu-de", "interface": "public",
                                                         "url": "https://ces.eu-de.otc.t-systems.com/V1.0/0391e4486e864c26be5654c522f440f2"}], "name": "cesv1", "id": "d72f4d81d6e9474b821f34c33b66706a", "type": "cesv1"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "74337eb573344771aad9b5a5ef285c09", "region": "eu-de", "interface": "public",
                                                         "url": "https://vpc.eu-de.otc.t-systems.com/v1/0391e4486e864c26be5654c522f440f2"}], "name": "vpc", "id": "f177def1baa44ed19f34d25f5c77cd34", "type": "vpc"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "412828451e1946d7a2a79171fab4e8ef", "region": "eu-de", "interface": "public",
                                                         "url": "https://rds.eu-de.otc.t-systems.com/v3/0391e4486e864c26be5654c522f440f2"}], "name": "rdsv3", "id": "99918fccb53a465798ff2a8c1ce5fa67", "type": "rdsv3"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "ca7b1cb6878f4a26a0446b7d7ccd5506", "region": "eu-de", "interface": "public",
                                                         "url": "https://smn.eu-de.otc.t-systems.com/v2/"}], "name": "SimpleMessageNotification", "id": "33f5635b02324436848c3350bb05b3e6", "type": "smn"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "62ce7ad8991d412aaac2aa0489185d75", "region": "eu-de", "interface": "public",
                                                         "url": "https://mrs.eu-de.otc.t-systems.com/v1.1"}], "name": "mapreduce", "id": "9ef2f792a4aa4f038a1d2a07d552483a", "type": "mrs"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "c4abc2a5a09c453b91d1c63d2dd520a0", "region": "eu-de", "interface": "public",
                                                         "url": "https://sdrs.eu-de.otc.t-systems.com/v1/0391e4486e864c26be5654c522f440f2"}], "name": "sdrs", "id": "7c147b43972c4203820d928cd4258067", "type": "sdrs"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "fc7a3989f18c4cfaac74abd7d890fefe", "region": "eu-de", "interface": "public",
                                                         "url": "https://obs.eu-de.otc.t-systems.com"}], "name": "objectstorage", "id": "51277de7b1b34c7d8edad30bd81ab5f1", "type": "object"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "c271920659c0481da20d260350f5545b", "region": "eu-de", "interface": "public",
                                                         "url": "https://dms.eu-de.otc.t-systems.com/v1.0"}], "name": "distributedmessageservice", "id": "9978936bc0a14813ba57f85d8377ace1", "type": "dms"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "f54a19af702843fcbc8d6e23e214dd69", "region": "eu-de", "interface": "public",
                                                         "url": "https://rds.eu-de.otc.t-systems.com/v1.0"}], "name": "trove", "id": "0e535c30b96e49b19f9098cb9fd4b368", "type": "database"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "1c26054c2c434409a4d285fef5a729c5", "region": "eu-de", "interface": "public",
                                                         "url": "https://cce.eu-de.otc.t-systems.com"}], "name": "ccev2.0", "id": "0ee6a30469c947aebb19fe4b446c3644", "type": "ccev2.0"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "0047a06690484d86afe04877074efddf", "region": "eu-de", "interface": "public",
                                                         "url": "https://dns.eu-de.otc.t-systems.com"}], "name": "designate", "id": "56cd81db1f8445d98652479afe07c5ba", "type": "dns"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "2bbfa8fc6ea246eb8556d2e2525c46d8", "region": "eu-de", "interface": "public",
                                                         "url": "https://rts.eu-de.otc.t-systems.com/v1/0391e4486e864c26be5654c522f440f2"}], "name": "heat", "id": "233635b49a5b4ba48f6615f84ffc6694", "type": "orchestration"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "655849fb14d944b6b940824fc99a26de", "region": "eu-de", "interface": "public",
                                                         "url": "https://cts.eu-de.otc.t-systems.com/v2.0/0391e4486e864c26be5654c522f440f2"}], "name": "ctsv2", "id": "7444878c18d848a5a3cccd8f98f90b7c", "type": "ctsv2"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "91e6557513f646c69fe3eb1100b3cc7b", "region": "eu-de", "interface": "public",
                                                         "url": "https://waf.eu-de.otc.t-systems.com"}], "name": "waf", "id": "ecb81bb5d15d4abcba7e8aa3d87f6235", "type": "waf"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "2e5af55430da40ec89c748683f1bccb4", "region": "eu-de", "interface": "public",
                                                         "url": "https://mrs.eu-de.otc.t-systems.com/v1.1/0391e4486e864c26be5654c522f440f2"}], "name": "mrsv1", "id": "4c207327decb4dac95f15c47a3605f36", "type": "mrsv1"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "9d53edaf9e204bbea29c436e0c725933", "region": "eu-de", "interface": "public",
                                                         "url": "https://rds.eu-de.otc.t-systems.com/rds/v1/0391e4486e864c26be5654c522f440f2"}], "name": "rdsv1", "id": "53d86c9dd35245d9850cedd34f8c7edc", "type": "rdsv1"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "c097d8ea9064465296461205bdaf26d1", "region": "eu-de", "interface": "public",
                                                         "url": "https://evs.eu-de.otc.t-systems.com/v2/0391e4486e864c26be5654c522f440f2"}], "name": "cinderv2", "id": "0c69eafe914149d487fb7475ed0287c5", "type": "volumev2"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "ee2841360821491a9074f70c23aa3f62", "region": "eu-de", "interface": "public",
                                                         "url": "https://css.eu-de.otc.t-systems.com/v1.0/0391e4486e864c26be5654c522f440f2"}], "name": "css", "id": "85c04ec8ade54221b6c150620a70ddb9", "type": "css"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "73702f027c994bbabda6d18755efb3bd", "region": "eu-de", "interface": "public",
                                                         "url": "https://dis.eu-de.otc.t-systems.com/v2/0391e4486e864c26be5654c522f440f2"}], "name": "disv2", "id": "289b6a2d2d50435dac63a20954db554e", "type": "disv2"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "c2a8b2db595d4ff7b4637f6abb32a899", "region": "eu-de", "interface": "public",
                                                         "url": "https://as.eu-de.otc.t-systems.com/autoscaling-api/v1/0391e4486e864c26be5654c522f440f2"}], "name": "asv1", "id": "fe9a5486dd6843728fd1a6767f7e9967", "type": "asv1"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "22e073c62e6f412cac0297f22cb0eb6f", "region": "eu-de", "interface": "public",
                                                         "url": "https://evs.eu-de.otc.t-systems.com/v2/0391e4486e864c26be5654c522f440f2"}], "name": "evs", "id": "cb195887b01349d0b3e361db478f458e", "type": "evs"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "9624e5f4dd5f4309a18a8062702786c7", "region": "eu-de", "interface": "public",
                                                         "url": "https://vbs.eu-de.otc.t-systems.com/v2/"}], "name": "volume-backup", "id": "f48ebde6bb6a4e43b5ec914eae78e77b", "type": "vbs"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "cc2a08206ac8447e9517551142215bb1", "region": "eu-de", "interface": "public",
                                                         "url": "https://smn.eu-de.otc.t-systems.com/v2/0391e4486e864c26be5654c522f440f2"}], "name": "smnv2", "id": "d9856847bd2c4e50a878ab7c8e183b58", "type": "smnv2"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "fd24445c934b4687acb0d8a47b5e136c", "region": "eu-de", "interface": "public",
                                                         "url": "https://evs.eu-de.otc.t-systems.com/v2/0391e4486e864c26be5654c522f440f2"}], "name": "cinder", "id": "ac97a488327b43d19f50fd0afee67c33", "type": "volume"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "64d30135a5fa4054bd7c2eaafce1743c", "region": "eu-de", "interface": "public",
                                                         "url": "https://dms.eu-de.otc.t-systems.com/v1.0/0391e4486e864c26be5654c522f440f2"}], "name": "dmsv1", "id": "d0cab6a75f114541b6c635e251de4324", "type": "dmsv1"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "c78833f16e604b4f9779b1bd0a5270ce", "region": "eu-de", "interface": "public",
                                                         "url": "https://rds.eu-de.otc.t-systems.com/rds/v1"}], "name": "relationaldatabase", "id": "f5508175271042759f4f979bb274bd8b", "type": "rds"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "2d5ed0fb59b94846bd23ce26f9db8698", "region": "eu-de", "interface": "public",
                                                         "url": "https://maas.eu-de.otc.t-systems.com"}], "name": "maas", "id": "7f063c076bec425a83a8d0ab13a533ed", "type": "maas"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "bd5bdaf3afbb487db25cbff46d3ea3a4", "region": "eu-de", "interface": "public",
                                                         "url": "https://workspace.eu-de.otc.t-systems.com/v1.0/0391e4486e864c26be5654c522f440f2"}], "name": "workspace", "id": "9af8c1bfaa7b4973a733b233be509f6a", "type": "workspace"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "18187aeed8de4ce690f1140540097a9f", "region": "eu-de", "interface": "public",
                                                         "url": "https://dws.eu-de.otc.t-systems.com"}], "name": "datawarehouseservice", "id": "b5631c5444ae4d83a56175084333ad6f", "type": "dws"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "12083f0bf1f14c09937c9111508d738d", "region": "eu-de", "interface": "public",
                                                         "url": "https://as.eu-de.otc.t-systems.com/autoscaling-api/v1"}], "name": "autoscaling", "id": "4d06a55b120640eabe9d1b8a706cd9b6", "type": "as"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "68f70ac830fd4e4e9e83caea260f46ec", "region": "eu-de", "interface": "public",
                                                         "url": "https://tms.eu-de.otc.t-systems.com/v1.0"}], "name": "tag-management", "id": "a5149bea8d664191a0fe1c7eaa886706", "type": "tms"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "480c81f968e841b8bfac3d7a1c46a589", "region": "eu-de", "interface": "public",
                                                         "url": "https://swift.eu-de.otc.t-systems.com/v1/AUTH_0391e4486e864c26be5654c522f440f2"}], "name": "swift", "id": "b2a2507faf154effae7d8183afa493b3", "type": "object-store"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "a3134e8d73e9429599460b4195e64617", "region": "eu-de", "interface": "public",
                                                         "url": "https://elb.eu-de.otc.t-systems.com/v1.0"}], "name": "loadbalance", "id": "d06b35e9eea0408b83581bcd3e3f7f2b", "type": "elb"},
                                         {"endpoints": [{"region_id": "eu-de", "id": "c945c929a57c4dc3b49b6d9c238687ab", "region": "eu-de", "interface": "public",
                                                         "url": "https://workspace.eu-de.otc.t-systems.com/v1.0/0391e4486e864c26be5654c522f440f2"}], "name": "Workspace", "id": "272d59f7d1934e2f9b2d065149122fff", "type": "wks"},
                                         {"endpoints": [{"region_id": "*", "id": "2df96872ffd84d4a84c29967739ae3fd", "region": "*", "interface": "public", "url": "https://iam.eu-de.otc.t-systems.com/v3"}], "name": "keystone", "id": "45a401041b6547f79b976e2d0727c52b", "type": "identity"}], "roles": [{"name": "te_agency", "id": "41ce5857c94c4775b6cc53d5feeba445"}, {"name": "te_admin", "id": "699bd62cda304d2cad03fd2fb190b8cf"}, {"name": "op_gated_cce_switch", "id": "0"}], "project": {"domain": {"xdomain_type": "TSI", "name": "OTC00000000001000000317", "id": "f61828ffa6844c2caca6618cd6fdecb7", "xdomain_id": "00000000001000000317"}, "name": "eu-de_profi9", "id": "0391e4486e864c26be5654c522f440f2"}, "issued_at": "2019-05-23T15:11:11.815000Z", "user": {"domain": {"xdomain_type": "TSI", "name": "OTC00000000001000000317", "id": "f61828ffa6844c2caca6618cd6fdecb7", "xdomain_id": "00000000001000000317"}, "name": "brederle", "password_expires_at": "2219-06-05T12:42:20.000000", "id": "984366b9749e43d88660cc093d95b83b"}}}
                        )
    ]
