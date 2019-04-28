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

from opentelekom import otc_proxy
from opentelekom.rds.v3 import datastore as _datastore
from opentelekom.rds.v3 import flavor as _flavor
from opentelekom.rds.v3 import instance as _db

from openstack import resource

class Proxy(otc_proxy.OtcProxy):

    # TODO: OTC fix catalog and endpoint version (numerical 3 instead of 'v3' when gettting endpoint)
    # this is a temporary workaround only
    skip_discovery = True

    # ======== Datastores ========
    def datastores(self, **param):
        """Retrieve a generator of datastores

        :param dict query: Optional query parameters to be sent to limit the
            resources being returned.

            * `engine_name`: Name of the database engine, e.g. MySQL, PostgreSQL, SQLServer

        :returns: A generator of version object
        :rtype: :class:`~opentelekomsdk.rds.v3.datastore.Version
        """

        return self._list(_datastore.Version, **param )

    def flavors(self, **param):
        """Retrieve a generator of datastores

        :param dict query: Optional query parameters to be sent to limit the
            resources being returned.

            * `engine_name`: Name of the database engine, e.g. MySQL, PostgreSQL, SQLServer
            * `version_name`: Version of the 

        :returns: A generator of flavor object
        :rtype: :class:`~opentelekomsdk.rds.v3.datastore.Version
        """
        return self._list(_flavor.Flavor, **param )

    def create_db(self, **attrs):
        """Create a new DB from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~opentelekom.rds.v3.instance.DB`,
                           comprised of the properties on the DB class.

        :returns: The results of db creation
        :rtype: :class:`~opentelekom.rds.v3.instance.DB`
        """
        return self._create(_db.DB, **attrs)

    def update_db(self, db, **attrs):
        """Update db attributes

        :param dict attrs: Keyword arguments which will be used to create
                           comprised of the properties on the Vpc class.

        :returns: The results of db update
        :rtype: :class:`~opentelekom.rds.v3.instance.DB`
        """
        return self._update(_db.DB, db, **attrs)

    def get_db(self, db):
        """Get a db info

        :param queue: The value can be the name of a queue or a
            :class:`~opentelekom.rds.v3.instance.DB` instance.

        :rtype: :class:`~opentelekom.rds.v3.instance.DB`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            queue matching the name could be found.
        """
        return self._get(_db.DB, db)

    def dbs(self, **query):
        """Retrieve a list of db infos

        :param kwargs query: Optional query parameters to be sent to
            restrict the queues to be returned. Available parameters include:
            * limit: Requests at most the specified number of items be
                returned from the query.
            * offset: specify a pagin offset
        :returns: A generator of db instances.
        """
        return self._list(_db.DB, **query)

    def delete_db(self, db, ignore_missing=True):
        """Delete a db

        :param db: The value can be either the name of a vpc or a
                      :class:`~opentelekom.rds.v3.instance.DB` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the queue does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent queue.

        :returns: ``None``
        """
        return self._delete(_db.DB, db, ignore_missing=ignore_missing)


    def wait_for_status(self, res, status='ACTIVE', failures=None,
                        interval=15, wait=1000):
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

    def wait_for_delete(self, res, interval=15, wait=1000):
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
