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

        
    # @classmethod
    # def new(cls, **kwargs):
    #     '''Handle setting of id value for _get_resource (e.g. for proxy._get)'''
    #     resource = super().new(**kwargs)
    #     if not resource.metadata:
    #         resource.metadata = MetadataSpec.new(**kwargs)
    #     if 'id' in kwargs:
    #         resource.metadata.uid = kwargs['id']
    #     return resource