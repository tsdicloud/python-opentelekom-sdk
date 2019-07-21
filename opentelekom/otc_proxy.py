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
import copy

from openstack import _log
from openstack import proxy
from openstack import exceptions
from openstack import format
from openstack import utils

from openstack.resource import _normalize_status

def _pretty_ids(resources):
    text = ""
    for resource in resources:
        text += "{res}:{id},".format(
            res=resource.__class__.__name__, 
            id=resource.id)
    return text


def _pretty_states(resources, attribute):
    text = ""
    for resource in resources:
        text += "{res}:{id}={status},".format(
            res=resource.__class__.__name__, 
            id=resource.id, 
            status=getattr(resource, attribute))
    return text

class OtcProxy(proxy.Proxy):

    def __init__(self, session, **kwargs):
        '''Add some additional default http headers required by OpenTelekom services'''
        super().__init__(session, **kwargs)

        self.session.additional_headers = {
            'Accept': 'application/json', 
            'Content-Type': 'application/json',
            'X-Language': "en-us"
        }
    
    #==== bulk status support functions ====
    def wait_for_status_all(self, list_func, status, failures,
        interval=None, wait=None, attribute='status', **args):
        ''' Wait for all given ressources to reach a certain status 
        If the list of rsources is empty, the empty list is silently
        returned.
        The methods return the resources with their current status
        if all resources have either end status or failure status
        All other cases run into timeout.
        :param list_func: a function that is called tO refresh
            resource list 
        :param status: Desired status.
        :param failures: Statuses that would be interpreted as failures.
        :type failures: :py:class:`list`
        :param interval: Number of seconds to wait before to consecutive
                         checks. Default to 2.
        :param wait: Maximum number of seconds to wait before the change.
                     Default to 120.
        :returns: the list of resources in their final status
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if transition
                 to the desired status failed to occur in specified seconds.
        :raises: :class:`~openstack.exceptions.ResourceFailure` if the resource
                 has transited to one of the failure statuses.
        :raises: :class:`~AttributeError` if the resource does not have a
                ``status`` attribute.
        '''
        log = _log.setup_logging(__name__)

        if failures is None:
            failures = ['ERROR']
        failures = [f.lower() for f in failures]

        end_status = _normalize_status(status)

        observed = None
        orig_list = list(list_func())

        def _pending(res):
            res_status = _normalize_status(getattr(res, attribute))
            return (res_status != end_status) and (res_status not in failures)

        def _disappeared(res):
            res_status = _normalize_status(getattr(res, attribute)) 
            return (res_status == 'deleted')

        def _failed(res):
            res_status = _normalize_status(getattr(res, attribute)) 
            return (res_status in failures)

        for count in utils.iterate_timeout(
            timeout=wait,
            message="[{ids}] Timeout waiting to transition to {status}".format(
                ids=_pretty_ids(list(orig_list)), status=status),
            wait=interval):

            # use the early-read initial resource state list for the first iteration
            if observed is None:
                observed = orig_list
            else:
                observed = list(list_func())

            # check for interfering deletes from somewhere else with suddenly
            # disapearing resources
            try:
                if ( len(orig_list) == len(observed) ):   
                    next(filter(_disappeared, observed))
                    raise exceptions.ResourceFailure(
                        "Some resources unexpectedly disappeared during wait.")                
            except StopIteration:
                pass

            # get states
            # always check all resources in case of late errors and
            # externally triggered state changes
            pending = list(filter(_pending, observed))
            if pending:
                # test for non-empty pending set, and also log the
                # pending ones
                pending_states = _pretty_states(pending, attribute) 
                log.debug("[%s] still waiting for state %s.", 
                    pending_states, end_status)
            else:
                errors = list(filter(_failed, observed))
                if errors:
                    raise exceptions.ResourceFailure(
                            "[{name}] transitioned to failure states".format(
                            name=_pretty_states(errors, attribute)))
                else:
                    return observed

        return observed


    def wait_for_delete_all(self, list_func, interval, wait, attribute='status'):
        ''' Wait for all ressources given for getting deleted
        
        :param list_func: A function to update list of deleted nodes
        :type resource: :class:`~openstack.resource.Resource`
        :param interval: Number of seconds to wait between checks.
        :param wait: Maximum number of seconds to wait for the delete.
        :return: Method returns self on success.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` transition
             to status failed to occur in wait seconds.
        '''
        def _pending(res):
            return _normalize_status(getattr(res, attribute)) != 'deleted'

        orig_nodes = list(list_func())
        observed = None

        for count in utils.iterate_timeout(
            timeout=wait,
            message="[{ids}] Timeout waiting for delete".format(ids=_pretty_ids(list(orig_nodes))),
            wait=interval):

            if not observed:
                observed = filter(_pending, orig_nodes)
            else:
                orig_nodes = list(list_func())
                observed = filter(_pending, orig_nodes)

            # update observed list for all other iterations
            try:
                next(observed) # test for non-empty pending set
            except StopIteration:
                return orig_nodes

        return orig_nodes


    #==== key/value tag handling support ====
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