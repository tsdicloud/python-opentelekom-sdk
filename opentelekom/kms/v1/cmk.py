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
import datetime

from openstack import utils
from openstack import exceptions

from openstack import resource
from opentelekom import otc_resource

class CustomerMasterKey(otc_resource.OtcResource, otc_resource.TagMixin):
    resources_key = "key_details"
    resource_key = "key_info"
    base_path = None

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_list = True

    create_method = 'POST'

    # Properties
    #: key_alias: An alias name of the customer master key. It 
    #: must not exceed 255 bytes in length, according to the regex
    #: ^[a-zA-Z0-9:/_-]+{1,255}$
    name = resource.Body("key_alias")
    #: key_description: CMK description (optional)
    key_description = resource.Body("key_description")
    #: origin: where the key comes from. Values ["kms", "external"] (optional)
    origin = resource.Body("origin")
    #: sequence: an external, 36-byte serial number as additional reference
    sequence = resource.Body("sequence")
    #: pending_days: this property is only needed for schedules deletion
    pending_days = resource.Body("pending_days")
    #---- returned only by queries
    #: key_id: this strage service does not use id, but key_id as identifier
    #: this property is needed for some of the special service interactions
    key_id = resource.Body("key_id", alternate_id=True)
    #: key_state: state of key: "2"=enabled, "3"=disabled, "4"=scheduled for deletion
    key_state = resource.Body("key_state", type=int)
    #: key_type: cmk key type
    key_type = resource.Body("key_type", type=int)
    #: creation_date: time of key creation
    creation_date = resource.Body("creation_date")
    #: scheduled_deletion_date: time of planned deletion
    scheduled_deletion_date = resource.Body("scheduled_deletion_date")
    #: default_key_flag: "1" Indicates a default key
    default_key_flag = resource.Body("default_key", type=int)
    #: expiration_time: certificate expiration time
    expiration_time = resource.Body("expiration_time")
    #: origin: "kms"=generated in KMS, "external"=generated external
    origin = resource.Body("origin")

    def _otc_delete(self, session, base_path, microversion=None, **kwargs):
        preserve_resource_key = self.resource_key
        self.resource_key = None
        result = self._otc_action(session, base_path, microversion, **kwargs)
        self.resource_key = preserve_resource_key
        return result

    def _otc_action(self, session, base_path, microversion=None, **kwargs):
        body = kwargs
        session = self._get_session(session)
        microversion = self._get_microversion_for(session, 'create')

        # session = cls._get_session(session)
        # microversion = cls._get_microversion_for_list(session)
        #cls._query_mapping._validate(params, base_path=base_path)
        #query_params = cls._query_mapping._transpose(params)
        #uri = base_path % params
        resp = session.post(url=base_path, json=body,
            microversion=microversion)
        self._translate_response(resp)
        return self

    def fetch(self, session, requires_id=True,
              base_path=None, error_message=None, **params):
        """Get a remote resource based on this instance.
           This is a special implementation for the strange way
           key management is implemented in Open Telekom with POST calls

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param boolean requires_id: A boolean indicating whether resource ID
                                    should be part of the requested URI.
        :param str base_path: Base part of the URI for fetching resources, if
                              different from
                              :data:`~openstack.resource.Resource.base_path`.
        :param str error_message: An Error message to be returned if
                                  requested object does not exist.
        :param dict params: Additional parameters that can be consumed.
        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_fetch` is not set to ``True``.
        :raises: :exc:`~openstack.exceptions.ResourceNotFound` if
                 the resource was not found.
        """
        if not self.allow_fetch:
            raise exceptions.MethodNotSupported(self, "fetch")
        try:
            if base_path is None:
                base_path = "/kms/describe-key"
            body = params
            body['key_id'] = self.id
            session = self._get_session(session)
            microversion = self._get_microversion_for(session, 'fetch')
            response = session.post(url=base_path, microversion=microversion, json=body)
            kwargs = {}
            if error_message:
                kwargs['error_message'] = error_message

            self.microversion = microversion
            self._translate_response(response, **kwargs)
            return self
        except exceptions.BadRequestException as bad:
            raise exceptions.ResourceNotFound(details=bad.details, http_status=404, request_id=bad.request_id)


    @classmethod
    def list(cls, session, paginated=False, base_path='/kms/list-keys', microversion=None, **kwargs):
        """Special key listing with query POST parameters:
            * key_state
            * sequence
            * limit
            * marker"""
        if not cls.allow_list:
            raise exceptions.MethodNotSupported(cls, "list")

        # FIXIT: pagination not suppoprted yet
        #body = {}
        body = kwargs
        session = cls._get_session(session)
        microversion = cls._get_microversion_for_list(session)

        if base_path is None:
            base_path = cls.base_path
        #cls._query_mapping._validate(params, base_path=base_path)
        #query_params = cls._query_mapping._transpose(params)
        #uri = base_path % params
        resp = session.post(url=base_path, json=body,
            microversion=microversion)
        resp = resp.json()
        resp = resp[cls.resources_key]

        for raw_resource in resp:
            value = cls.existing(
                microversion=microversion,
                connection=session._get_connection(),
                **raw_resource)
            yield value

    def enable(self, session, **kwargs):
        return self._otc_action(session, base_path='/kms/enable-key', **kwargs)

    def disable(self, session, **kwargs):
        return self._otc_action(session, base_path='/kms/disable-key', **kwargs)

    def schedule_delete(self, session, **kwargs):
        return self._otc_delete(session, base_path='/kms/schedule-key-deletion', **kwargs)

    def cancel_delete(self, session, **kwargs):
        return self._otc_delete(session, '/kms/cancel-key-deletion', **kwargs)
    
    def create(self, session, prepend_key=True, base_path=None, **kwargs):
        return super().create(session=session, prepend_key=False, 
            base_path='/kms/create-key', **kwargs)


