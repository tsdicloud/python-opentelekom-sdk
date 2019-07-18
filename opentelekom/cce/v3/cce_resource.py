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
# import six
from openstack import exceptions
from openstack import utils

from openstack import resource
from opentelekom import otc_resource

class MetadataSpec(resource.Resource):
    # Properties
    #: the name of the cluster
    name = resource.Body('name')
    #: the openstack id of the cluster (non-conforming place!)
    uid = resource.Body('uid')
    #: optional key/value pairs to label nodes
    labels = resource.Body('labels', type=dict)
    #: optional key/value pairs to 
    annotations = resource.Body('annotations', type=dict)
    #: status structure
    #==== get/fetch fields
    #: *Type:str
    created_at = resource.Body('creationTimeStamp')
    #: Update time
    #: *Type:str
    updated_at = resource.Body('updateTimeStamp')


class Cce2Resource(otc_resource.OtcResource):
    # Properties
    #: specification
    metadata = resource.Body('metadata', type=MetadataSpec)
    #: fixed value: kind=Cluster
    kind = resource.Body('kind')
    #: fixed value: apiVersion=v3
    api_version = resource.Body('apiVersion')

    def __init__(self, _synchronized=False, connection=None, **kwargs):
        '''Deviate setting of standard fields id, name, status to corresponding
           sub-structures, e.g. for_get_resouce, fetch, ...'''
        super().__init__(_synchronized, connection, **kwargs)

        if not self.metadata:
            self.metadata = MetadataSpec.new()
        if 'name' in kwargs:
            self.metadata.name = kwargs['name']
        elif 'id' in kwargs:
            self.metadata.uid = kwargs['id']

    def __setattr__(self, name, value):
        if name == 'name':
            if not self.metadata:
                self.metadata = MetadataSpec.new()
            self.metadata.name = value
        elif name == 'id':
            if not self.metadata:
                self.metadata = MetadataSpec.new()
            self.metadata.uid = value
        else:
            super().__setattr__(name, value)


    def __getattribute__(self, name):
        '''Intercept access to standard fields name, id, status
           due to inconforming modelling od CCE data structures'''
        if name == 'name':
            # retrieved values have prio
            if hasattr(self, 'metadata') and self.metadata:
                return self.metadata.name
        elif name == 'id':
            # retrieved values have prio
            if hasattr(self, 'metadata') and self.metadata and hasattr(self.metadata, 'uid'):
                return self.metadata.uid
        elif name == 'status':
            if hasattr(self, 'status_info') and self.status_info:
                return self.status_info.status
            else:
                return 'Unknown'
        else:
            return super().__getattribute__(name)
        return None

    @classmethod
    def list(cls, session, paginated=True, base_path=None, **params):
        """This method is a complete overwrite of the list function
        to work around the (terrible) inconsistency of returning null
        RESP BODY: {"kind":"Cluster","apiVersion":"v3","items":null}
        instead of an empty list in ccev2 API
        """
        if not cls.allow_list:
            raise exceptions.MethodNotSupported(cls, "list")
        session = cls._get_session(session)
        microversion = cls._get_microversion_for_list(session)

        if base_path is None:
            base_path = cls.base_path
        cls._query_mapping._validate(params, base_path=base_path)
        query_params = cls._query_mapping._transpose(params)
        uri = base_path % params

        limit = query_params.get('limit')

        # Track the total number of resources yielded so we can paginate
        # swift objects
        total_yielded = 0
        while uri:
            # Copy query_params due to weird mock unittest interactions
            response = session.get(
                uri,
                headers={"Accept": "application/json"},
                params=query_params.copy(),
                microversion=microversion)
            exceptions.raise_from_response(response)
            data = response.json()

            # Discard any existing pagination keys
            query_params.pop('marker', None)
            query_params.pop('limit', None)

            if cls.resources_key:
                resources = data[cls.resources_key]
            else:
                resources = data

            # CCE list result patch start
            if not resources:
                resources = []
            # CCE list result patch end

            if not isinstance(resources, list):
                resources = [resources]

            marker = None
            for raw_resource in resources:
                # Do not allow keys called "self" through. Glance chose
                # to name a key "self", so we need to pop it out because
                # we can't send it through cls.existing and into the
                # Resource initializer. "self" is already the first
                # argument and is practically a reserved word.
                raw_resource.pop("self", None)

                value = cls.existing(
                    microversion=microversion,
                    connection=session._get_connection(),
                    **raw_resource)
                marker = value.id
                yield value
                total_yielded += 1

            if resources and paginated:
                uri, next_params = cls._get_next_link(
                    uri, response, data, marker, limit, total_yielded)
                query_params.update(next_params)
            else:
                return
