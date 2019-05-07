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

import uuid
import json

from openstack import resource, exceptions
from opentelekom import otc_resource


class ConsumerGroup(otc_resource.OtcResource, otc_resource.TagMixin):
    resources_key = "groups"
    resource_key = "groups"
    base_path = "/queues/%(queue_id)s/groups"

    _query_mapping = resource.QueryParameters("include_deadletter", 
        "include_messages_num",
        **resource.TagMixin._tag_query_parameters
    )
    # FIXME: Get does only have one query parameter
    #_query_mapping = resource.QueryParameters("include_deadletter")

     # capabilities
    allow_create = True
    allow_list = True
    allow_fetch = True
    allow_delete = True

    create_method = 'POST'

    # Properties
    # special resource modelling for groups
    #: association of the consumption group to a queue
    queue = resource.URI("queue_id")
    #: group name, 32 charaacters a-zA-Z0-9_-
    name = resource.Body("name")
    #--- get/fetch
    #: number of available messages
    queue_mode = resource.Body("available_messages",type=int)
    #: number of dead letter messages of group
    produced_deadletters = resource.Body("produced_deadletters")
    #: number of available deadletters not consumed by group
    available_deadletters = resource.Body("available_deadletters")

    # some overrides for the strange modelling with lists in create and delete
    def create(self, session, prepend_key=True, base_path=None, **kwargs):
        """ This has to be reimplemented due to the strage list for creation """

        session = self._get_session(session)
        microversion = self._get_microversion_for(session, 'create')
        request = self._prepare_request(requires_id=False,
                                        prepend_key=prepend_key,
                                        base_path=base_path)
        # adapt request to the strange, non-consistent list structure
        request.body['groups'] = [ request.body['groups'] ]
        response = session.post(request.url,
                                json=request.body, headers=request.headers,
                                microversion=microversion)
        self.microversion = microversion
        # we have to remove also the list in the response
        body = response.json()
        body = body['groups'][0] 
        body = self._consume_body_attrs(body)
        self._body.attributes.update(body)
        self._body.clean()

        self._translate_response(response, has_body=False)

        return self

    def fetch(self, session, requires_id=True,
              base_path=None, error_message=None, **params):
        # Consumer groupss has no dedicated GET Method, so we have to use the list query with id
        groups = list(ConsumerGroup.list(session, base_path=base_path, 
           queue_id=self._uri.attributes['queue_id']))
        result = list(filter(lambda x: x['id'] == self.id, groups))
        if result:
            return result[0]
        else:
            raise exceptions.ResourceNotFound(details="Consumer group not found.", http_status=404)
