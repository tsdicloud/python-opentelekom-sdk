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

#from opentelekom.csbs.v1 import backup as _backup
from opentelekom.csbs.v1 import policy as _backup_policy
from opentelekom import otc_proxy
from openstack import resource


class Proxy(otc_proxy.OtcProxy):

    def create_policy(self, **attrs):
        """Create a new backup policy from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~opentelekom.csbs.v1.policy.Policy`,
                           comprised of the properties on the csbs policy class.

        :returns: The results of cluster creation
        :rtype: :class:`~opentelekom.csbs.v1.policy.Policy`
         """
        return self._create(_backup_policy.Policy, **attrs)

    def update_policy(self, policy, **attrs):
        """Update csbs policy attributes

        :param dict attrs: Keyword arguments which will be used to create
                          comprised of the properties on the csbs policy class.

        :returns: The results of vpc update
        :rtype: :class:`~opentelekom.csbs.v1.policy.Policy`
        """
        return self._update(_backup_policy.Policy, policy, **attrs)


    def get_policy(self, policy):
        """Get a csbs policy

        :param policy: The value can be the name of a queue or a
            :class:`~pentelekom.csbs.v1.policy.Policy` instance.

        :rtype: :class:`~opentelekom.csbs.v1.policy.Policy`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            queue matching the name could be found.
        """
        return self._get(_backup_policy.Policy, policy)

    def find_policy(self, name_or_id, ignore_missing=True, **args):
        """Find a csbs policy by name or id

        :param name_or_id: The name or ID of a csbs policy
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :param dict args: Any additional parameters to be passed into
                          underlying methods. such as query filters.
        :returns: One :class:`~opentelekom.css.v1.cluster.Cluster` or None
        """
        return self._find(_backup_policy.Policy, name_or_id, ignore_missing=ignore_missing, **args)


    def policies(self, **query):
        """Retrieve a list of csbs policies

        :param kwargs query: Optional query parameters to be sent to
            restrict the queues to be returned. Available parameters include:

            * limit: Requests at most the specified number of items be
                returned from the query.
            * marker: Specifies the ID of the last-seen queue. Use the limit
                parameter to make an initial limited request and use the ID of
                the last-seen queue from the response as the marker parameter
                value in a subsequent limited request.

        :returns: A generator of css cluster instances.
        """
        return self._list(_backup_policy.Policy, **query)

    def delete_policy(self, policy, ignore_missing=True):
        """Delete a csbs policy

        :parampolicy: The value can be either the id of a csbs policy or a
                      :class:`~pentelekom.csbs.v1.policy.Policy` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the queue does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent queue.

        :returns: ``None``
        """
        return self._delete(_backup_policy.Policy, policy, ignore_missing=ignore_missing)

    def wait_for_status(self, res, status='200', failures=None,
                        interval=15, wait=1500):
        """Wait for a resource to be in a particular status.

        FIXME: 200 is not a proper Openstack status. Should be something like FAIL, ACTIVE  ect

        :param res: The resource to wait on to reach the specified status.
                    The resource must have a ``status`` attribute.
        :type resource: A :class:`~openstack.resource.Resource` object.
        :param status: Desired status.
        :param failures: Statuses that would be interpreted as failures.
        :type failures: :py:class:`list`
        :param interval: Number of seconds to wait before to consecutive
                         checks. Default to 2.
        :param wait: Maximum number of seconds to wait before the change.
                     Default to 120.
        :returns: The resource is returned on success.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if transition
                 to the desired status failed to occur in specified seconds.
        :raises: :class:`~openstack.exceptions.ResourceFailure` if the resource
                 has transited to one of the failure statuses.
        :raises: :class:`~AttributeError` if the resource does not have a
                ``status`` attribute.
        """
        failures = ['Error'] if failures is None else failures
        return resource.wait_for_status(
            self, res, status, failures, interval, wait)

    def wait_for_delete(self, res, interval=15, wait=1200):
        """Wait for a resource to be deleted.

        :param res: The resource to wait on to be deleted.
        :type resource: A :class:`~openstack.resource.Resource` object.
        :param interval: Number of seconds to wait before to consecutive
                         checks. Default to 2.
        :param wait: Maximum number of seconds to wait before the change.
                     Default to 120.
        :returns: The resource is returned on success.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if transition
                 to delete failed to occur in the specified seconds.
        """
        return resource.wait_for_delete(self, res, interval, wait)
