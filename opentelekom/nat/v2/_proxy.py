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

from opentelekom.nat.v2 import gateway as _gw
from opentelekom.nat.v2 import snat as _snat
from opentelekom import otc_proxy
from openstack import resource


class Proxy(otc_proxy.OtcProxy):

    def create_nat(self, **attrs):
        """Create a new natting gateway from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~opentelekom.nat.v2.gateway.Service`,
                           comprised of the properties on the Gateway class.

        :returns: The results of gateway creation
        :rtype: :class:`~opentelekom.nat.v2.gateway.Service`
         """
        return self._create(_gw.Service, tenant_id=self.get_project_id(), **attrs)

    def update_nat(self, natgw, **attrs):
        """Update nat gateway attributes 

        :param dict attrs: Keyword arguments which will be used to create
                           comprised of the properties on the Service class.

        :returns: The results of nat gateway update
        :rtype: :class:`~opentelekom.nat.v2.gateway.Service`
        """
        return self._update(_gw.Service, natgw, **attrs)

    def get_nat(self, natgw):
        """Get nat gateway information (only for the given project)

        :param queue: The value can be the id of a gateway or a
            :class:`~opentelekom.nat.v2.gateway.Service` instance.

        :rtype: :class:`~opentelekom.nat.v2.gateway.Service`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            queue matching the name could be found.
        """
        return self._get(_gw.Service, natgw)

    def gateways(self, **query):
        """Retrieve a ist of nat gateways (only for the given project)

        :param kwargs query: Optional query parameters to be sent to
            restrict the queues to be returned. Available parameters include:

            * limit: Requests at most the specified number of items be
                returned from the query.
            * marker: Specifies the ID of the last-seen queue. Use the limit
                parameter to make an initial limited request and use the ID of
                the last-seen queue from the response as the marker parameter
                value in a subsequent limited request.

        :returns: A generator of nat gw instances.
        """
        return self._list(_gw.Service, tenant_id=self.get_project_id(), **query)

    def delete_nat(self, natgw, ignore_missing=True):
        """Delete a nat gateway

        :param natgw: The value can be either the id of a gateway or a
                      :class:`~opentelekom.nat.v2.gateway.Service` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the queue does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent queue.

        :returns: ``None``
        """
        self._delete(_gw.Service, natgw, ignore_missing=ignore_missing)

    def create_snat_rule(self, **attrs):
        """Create a snat rule for natting gateway from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~opentelekom.nat.v2.snat.Rule`,
                           comprised of the properties on the SNAT rule class.

        :returns: The results of rule creation
        :rtype: :class:`~opentelekom.nat.v2.snat.Rule`
         """
        return self._create(_snat.Rule, **attrs)

    def get_snat_rule(self, snatrule):
        """Get snat rule information

        :param queue: The value can be the id of a rule or a
            :class:`~opentelekom.nat.v2.snat.Rule` instance.

        :rtype: :class:`~opentelekom.nat.v2.snat.Rule`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            queue matching the name could be found.
        """
        return self._get(_snat.Rule, snatrule)

    def snat_gw_rules(self, natgw, **query):
        """Retrieve a list of snat rules of a dedicated gateway

        :param natgw: The value can be either the id of a gateway or a
                      :class:`~opentelekom.nat.v2.gateway.Service` instance.
        :param kwargs query: Optional query parameters to be sent to
            restrict the queues to be returned. Available parameters include:
 
            * limit: Requests at most the specified number of items be
                returned from the query.
            * marker: Specifies the ID of the last-seen queue. Use the limit
                parameter to make an initial limited request and use the ID of
                the last-seen queue from the response as the marker parameter
                value in a subsequent limited request.

        :returns: A generator of nat gw instances.
        """
        parent_natgw = self._get_resource(_gw.Service, natgw)
        return self._list(_snat.Rule, nat_gateway_id=parent_natgw.id ,**query)

    def delete_snat_rule(self, rule, ignore_missing=True):
        """Delete a snat rule

        :param rule: The value can be either the rule id or a
                      :class:`~opentelekom.nat.v2.snat.Rule` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the queue does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent queue.

        :returns: ``None``
        """
        self._delete(_snat.Rule, rule, ignore_missing=ignore_missing)


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
