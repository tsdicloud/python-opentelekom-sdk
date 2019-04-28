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

from opentelekom.css.v1 import cluster as _elastic
from opentelekom.css.v1 import flavor as _flavor
from opentelekom import otc_proxy
from openstack import resource


class Proxy(otc_proxy.OtcProxy):

    def flavors(self, **query):
        """Retrieve a list of search service versions and flavors

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
        return self._list(_flavor.Flavor, **query)
    
    def create_css(self, **attrs):
        """Create a new cloud search service from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.message.v2.queue.Queue`,
                           comprised of the properties on the Queue class.

        :returns: The results of cluster creation
        :rtype: :class:`~opentelekom.vpc.v1.Vpc`
         """
        return self._create(_elastic.Cluster, **attrs)

    def update_css(self, cluster, **attrs):
        """Update vpc attributes

        :param dict attrs: Keyword arguments which will be used to create
                           comprised of the properties on the Vpc class.

        :returns: The results of vpc update
        :rtype: :class:`~opentelekom.vpc.v1.Vpc`
        """
        return self._update(_elastic.Cluster, cluster, **attrs)

    def get_css(self, cluster):
        """Get a vpc

        :param queue: The value can be the name of a queue or a
            :class:`~opentelekom.vpc.v1.Vpc` instance.

        :rtype: :class:`~opentelekom.vpc.Vpc`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            queue matching the name could be found.
        """
        return self._get(_elastic.Cluster, cluster)

    def clusters(self, **query):
        """Retrieve a ist of vpcs

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
        return self._list(_elastic.Cluster, **query)

    def delete_css(self, cluster, ignore_missing=True):
        """Delete a css cluster

        :param vpc: The value can be either the name of a vpc or a
                      :class:`~opentelekom.vpc.v1.Vpc` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the queue does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent queue.

        :returns: ``None``
        """
        return self._delete(_elastic.Cluster, cluster, ignore_missing=ignore_missing)

    def wait_for_status(self, res, status='ACTIVE', failures=None,
                        interval=2, wait=120):
        """Wait for a resource to be in a particular status.

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

    def wait_for_delete(self, res, interval=2, wait=120):
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
