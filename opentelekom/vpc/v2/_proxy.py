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

from opentelekom.vpc.v2 import peering as _peering

from opentelekom import otc_proxy
from openstack import resource


class Proxy(otc_proxy.OtcProxy):

    def create_peering(self, **attrs):
        """Create a new vpc from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:~opentelekom.vpc.v2.peering.Peering`,
                           comprised of the properties on the Peering class.

        :returns: The results of queue creation
        :rtype: :class:`~opentelekom.vpc.v2.peering.Peering`
         """
        return self._create(_peering.Peering, **attrs)

    def update_peering(self, peering, **attrs):
        """Update peering attributes (only name)

        :param dict attrs: Keyword arguments which will be used to update
                           comprised of the properties on the Peering class.

        :returns: The results of peering update
        :rtype: :class:`~opentelekom.vpc.v2.peering.Peering`
        """
        return self._update(_peering.Peering, peering, **attrs)

    def get_peering(self, peering):
        """Get a vpc

        :param queue: The value can be the name of a queue or a
            :class:`~opentelekom.vpc.v1.Vpc` instance.

        :rtype: :class:``~opentelekom.vpc.v2.peering.Peering`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            queue matching the name could be found.
        """
        return self._get(_peering.Peering, peering)

    def accept_peering(self, peering):
        """Accept a peering from a vpc of a foreign tenant

        :param peering: The value can be the id or a
            :class:`~opentelekom.vpc.v1.Vpc` instance.

        :rtype: :class:``~opentelekom.vpc.v2.peering.Peering`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            queue matching the name could be found.
        """
        peering_res = self._get_resource(_peering.Peering, peering)
        return peering_res.accept(self)

    def reject_peering(self, peering):
        """Reject a peering from a vpc of a foreign tenant


        :param peering: The value can be the id or a
            :class:`~opentelekom.vpc.v2.peering.Peering` instance.

        :rtype: :class:``~opentelekom.vpc.v2.peering.Peering`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            queue matching the name could be found.
        """
        peering_res = self._get_resource(_peering.Peering, peering)
        return peering_res.reject(self)



    def find_peering(self, name_or_id, ignore_missing=True, **args):
        """Find IP availability of a network

        :param name_or_id: The name or ID of a peering
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :param dict args: Any additional parameters to be passed into
                          underlying methods. such as query filters.
        :returns: One :class:`~opentelekom.vpc.v2.peering.Peering` or None
        """
        return self._find(_peering.Peering, name_or_id, ignore_missing=ignore_missing, **args)


    def peerings(self, **query):
        """Retrieve a ist of vpcs

        :param kwargs query: Optional query parameters to be sent to
            restrict the queues to be returned. Available parameters include:

            * limit: Requests at most the specified number of items be
                returned from the query.
            * marker: Specifies the ID of the last-seen queue. Use the limit
                parameter to make an initial limited request and use the ID of
                the last-seen queue from the response as the marker parameter
                value in a subsequent limited request.

        :returns: A generator of peering instances.
        """
        return self._list(_peering.Peering, **query)

    def delete_peering(self, peering, ignore_missing=True):
        """Delete a vpc

        :param vpc: The value can be either the name of a vpc or a
                      :class:`~opentelekom.vpc.v2.peering.Peering` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the queue does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent queue.

        :returns: ``None``
        """
        return self._delete(_peering.Peering, peering, ignore_missing=ignore_missing)


    def create_route(self, **attrs):
        """Create a new vpc from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:~opentelekom.vpc.v2.peering.PeeringRoute`,
                           comprised of the properties on the PeeringRoute class.

        :returns: The results of queue creation
        :rtype: :class:`~opentelekom.vpc.v2.peering.PeeringRoute`
         """
        return self._create(_peering.PeeringRoute, **attrs)

    def get_route(self, route):
        """Get a vpc

        :param queue: The value can be the name of a queue or a
            :class:`~opentelekom.vpc.v1.Vpc` instance.

        :rtype: :class:``~opentelekom.vpc.v2.route.PeeringRoute`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            queue matching the name could be found.
        """
        return self._get(_peering.PeeringRoute, route)

    def find_route(self, name_or_id, ignore_missing=True, **args):
        """Find vpc peer route

        :param name_or_id: The name or ID of a route
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :param dict args: Any additional parameters to be passed into
                          underlying methods. such as query filters.
        :returns: One :class:`~opentelekom.vpc.v2.route.PeeringRoute` or None
        """
        return self._find(_peering.PeeringRoute, name_or_id, ignore_missing=ignore_missing, **args)


    def routes(self, **query):
        """Retrieve a list of peer routes

        :param kwargs query: Optional query parameters to be sent to
            restrict the queues to be returned. Available parameters include:

            * limit: Requests at most the specified number of items be
                returned from the query.
            * marker: Specifies the ID of the last-seen queue. Use the limit
                parameter to make an initial limited request and use the ID of
                the last-seen queue from the response as the marker parameter
                value in a subsequent limited request.

        :returns: A generator of route instances.
        """
        return self._list(_peering.PeeringRoute, **query)

    def delete_route(self, route, ignore_missing=True):
        """Delete a vpc

        :param vpc: The value can be either the name of a vpc or a
                      :class:`~opentelekom.vpc.v2.peering.PeeringRoute` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the queue does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent queue.

        :returns: ``None``
        """
        return self._delete(_peering.PeeringRoute, route, ignore_missing=ignore_missing)



    def wait_for_status(self, res, status='ACTIVE', failures=None,
                        interval=2, wait=120):
        """Wait for a resource to be in a particular status.
           This is especiall useful to wait for accepts/rejects from peerings
           e.g. set status='REJECTED', failures=['ERROR', "EXPIRED", "ACTIVE"]
           to wait for an active rejection or
           status='ACTIVE', failures=['ERROR', "REJECTED", "EXPIRED"]
           for successful pairings

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
