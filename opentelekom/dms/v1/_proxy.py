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
from opentelekom.dms.v1 import queue as _queue
from opentelekom.dms.v1 import group as _group

#from opentelekom.dms.v1.0 import subscription as _subscription
from opentelekom import otc_proxy
from openstack import resource


class Proxy(otc_proxy.OtcProxy):

    def create_queue(self, **attrs):
        """Create a new queue from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.message.v2.queue.Queue`,
                           comprised of the properties on the Queue class.

        :returns: The results of queue creation
        :rtype: :class:`~openstack.message.v2.queue.Queue`
        """
        return self._create(_queue.Queue, **attrs)

    def get_queue(self, queue):
        """Get a queue

        :param queue: The value can be the name of a queue or a
            :class:`~openstack.message.v2.queue.Queue` instance.

        :returns: One :class:`~openstack.message.v2.queue.Queue`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            queue matching the name could be found.
        """
        return self._get(_queue.Queue, queue)

    def find_queue(self, name_or_id, ignore_missing=True, **args):
        """Find a queue instance by name or id

        :param name_or_id: The name or ID of a css cluster
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :param dict args: Any additional parameters to be passed into
                          underlying methods. such as query filters.
        :returns: One :class:`~opentelekom.css.v1.cluster.Cluster` or None
        """
        return self._find(_queue.Queue, name_or_id, ignore_missing=ignore_missing, **args)

    def queues(self, **query):
        """Retrieve a generator of queues

        :param kwargs query: Optional query parameters to be sent to
            restrict the queues to be returned. Available parameters include:

            * limit: Requests at most the specified number of items be
                returned from the query.
            * marker: Specifies the ID of the last-seen queue. Use the limit
                parameter to make an initial limited request and use the ID of
                the last-seen queue from the response as the marker parameter
                value in a subsequent limited request.

        :returns: A generator of queue instances.
        """
        return self._list(_queue.Queue, **query)

    def delete_queue(self, value, ignore_missing=True):
        """Delete a queue

        :param value: The value can be either the name of a queue or a
                      :class:`~openstack.message.v2.queue.Queue` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the queue does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent queue.

        :returns: ``None``
        """
        self._delete(_queue.Queue, value, ignore_missing=ignore_missing)

    def create_queue_group(self, queue, **attrs):
        """Create a new queue from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.message.v2.queue.Queue`,
                           comprised of the properties on the Queue class.
        :returns: The results of queue creation
        :rtype: :class:`~openstack.message.v2.queue.Queue`
        """
        q  = self._get_resource(_queue.Queue, queue)
        return self._create(_group.ConsumerGroup, queue_id=q.id, **attrs)

    def get_queue_group(self, queue, group):
        """Get a queue

        :param queue: The value can be the name of a queue or a
            :class:`~openstack.message.v2.queue.Queue` instance.

        :returns: One :class:`~openstack.message.v2.queue.Queue`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            queue matching the name could be found.
        """
        q  = self._get_resource(_queue.Queue, queue)
        return self._get(_group.ConsumerGroup, group, queue_id=q.id)

    def find_queue_group(self, queue, name_or_id, ignore_missing=True, **args):
        """Find a rds instance by name or id

        :param name_or_id: The name or ID of a css cluster
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :param dict args: Any additional parameters to be passed into
                          underlying methods. such as query filters.
        :returns: One :class:`~opentelekom.css.v1.cluster.Cluster` or None
        """
        q  = self._get_resource(_queue.Queue, queue)
        return self._find(_group.ConsumerGroup, name_or_id, ignore_missing=ignore_missing, queue_id=q.id, **args)

    def queue_groups(self, queue, **query):
        """Retrieve a generator of queues

        :param kwargs query: Optional query parameters to be sent to
            restrict the queues to be returned. Available parameters include:

            * limit: Requests at most the specified number of items be
                returned from the query.
            * marker: Specifies the ID of the last-seen queue. Use the limit
                parameter to make an initial limited request and use the ID of
                the last-seen queue from the response as the marker parameter
                value in a subsequent limited request.

        :returns: A generator of queue instances.
        """
        q  = self._get_resource(_queue.Queue, queue)
        return self._list(_group.ConsumerGroup, queue_id=q.id, **query)

    def delete_queue_group(self, queue, group, ignore_missing=True):
        """Delete a queue consumer group

        :param value: The value can be either the name of a queue or a
                      :class:`~openstack.message.v2.queue.Queue` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the queue does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent queue.

        :returns: ``None``
        """
        q  = self._get_resource(_queue.Queue, queue)
        self._delete(_group.ConsumerGroup, group, ignore_missing=ignore_missing, queue_id=q.id)
