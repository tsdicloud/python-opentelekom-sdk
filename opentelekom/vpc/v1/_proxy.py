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

#from opentelekom.dms.v1 import message as _message
from opentelekom.vpc.v1 import vpc as _vpc
from opentelekom.vpc.v1 import subnet as _subnet
#from opentelekom.dms.v1.0 import subscription as _subscription
from opentelekom import otc_proxy
from openstack import resource


class Proxy(otc_proxy.OtcProxy):

    def create_vpc(self, **attrs):
        """Create a new vpc from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.message.v2.queue.Queue`,
                           comprised of the properties on the Queue class.

        :returns: The results of queue creation
        :rtype: :class:`~opentelekom.vpc.v1.Vpc`
         """
        return self._create(_vpc.Vpc, **attrs)

    def update_vpc(self, vpc, **attrs):
        """Update vpc attributes

        :param dict attrs: Keyword arguments which will be used to create
                           comprised of the properties on the Vpc class.

        :returns: The results of vpc update
        :rtype: :class:`~opentelekom.vpc.v1.Vpc`
        """
        return self._update(_vpc.Vpc, vpc, **attrs)

    def get_vpc(self, vpc):
        """Get a vpc

        :param queue: The value can be the name of a queue or a
            :class:`~opentelekom.vpc.v1.Vpc` instance.

        :rtype: :class:`~opentelekom.vpc.Vpc`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            queue matching the name could be found.
        """
        return self._get(_vpc.Vpc, vpc)

    def vpcs(self, **query):
        """Retrieve a ist of vpcs

        :param kwargs query: Optional query parameters to be sent to
            restrict the queues to be returned. Available parameters include:

            * limit: Requests at most the specified number of items be
                returned from the query.
            * marker: Specifies the ID of the last-seen queue. Use the limit
                parameter to make an initial limited request and use the ID of
                the last-seen queue from the response as the marker parameter
                value in a subsequent limited request.

        :returns: A generator of vpc instances.
        """
        return self._list(_vpc.Vpc, **query)

    def delete_vpc(self, vpc, ignore_missing=True):
        """Delete a vpc

        :param vpc: The value can be either the name of a vpc or a
                      :class:`~opentelekom.vpc.v1.Vpc` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the queue does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent queue.

        :returns: ``None``
        """
        return self._delete(_vpc.Vpc, vpc, ignore_missing=ignore_missing)

    def create_subnet(self, vpc, **attrs):
        """Create a new subnet for a vpc from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.message.v2.queue.Queue`,
                           comprised of the properties on the Queue class.

        :returns: The results of queue creation
        :rtype: :class:`~opentelekom.vpc.v1.subnet.Subnet`
         """
        parent_vpc = self._get_resource(_vpc.Vpc, vpc)
        return self._create(_subnet.Subnet, vpc_id=parent_vpc.id, **attrs)

    def update_subnet(self, subnet, **attrs):
        """Update subnet of a vpc with attributes, you annot change the vpc

        :param dict attrs: Keyword arguments which will be used to create
                           comprised of the properties on the Vpc class.

        :returns: The results of vpc update
        :rtype: :class:`~opentelekom.vpc.v1.Vpc`
        """
        sn = self._get_resource(_subnet.Subnet, subnet)
        if sn.vpc_id is None:
            sn = self.get_subnet(sn.id)
        # I need the full attribute spec, so the DELETE solution is not applicable here
        return self._update(_subnet.Subnet, sn.id, base_path='/vpcs/%(parent_vpc_id)s/subnets',
            prepend_key=False,
            parent_vpc_id=sn.vpc_id,
            **attrs)

    def get_subnet(self, subnet):
        """Get a subnet

        :param subnet: The value can be the id of a subnet or a
            :class:`~opentelekom.vpc.v1.subnet.Subnet` instance.

        :rtype: :class:`~opentelekom.vpc.Vpc`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            queue matching the name could be found.
        """
        return self._get(_subnet.Subnet, subnet)

    def subnets(self, **query):
        """Retrieve a ist of vpcs

        :param kwargs query: Optional query parameters to be sent to
            restrict the queues to be returned. Available parameters include:

            * limit: Requests at most the specified number of items be
                returned from the query.
            * marker: Specifies the ID of the last-seen queue. Use the limit
                parameter to make an initial limited request and use the ID of
                the last-seen queue from the response as the marker parameter
                value in a subsequent limited request.

        :returns: A generator of vpc instances.
        """
        return self._list(_subnet.Subnet, **query)

    def delete_subnet(self, subnet, ignore_missing=True):
        """Delete a subnet

        :param value: The value can be either the name of a vpc or a
                      :class:`~opentelekom.vpc.v1.Vpc` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the queue does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent queue.

        :returns: ``subnet'' for chained status
        """
        sn = self._get_resource(_subnet.Subnet, subnet)
        if sn.vpc_id is None:
            sn = self.get_subnet(sn.id)
        # for the (somehow deviating) delete case, we use a special resource object
        # which is deleted instead of the originating subnet resource
        # The reason is a resource path on vpc with both subnet and vpc id
        self._delete(_subnet.VpcSubnetAssoc, vpc_id=sn.vpc_id, id=sn.id)
        # we return the subnet, not the association helper, which is kept hidden
        # so, the return value can directly be used for status check
        return sn


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
