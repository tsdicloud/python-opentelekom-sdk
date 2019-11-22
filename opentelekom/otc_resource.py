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

import re

from openstack import resource
from openstack import exceptions
from openstack import utils

class OtcResource(resource.Resource):

    # ===== adaptions of standard methods for OTC
    def fetch(self, session, requires_id=True,
         base_path=None, error_message=None, **params):
         """ Open Telekom Cloud sometimes throws an Bad Request exception.although a
             NotFound is required to make find or fetch working 
         """
         try:
             return super().fetch(session=session, requires_id=requires_id,
                 base_path=base_path, error_message=error_message, **params)
         except exceptions.BadRequestException as bad:
             raise exceptions.ResourceNotFound(details=bad.details, http_status=404, request_id=bad.request_id)


    def _translate_response(self, response, has_body=None, error_message=None):
        """ Open Telekom has non-uniform formats for error details,
            so we try to adapt the different formats to get useful information out of exceptions """
        isError = False
        if has_body is None:
            has_body = self.has_body
        if has_body:
            content_type = response.headers.get('content-type', '')
            if response.content and 'application/json' in content_type:
                oerror = response.json()
                emsg = ""
                # Normalize to dict if error is described as a sub-structure
                if "error" in oerror:
                    isError = True
                    oerror = oerror['error']
                # first: extract some know code,value pairs
                if "code" in oerror:
                    isError = True
                    emsg += "[" + str(oerror['code']) + "]"
                    if "message" in oerror:
                        emsg += " " + oerror['message'] + "\n"
                    else:
                        emsg += "\n"
                if "error_code" in oerror:
                    isError = True
                    if "error_msg" in oerror:
                        emsg += " " + oerror['error_msg'] + "\n"
                    else:
                        emsg += "\n"
                if "errorCode" in oerror:
                    isError = True
                    emsg += "[" + oerror['errorCode'] + "]"
                    if "message" in oerror:
                        emsg += " " + oerror['message'] + "\n"
                    else:
                        emsg += "\n"
                # second: collect reasons in case of error to not loose information
                if isError:
                    for reason, msg in oerror.items():
                        if reason not in ['code', 'error_code', 'errorCode', 'message', 'error_msg']:
                            emsg += reason + "=" + msg + '\n'

        super()._translate_response(response, has_body=has_body, error_message=emsg if isError else None)

        #==== additional convenience functions here =====

#==== OpenTelekom Cloud usage of sub-resources to have cleaner APIs ====
class OtcSubResource(resource.Resource):
    """ This is an extension for Open Telekom Cloud so that sub-dicts could be defined with
        resource fields for better documentation and type control """

    def to_dict(self, body=True, headers=False, computed=True,
                ignore_none=True, **params):
        """ Just redefine behavior of to_dict to ignore Nones """
        import pdb; pdb.set_trace()
        super().to_dict(body=body, headers=headers, computed=computed,
                ignore_none=ignore_none, **params)


#==== OpenTelekom Cloud key/value extended tag handling ====
class TagMixin(object):

    #: A list of associated tags
    #: *Type: list of tag strings*
    tags = resource.Body('tags', type=dict, default={})

    _key_syntax = re.compile('^[0-9a-zA-Z_\-]{1,36}$')
    _value_syntax = re.compile('^[0-9a-zA-Z_\-]{0,43}$')

    def _checkOtcTagSyntax(self, key, value):
        if TagMixin._key_syntax.match(key) == None:
            raise exceptions.InvalidRequest(
                'Key %s should have 1..36 characters a-zA_Z0-9_-' % key)
        if TagMixin._value_syntax.match(value) == None:
            raise exceptions.InvalidRequest(
                'Value %s should have at most 43 characters a-zA_Z0-9_-' % value)
    
    def _fetch(self, session):
        url = utils.urljoin(self.base_path, self.id, 'tags')
        session = self._get_session(session)
        response = session.get(url)
        exceptions.raise_from_response(response)
        json = response.json()
        tags = {}
        if 'tags' in json:
            for t in json['tags']:
                tags[ t['key'] ] = t['value']
            self._body.attributes.update({'tags': tags })
        return response

    def fetch_tags(self, session):
        """Lists tags set on the entity.

        :param session: The session to use for making this request.
        :return: The list with tags attached to the entity
        """
        # NOTE(gtema): since this is a common method
        # we can't rely on the resource_key, because tags are returned
        # without resource_key. Do parse response here
        self._fetch(session)
        return self

    def check_tag(self, session, key):
        """Checks if tag exists on the entity.

        If the tag does not exist a 404 will be returned

        :param session: The session to use for making this request.
        :param tag: The tag as a string.
        """
        response = self._fetch(session)
        if key not in self.tags:
            exceptions.raise_from_response(response,
                error_message='Tag does not exist')
        return self

    def add_tag(self, session, key, value):
        """Adds a single key,value tag to the resource.

        :param session: The session to use for making this request.
        :param key: The tag key as a string.
        :param value: The tag value as a string.
        """
        self._checkOtcTagSyntax(key, value)
        url = utils.urljoin(self.base_path, self.id, 'tags')
        session = self._get_session(session)
        response = session.post(url=url, json={ "tag": { "key": key, "value": value }})
        exceptions.raise_from_response(response)
        # we do not want to update tags directly
        tags = self.tags
        tags[key] = value
        self._body.attributes.update({
            'tags': tags
        })
        return self

    def remove_tag(self, session, key):
        url = utils.urljoin(self.base_path, self.id, 'tags', key)
        session = self._get_session(session)
        response = session.delete(url=url)
        exceptions.raise_from_response(response)
        # we do not want to update tags directly
        tags = self.tags
        del tags[key]
        self._body.attributes.update({
            'tags': tags
        })
        return self

    def remove_all_tags(self, session):
        """Removes all tags on the entity.

        :param session: The session to use for making this request.
        """
        self.fetch_tags(session)
        keys = list(self.tags.keys())
        for key in keys:
            self.remove_tag(session, key)
        return self

    def set_tags(self, session, tags={}):
        """Sets/Replaces all tags on the resource.

        :param session: The session to use for making this request.
        :param list tags: List with tags to be set on the resource
        """
        if len(tags)>10:
            raise exceptions.InvalidRequest('Not more than 10 tags allowed!')
        for key,value in tags.items():        
            self._checkOtcTagSyntax(key,value)

        self.remove_all_tags(session)
        for key,value in dict(tags).items():        
            self.add_tag(session, key, value)            
        return self
