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

from openstack import proxy

from openstack import exceptions

class OtcProxy(proxy.Proxy):

    def __init__(self, session, **kwargs):
        super().__init__(session, **kwargs)

        self.session.additional_headers = {
            'Accept': 'application/json', 
            'Content-Type': 'application/json',
            'X-Language': "en-us"
        }

    @staticmethod
    def _check_tag_support(resource):
        try:
            # Check 'tags' attribute exists
            resource.tags
        except AttributeError:
            raise exceptions.InvalidRequest(
                '%s resource does not support tag' %
                resource.__class__.__name__)

    def set_tags(self, resource, tags={}):
        """Replace tags of a specified resource with specified tags

        :param resource:
            :class:`~openstack.resource.Resource` instance.
        :param tags: New tags to be set.
        :type tags: "list"

        :returns: The updated resource
        :rtype: :class:`~openstack.resource.Resource`
        """
        self._check_tag_support(resource)
        return resource.set_tags(self, tags)

    def fetch_tags(self, resource):
        """Get tags of a specified resource

        :param resource:
            :class:`~openstack.resource.Resource` instance.

        :returns: The updated resource
        :rtype: list of tags
        """
        self._check_tag_support(resource)
        return resource.fetch_tags(self)

    def remove_all_tags(self, resource):
        """Removes all tags on the resource.

        :param resource:
            :class:`~openstack.resource.Resource` instance.
        """
        self._check_tag_support(resource)
        return resource.remove_all_tags(self)

    def check_tag(self, resource, key):
        """Checks if tag exists on the entity.

        If the tag does not exist a 404 will be returned

        :param session: The session to use for making this request.
        :param tag: The tag as a string.
        """
        self._check_tag_support(resource)
        return resource.check_tag(self, key)

    def add_tag(self, resource, key, value):
        """Adds a single tag to the resource.

        :param session: The session to use for making this request.
        :param tag: The tag as a string.
        """
        self._check_tag_support(resource)
        return resource.add_tag(self, key, value)

    def remove_tag(self, resource, key):
        """Removes a single tag from the specified server.

        :param session: The session to use for making this request.
        :param tag: The tag as a string.
        """
        self._check_tag_support(resource)
        return resource.remove_tag(self, key)