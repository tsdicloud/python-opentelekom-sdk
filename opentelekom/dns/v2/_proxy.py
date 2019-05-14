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
from opentelekom.dns.v2 import recordset as _rs
from opentelekom.dns.v2 import zone as _zone


class Proxy(proxy.Proxy):

    # ======== Zones ========
    def zones(self, **query):
        """Retrieve a generator of zones

        :param dict query: Optional query parameters to be sent to limit the
            resources being returned.

            * `name`: Zone Name field.
            * `type`: Zone Type field.
            * `email`: Zone email field.
            * `status`: Status of the zone.
            * `ttl`: TTL field filter.abs
            * `description`: Zone description field filter.

        :returns: A generator of zone
            :class:`~openstack.dns.v2.zone.Zone` instances.
        """
        #if not query.get('project_id'):
        #    query['project_id'] = self.get_project_id()
        return self._list(_zone.Zone, **query)

    def create_zone(self, **attrs):
        """Create a new zone from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.dns.v2.zone.Zone`,
            comprised of the properties on the Zone class.
        :returns: The results of zone creation.
        :rtype: :class:`~openstack.dns.v2.zone.Zone`
        """
        if not attrs.get('project_id'):
            attrs['project_id'] = self.get_project_id()
        return self._create(_zone.Zone, prepend_key=False, **attrs)

    def get_zone(self, zone, **attrs):
        """Get a zone

        :param zone: The value can be the ID of a zone
             or a :class:`~openstack.dns.v2.zone.Zone` instance.
        :returns: Zone instance.
        :rtype: :class:`~openstack.dns.v2.zone.Zone`
        """
        #if not attrs.get('project_id'):
        #    attrs['project_id'] = self.get_project_id()
        return self._get(_zone.Zone, zone, **attrs)

    def delete_zone(self, zone, ignore_missing=True, **attrs):
        """Delete a zone

        :param zone: The value can be the ID of a zone
             or a :class:`~openstack.dns.v2.zone.Zone` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the zone does not exist.
            When set to ``True``, no exception will be set when attempting to
            delete a nonexistent zone.

        :returns: Zone been deleted
        :rtype: :class:`~openstack.dns.v2.zone.Zone`
        """
        if not attrs.get('project_id'):
            attrs['project_id'] = self.get_project_id()
        return self._delete(_zone.Zone, zone, ignore_missing=ignore_missing, **attrs)

    def update_zone(self, zone, **attrs):
        """Update zone attributes

        :param zone: The id or an instance of
            :class:`~openstack.dns.v2.zone.Zone`.
        :param dict attrs: attributes for update on
            :class:`~openstack.dns.v2.zone.Zone`.

        :rtype: :class:`~openstack.dns.v2.zone.Zone`
        """
        if not attrs.get('project_id'):
            attrs['project_id'] = self.get_project_id()
        return self._update(_zone.Zone, zone, **attrs)

    def find_zone(self, name_or_id, type, ignore_missing=True, **attrs):
        """Find a single zone

        :param name_or_id: The name or ID of a zone
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the zone does not exist.
            When set to ``True``, no exception will be set when attempting
            to delete a nonexistent zone.

        :returns: :class:`~openstack.dns.v2.zone.Zone`
        """
        #if not attrs.get('project_id'):
        #    attrs['project_id'] = self.get_project_id()
        attrs.update({ 'type': type })    
        return self._find(_zone.Zone, name_or_id, ignore_missing, **attrs)

    def abandon_zone(self, zone, **attrs):
        """Abandon Zone

        :param zone: The value can be the ID of a zone to be abandoned
             or a :class:`~openstack.dns.v2.zone_export.ZoneExport` instance.

        :returns: None
        """
        zone = self._get_resource(_zone.Zone, zone)
        if not attrs.get('project_id'):
            attrs['project_id'] = self.get_project_id()
        return zone.abandon(self, **attrs)

    # ======== Recordsets ========
    def recordsets(self, zone=None, **query):
        """Retrieve a generator of recordsets

        :param zone: The optional value can be the ID of a zone
             or a :class:`~openstack.dns.v2.zone.Zone` instance. If it is not
             given all recordsets for all zones of the tenant would be
             retrieved
        :param dict query: Optional query parameters to be sent to limit the
            resources being returned.

            * `name`: Recordset Name field.
            * `type`: Type field.
            * `status`: Status of the recordset.
            * `ttl`: TTL field filter.
            * `description`: Recordset description field filter.

        :returns: A generator of zone
            (:class:`~openstack.dns.v2.recordset.Recordset`) instances
        """
        if zone:
            zone = self._get_resource(_zone.Zone, zone)
            query.update({'zone_id': zone.id})
        return self._list(_rs.Recordset, **query)

    def create_recordset(self, zone, **attrs):
        """Create a new recordset in the zone

        :param zone: The value can be the ID of a zone
            or a :class:`~openstack.dns.v2.zone.Zone` instance.
        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.dns.v2.recordset.Recordset`,
            comprised of the properties on the Recordset class.
        :returns: The results of zone creation
        :rtype: :class:`~openstack.dns.v2.recordset.Recordset`
        """
        zone = self._get_resource(_zone.Zone, zone)
        attrs.update({'zone_id': zone.id})
        if not attrs.get('project_id'):
            attrs['project_id'] = self.get_project_id()
        return self._create(_rs.Recordset, prepend_key=False, **attrs)

    def update_recordset(self, recordset, zone, **attrs):
        """Update Recordset attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.dns.v2.recordset.Recordset`,
            comprised of the properties on the Recordset class.
        :returns: The results of zone creation
        :rtype: :class:`~openstack.dns.v2.recordset.Recordset`
        """
        if not attrs.get('project_id'):
            attrs['project_id'] = self.get_project_id()
        zone = self._get_resource(_zone.Zone, zone)
        return self._update(_rs.Recordset, recordset, zone_id=zone.id, **attrs)

    def get_recordset(self, recordset, zone):
        """Get a recordset

        :param zone: The value can be the ID of a zone
             or a :class:`~openstack.dns.v2.zone.Zone` instance.
        :param recordset: The value can be the ID of a recordset
             or a :class:`~openstack.dns.v2.recordset.Recordset` instance.
        :returns: Recordset instance
        :rtype: :class:`~openstack.dns.v2.recordset.Recordset`
        """
        zone = self._get_resource(_zone.Zone, zone)
        return self._get(_rs.Recordset, recordset, zone_id=zone.id)

    def find_recordset(self, name_or_id, zone, ignore_missing=True, **attrs):
        """Get a recordset

        :param zone: The value can be the ID of a zone
             or a :class:`~openstack.dns.v2.zone.Zone` instance.
        :param recordset: The value can be the ID of a recordset
             or a :class:`~openstack.dns.v2.recordset.Recordset` instance.
        :returns: Recordset instance
        :rtype: :class:`~openstack.dns.v2.recordset.Recordset`
        """
        zone = self._get_resource(_zone.Zone, zone)
        return self._find(_rs.Recordset, name_or_id,
            zone_id=zone.id, ignore_missing=ignore_missing, **attrs)
    
    def delete_recordset(self, recordset, zone=None, ignore_missing=True, **attrs):
        """Delete a zone

        :param recordset: The value can be the ID of a recordset
             or a :class:`~openstack.dns.v2.recordset.Recordset`
             instance.
        :param zone: The value can be the ID of a zone
             or a :class:`~openstack.dns.v2.zone.Zone` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the zone does not exist. When set to ``True``, no exception will
            be set when attempting to delete a nonexistent zone.

        :returns: Recordset instance been deleted
        :rtype: :class:`~openstack.dns.v2.recordset.Recordset`
        """
        if zone:
            zone = self._get_resource(_zone.Zone, zone)
            recordset = self._get(
                _rs.Recordset, recordset, zone_id=zone.id)
        if not attrs.get('project_id'):
            attrs['project_id'] = self.get_project_id()
        return self._delete(_rs.Recordset, recordset,
                            ignore_missing=ignore_missing, **attrs)
